"""Deadlock recovery strategies.

Strategies:
1) Process termination (priority-based or least-resource-usage)
2) Resource preemption from selected victim processes
"""

from __future__ import annotations

from typing import Dict, List, Tuple

Matrix = List[List[int]]
Vector = List[int]


def terminate_processes(
    deadlocked: List[int],
    allocation: Matrix,
    available: Vector,
    priorities: List[int],
    mode: str = "priority",
) -> Tuple[List[str], Matrix, Vector, List[int]]:
    """Terminate deadlocked processes one-by-one until none remain.

    Higher priority number means lower importance (more likely to be terminated)
    in `priority` mode.
    """
    steps: List[str] = []
    new_allocation = [row[:] for row in allocation]
    new_available = available[:]
    terminated: List[int] = []

    candidates = deadlocked[:]
    while candidates:
        victim = _pick_victim(candidates, new_allocation, priorities, mode)
        terminated.append(victim)
        steps.append(f"Terminating P{victim} using mode='{mode}'.")

        # Release all resources held by victim.
        released = new_allocation[victim][:]
        for r_idx, qty in enumerate(released):
            new_available[r_idx] += qty
            new_allocation[victim][r_idx] = 0

        steps.append(f"Released resources from P{victim}: {released}.")
        candidates.remove(victim)

    return steps, new_allocation, new_available, terminated


def preempt_for_recovery(
    deadlocked: List[int],
    allocation: Matrix,
    available: Vector,
    target_resource: int,
    units: int,
) -> Tuple[List[str], Matrix, Vector, Dict[int, int]]:
    """Preempt a specific resource from deadlocked processes for recovery."""
    steps: List[str] = []
    new_allocation = [row[:] for row in allocation]
    new_available = available[:]
    taken_from: Dict[int, int] = {}
    remaining = units

    # Take from processes that hold most of the target resource first.
    sorted_procs = sorted(deadlocked, key=lambda p: new_allocation[p][target_resource], reverse=True)

    for p_idx in sorted_procs:
        if remaining <= 0:
            break
        held = new_allocation[p_idx][target_resource]
        if held <= 0:
            continue

        take = min(held, remaining)
        new_allocation[p_idx][target_resource] -= take
        new_available[target_resource] += take
        taken_from[p_idx] = take
        remaining -= take
        steps.append(f"Preempted {take} unit(s) of R{target_resource} from P{p_idx}.")

    if remaining > 0:
        steps.append(
            f"Recovery preemption incomplete. Requested {units}, recovered {units - remaining}."
        )
    else:
        steps.append(f"Recovery preemption complete. Recovered {units} unit(s).")

    return steps, new_allocation, new_available, taken_from


def _pick_victim(candidates: List[int], allocation: Matrix, priorities: List[int], mode: str) -> int:
    if mode == "least_resource":
        return min(candidates, key=lambda p: sum(allocation[p]))

    # Default priority mode: highest numeric priority value is victim first.
    return max(candidates, key=lambda p: priorities[p])


