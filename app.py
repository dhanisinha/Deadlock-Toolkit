from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS


# Import existing logic
from simulator import SystemState, build_state_from_input
from bankers import is_safe_state
from detection import run_detection_algorithm
from recovery import terminate_processes
from sample_cases import SAMPLE_CASES

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend interaction

# Global state for the simulation session
current_state = None

def state_to_dict(state: SystemState):
    if not state:
        return None
    return {
        "process_count": state.process_count,
        "resource_count": state.resource_count,
        "allocation": state.allocation,
        "max_matrix": state.max_matrix,
        "need": state.need,
        "available": state.available,
        "request_matrix": state.request_matrix,
        "priorities": state.priorities,
        "strategy": state.strategy.value if hasattr(state.strategy, 'value') else state.strategy
    }

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/samples', methods=['GET'])
def get_samples():
    return jsonify(list(SAMPLE_CASES.keys()))

@app.route('/api/state', methods=['GET', 'POST'])
def handle_state():
    global current_state
    if request.method == 'POST':
        data = request.json
        if 'sample' in data:
            # Load from sample
            sample_data = SAMPLE_CASES[data['sample']]
            current_state = build_state_from_input(
                process_count=sample_data["process_count"],
                resource_count=sample_data["resource_count"],
                allocation=[row[:] for row in sample_data["allocation"]],
                max_matrix=[row[:] for row in sample_data["max_matrix"]],
                available=sample_data["available"][:],
                priorities=sample_data["priorities"][:]
            )
        else:
            # Manual input
            current_state = build_state_from_input(
                process_count=data["process_count"],
                resource_count=data["resource_count"],
                allocation=data["allocation"],
                max_matrix=data["max_matrix"],
                available=data["available"],
                priorities=data.get("priorities", [])
            )
        return jsonify({"status": "success", "state": state_to_dict(current_state)})
    
    return jsonify(state_to_dict(current_state))

@app.route('/api/bankers', methods=['GET'])
def run_bankers():
    if not current_state:
        return jsonify({"error": "No state loaded"}), 400
    safe, sequence = is_safe_state(
        current_state.allocation,
        current_state.max_matrix,
        current_state.available
    )
    return jsonify({
        "safe": safe,
        "sequence": sequence if safe else None,
        "message": "System is SAFE" if safe else "System is UNSAFE"
    })

@app.route('/api/detect', methods=['GET'])
def run_detect():
    if not current_state:
        return jsonify({"error": "No state loaded"}), 400
        
    request_to_use = current_state.request_matrix
    if all(all(val == 0 for val in row) for row in request_to_use):
        request_to_use = current_state.need
        
    exists, deadlocked = run_detection_algorithm(
        current_state.allocation,
        request_to_use,
        current_state.available
    )
    return jsonify({
        "deadlock": exists,
        "processes": deadlocked,
        "message": f"Deadlock detected in processes: {deadlocked}" if exists else "No deadlock detected"
    })

@app.route('/api/recover', methods=['POST'])
def run_recover():
    global current_state
    if not current_state:
        return jsonify({"error": "No state loaded"}), 400
    
    data = request.json
    mode = data.get('mode', 'priority') # 'priority', 'least_resource', or 'preemption'
    
    # First detect using need if request matrix is zero
    request_to_use = current_state.request_matrix
    if all(all(val == 0 for val in row) for row in request_to_use):
        request_to_use = current_state.need
        
    exists, deadlocked = run_detection_algorithm(
        current_state.allocation,
        request_to_use,
        current_state.available
    )
    
    if not exists:
        return jsonify({"message": "No deadlock to recover from"})

    if mode in ['priority', 'least_resource']:
        steps, new_alloc, new_avail, terminated = terminate_processes(
            deadlocked,
            current_state.allocation,
            current_state.available,
            current_state.priorities,
            mode=mode
        )
        current_state.allocation = new_alloc
        current_state.available = new_avail
        for p_idx in terminated:
            current_state.request_matrix[p_idx] = [0 for _ in range(current_state.resource_count)]
        return jsonify({"status": "success", "steps": steps, "state": state_to_dict(current_state)})
    
    return jsonify({"error": "Invalid mode"}), 400

@app.route('/api/graph', methods=['GET'])
def get_graph():
    if not current_state:
        return jsonify({"error": "No state loaded"}), 400
    
    # Build data for Vis.js
    nodes = []
    edges = []
    
    request_to_use = current_state.request_matrix
    if all(all(val == 0 for val in row) for row in request_to_use):
        request_to_use = current_state.need
    
    # Processes
    for i in range(current_state.process_count):
        nodes.append({"id": f"P{i}", "label": f"Process P{i}", "group": "process"})
    
    # Resources
    for j in range(current_state.resource_count):
        nodes.append({"id": f"R{j}", "label": f"Resource R{j}", "group": "resource"})
        
    # Allocation Edges: Resource -> Process
    for i in range(current_state.process_count):
        for j in range(current_state.resource_count):
            if current_state.allocation[i][j] > 0:
                edges.append({
                    "from": f"R{j}", 
                    "to": f"P{i}", 
                    "label": str(current_state.allocation[i][j]),
                    "arrows": "to",
                    "color": {"color": "#10b981"}
                })
            if request_to_use[i][j] > 0:
                edges.append({
                    "from": f"P{i}", 
                    "to": f"R{j}", 
                    "label": str(request_to_use[i][j]),
                    "arrows": "to",
                    "color": {"color": "#ef4444"}
                })
                
    return jsonify({"nodes": nodes, "edges": edges})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
