# Deadlock Prevention, Detection, and Recovery Toolkit

A beginner-friendly Python toolkit that simulates OS-style process/resource competition and demonstrates:

- Deadlock avoidance (Banker's Algorithm)
- Deadlock detection (Work/Finish vectors)
- Deadlock prevention strategies
- Deadlock recovery techniques
- Resource Allocation Graph (cycle visibility)
- Real-time request simulation loop

## Project Structure

- `main.py` - Menu-driven CLI entry point
- `simulator.py` - Core system state + real-time execution engine
- `bankers.py` - Need matrix + safe-state + request safety checks
- `detection.py` - Deadlock detection using Work/Finish
- `prevention.py` - Hold-and-wait, ordering, and preemption prevention logic
- `recovery.py` - Termination and preemption recovery strategies
- `graph.py` - Resource Allocation Graph + cycle detection + visualization
- `sample_cases.py` - Predefined safe and deadlock-style scenarios
- `requirements.txt` - External dependencies for graphing

## Setup

1. Create or activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## CLI Features

From the menu you can:

1. Input custom system state
2. Select prevention strategy
3. Run real-time request simulation
4. Check safe state (Banker's Algorithm)
5. Detect deadlock
6. Visualize Resource Allocation Graph
7. Trigger recovery

## Input Format Notes

- Allocation matrix: one row per process, values separated by spaces
- Max matrix: same shape as Allocation
- Available vector: one value per resource type
- Request vector during simulation: one value per resource type

## Included Sample Test Cases

- `safe_case`: Common Banker's Algorithm example with safe sequence
- `deadlock_case`: Tight-resource scenario useful for detection/recovery practice

## Recovery Modes

- Process termination:
  - Priority mode (higher numeric value = lower importance)
  - Least resource usage mode
- Resource preemption:
  - Preempt selected resource units from deadlocked processes

## Educational Notes

- The toolkit favors clarity and readability over low-level OS complexity.
- Prevention and recovery policies are intentionally explicit to make behavior easy to observe.
- Real OS schedulers/resource managers have additional constraints not modeled here.
