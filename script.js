const API = '/api';
let currentState = null;
let network = null;

const delay = ms => new Promise(res => setTimeout(res, ms));

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    fetchSamples();
    fetchState();
});

function fetchSamples() {
    fetch(`${API}/samples`)
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById('sample-select');
            select.innerHTML = data.map(s => `<option value="${s}">${s}</option>`).join('');
        })
        .catch(err => log('ERR', 'Failed to fetch samples.'));
}

function fetchState() {
    fetch(`${API}/state`)
        .then(res => res.json())
        .then(data => {
            if (data) {
                currentState = data;
                renderState();
                updateGraph();
            }
        });
}

function loadSample() {
    const sample = document.getElementById('sample-select').value;
    if (!sample) return;
    
    fetch(`${API}/state`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sample })
    })
    .then(res => res.json())
    .then(data => {
        currentState = data.state;
        renderState();
        updateGraph();
        log('SYS', `📂 Loaded sample: <b>${sample}</b>. Matrices and Graph are updated and ready to be analysed.`);
    });
}

function renderState() {
    if (!currentState) return;

    // Render Allocation Matrix
    const allocContainer = document.getElementById('allocation-view');
    let html = '<h3>Allocation Matrix</h3><table>';
    html += '<thead><tr><th>Process</th>' + currentState.allocation[0].map((_, i) => `<th>R${i}</th>`).join('') + '</tr></thead>';
    html += '<tbody>' + currentState.allocation.map((row, i) => 
        `<tr><td><strong>P${i}</strong></td>${row.map(v => `<td>${v}</td>`).join('')}</tr>`
    ).join('') + '</tbody></table>';

    // Available vector
    html += `<div class="alert alert-info">Available Instances: [ ${currentState.available.join(', ')} ]</div>`;
    allocContainer.innerHTML = html;

    // Render Need Matrix
    const needContainer = document.getElementById('need-view');
    let needHtml = '<table><thead><tr><th>Process</th>' + currentState.need[0].map((_, i) => `<th>R${i}</th>`).join('') + '</tr></thead>';
    needHtml += '<tbody>' + currentState.need.map((row, i) => 
        `<tr><td><strong>P${i}</strong></td>${row.map(v => `<td>${v}</td>`).join('')}</tr>`
    ).join('') + '</tbody></table>';
    needContainer.innerHTML = needHtml;
}

function updateGraph() {
    fetch(`${API}/graph`)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('graph-container');
            const visData = {
                nodes: new vis.DataSet(data.nodes),
                edges: new vis.DataSet(data.edges)
            };
            const options = {
                nodes: {
                    font: { color: '#ffffff', size: 16, bold: true },
                    borderWidth: 2,
                    size: 25
                },
                edges: {
                    font: { align: 'top', color: '#ffffff', size: 14, strokeWidth: 0 },
                    arrows: { to: { enabled: true, scaleFactor: 1.0 } },
                    smooth: { type: 'dynamic' },
                    width: 2
                },
                physics: {
                    solver: 'repulsion',
                    repulsion: { nodeDistance: 150, springLength: 150 },
                    stabilization: { iterations: 50 }
                },
                groups: {
                    process: { 
                        shape: 'circle',
                        color: { background: '#2563eb', border: '#60a5fa' }
                    },
                    resource: { 
                        shape: 'square',
                        color: { background: '#059669', border: '#34d399' }
                    }
                },
                interaction: { hover: true }
            };
            // Small delay to ensure flexbox has settled
            setTimeout(() => {
                network = new vis.Network(container, visData, options);
                
                // Ensure it fits the container
                network.once('stabilizationIterationsDone', function() {
                    network.fit();
                });
            }, 100);
        })
        .catch(err => {
            console.error('Vis error:', err);
            log('ERR', 'Failed to update graph. Check console.');
        });
}

// Global UI Helpers
function updateHealthUI(isDeadlocked, isUnsafe = false) {
    const pulse = document.getElementById('health-pulse');
    const text = document.getElementById('health-text');
    
    if (isDeadlocked) {
        pulse.className = 'pulse danger';
        text.innerText = 'CRITICAL: Deadlock Detected';
        text.style.color = 'var(--danger)';
    } else if (isUnsafe) {
        pulse.className = 'pulse danger';
        text.innerText = 'WARNING: Unsafe State';
        text.style.color = 'var(--danger)';
    } else if (isUnsafe === 'processing') {
        pulse.className = 'pulse processing';
        text.innerText = 'AI: Thinking...';
        text.style.color = 'var(--primary)';
    } else {
        pulse.className = 'pulse';
        text.innerText = 'Stable & Optimized';
        text.style.color = 'var(--text-muted)';
    }
}

