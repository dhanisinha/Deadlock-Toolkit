# Deadlock Prevention, Detection and Recovery Toolkit

This is a Python-based project I built to understand how deadlocks work in operating systems and how they can be handled using different techniques.

The idea was to simulate processes and resources in a simple way so that concepts like Banker’s Algorithm, detection, and recovery become easier to see and experiment with.

---

## What this project does

* Checks safe and unsafe states using Banker’s Algorithm
* Detects deadlocks using the Work and Finish method
* Demonstrates different prevention techniques
* Simulates recovery using process termination and resource preemption
* Shows Resource Allocation Graph and detects cycles
* Allows real-time request simulation through a CLI

---

## Project files

```
main.py           - Menu-driven program to run everything
simulator.py      - Handles system state and simulation
bankers.py        - Banker’s Algorithm logic
detection.py      - Deadlock detection logic
prevention.py     - Prevention techniques
recovery.py       - Recovery strategies
graph.py          - Resource Allocation Graph and cycle detection
sample_cases.py   - Example test cases
requirements.txt  - Required libraries
```

---

## How to run

1. Clone the repository
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the project:

```
python main.py
```

---

## Features in the CLI

From the menu you can:

* Enter your own system state
* Run simulation step-by-step
* Check if the system is in a safe state
* Detect deadlock
* Visualize the resource allocation graph
* Apply recovery techniques

---

## Input format (simple idea)

* Allocation → resources currently assigned
* Max → maximum demand of each process
* Available → free resources
* Request → new request during simulation

---

## Sample cases

* safe_case → shows a safe sequence
* deadlock_case → useful for testing detection and recovery

---

## Notes

This project is mainly for learning purposes.
It focuses on clarity rather than matching real OS-level complexity.

---

## Author

Vishal Tiwari
