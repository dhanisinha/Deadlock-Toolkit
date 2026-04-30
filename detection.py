"""Deadlock detection module.

Implements a classic detection algorithm based on Work and Finish vectors.
The module expects a request matrix to represent current outstanding requests.
"""

from __future__ import annotations

from typing import List, Tuple

Matrix = List[List[int]]
Vector = List[int]


def run_detection_algorithm(allocation: Matrix, request: Matrix, available: Vector) -> Tuple[bool, List[int]]:
    """Detect deadlocked processes using Work/Finish algorithm."""
    process_count = len(allocation)
    work = available[:]
    finish = [False] * process_count

    for p_idx in range(process_count):
        if all(allocation[p_idx][r_idx] == 0 for r_idx in range(len(available))):
            finish[p_idx] = True

    progress = True
    while progress:
        progress = False
        for p_idx in range(process_count):
            if finish[p_idx]:
                continue

            can_satisfy = all(request[p_idx][r_idx] <= work[r_idx] for r_idx in range(len(work)))
            if can_satisfy:
                for r_idx in range(len(work)):
                    work[r_idx] += allocation[p_idx][r_idx]
                finish[p_idx] = True
                progress = True

    deadlocked = [idx for idx, done in enumerate(finish) if not done]
    return (len(deadlocked) > 0), deadlocked