async function runBankers() {
    log('SYS', '🔍 <b>Starting Banker\'s Safe-State Probing...</b>');
    updateHealthUI(false, 'processing');
    const data = await fetch(`${API}/bankers`).then(res => res.json());
    
    const safetyIndicator = document.getElementById('safety-indicator');
    
    if (data.safe) {
        safetyIndicator.className = 'alert alert-success';
        safetyIndicator.innerHTML = `Checking safe sequence...`;
        
        // Cinematic Slow-Motion Step-by-Step
        for (let i = 0; i < data.sequence.length; i++) {
            const pId = data.sequence[i];
            await delay(1200);
            log('SUCCESS', `🔄 <b>Step ${i+1}:</b> Checking Process <b>P${pId}</b>. Resources are available. P${pId} executes and releases dependencies...`);
            // Briefly highlight node if it exists
            if (network) {
                network.selectNodes([`P${pId}`]);
                setTimeout(() => network.unselectNodes(), 800);
            }
        }
        
        await delay(800);
        safetyIndicator.innerHTML = `System is SAFE. Seq: ${data.sequence.join(' -> ')}`;
        log('SUCCESS', `🎉 <b>Final Result: System is SAFE!</b><br>The complete safe execution path is: <b>[ P${data.sequence.join(' → P')} ]</b>. No deadlock can occur if this order is followed.`);
        updateHealthUI(false, false);
    } else {
        safetyIndicator.className = 'alert alert-danger';
        safetyIndicator.innerHTML = 'System is UNSAFE.';
        log('ALRT', `🚨 <b>Bankers check Failed! System is UNSAFE.</b><br>There is no safe way to satisfy all processes. The system might enter a deadlock state soon!`);
        updateHealthUI(false, true);
    }
}

async function runDetection() {
    const data = await fetch(`${API}/detect`).then(res => res.json());
    
    if (data.deadlock) {
        log('ALRT', `🚨 <b>Wait... DEADLOCK CAUGHT!</b><br>Processes <b>[ ${data.processes.map(p => `P${p}`).join(', ')} ]</b> are stuck in a Circular Wait. They are pointing at each other and blocking the entire system!`);
        updateHealthUI(true);
    } else {
        log('SUCCESS', `✅ <b>No deadlocks found!</b><br>Everyone is getting what they need, the system state is healthy.`);
        updateHealthUI(false);
    }
}

async function runRecovery() {
    log('SYS', 'Attempting Automatic Recovery...');
    const data = await fetch(`${API}/recover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'priority' })
    }).then(res => res.json());
    
    if (data.status === 'success') {
        data.steps.forEach(step => log('RCVR', `⚡ <b>Recovery Action:</b> ${step}`));
        currentState = data.state;
        renderState();
        updateGraph();
        log('SUCCESS', '🎉 Recovery complete! The cycle is broken and resources have been taken back.');
        updateHealthUI(false);
    } else {
        log('ALRT', data.message || 'System is not in a deadlock.');
    }
}

function log(type, msg) {
    const output = document.getElementById('log-output');
    
    const typeClass = {
        'SYS': 'sys-msg',
        'SUCCESS': 'success-msg',
        'ALRT': 'alert-msg',
        'RCVR': 'rec-msg',
        'ERR': 'alert-msg'
    }[type] || 'sys-msg';

    const newMsg = document.createElement('div');
    newMsg.className = `story-msg ${typeClass}`;
    newMsg.innerHTML = msg;
    
    // Add to the top of the chat
    output.prepend(newMsg);
}

// Layout handlers
function loadTab(tab) {
    document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
    event.currentTarget.classList.add('active');
}

let isMaximized = false;
function toggleMaximizeGraph() {
    const card = document.getElementById('graph-card');
    const btnIcon = document.querySelector('#max-btn i');
    
    isMaximized = !isMaximized;
    if (isMaximized) {
        card.classList.add('maximized');
        btnIcon.setAttribute('data-lucide', 'minimize');
    } else {
        card.classList.remove('maximized');
        btnIcon.setAttribute('data-lucide', 'maximize');
    }
    
    // Refresh the icon so Lucide redraws it correctly
    lucide.createIcons();
    
    // Allow CSS transition to settle then tell Vis.js to center and refit the graph
    if (network) {
        setTimeout(() => network.fit({ animation: true }), 310);
    }
}

function downloadReport() {
    const logs = document.querySelectorAll('.story-msg');
    if (logs.length === 0) {
        alert("No logs to export yet! Try running some simulations first.");
        return;
    }

    let reportText = "DEADLOCK SIMULATOR - SESSION REPORT\n";
    reportText += "Generated on: " + new Date().toLocaleString() + "\n";
    reportText += "==========================================\n\n";

    // Logs are prepended, so for a report, we reverse them to show chronological order
    const logArray = Array.from(logs).reverse();
    logArray.forEach((el, index) => {
        const timestamp = new Date().toLocaleTimeString();
        // Strip HTML tags for clean text report
        const cleanText = el.innerText.replace(/\n/g, " ");
        reportText += `[${timestamp}] ${cleanText}\n`;
    });

    reportText += "\n==========================================\n";
    reportText += "End of Simulation Report.";

    const blob = new Blob([reportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Deadlock_Simulation_Report_${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    log('SYS', '📝 <b>Report Exported:</b> Session summary has been downloaded to your computer.');
}
