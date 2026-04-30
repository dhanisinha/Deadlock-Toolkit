"""Banker's algorithm helpers for deadlock avoidance.

This module focuses on:
1) Need matrix computation
2) Safe-state check and safe sequence generation
3) Request validation and dry-run grant checks
"""

from __future__ import annotations

from typing import List, Tuple

Matrix = List[List[int]]
Vector = List[int]


def compute_need(max_matrix: Matrix, allocation: Matrix) -> Matrix:
    """Compute Need = Max - Allocation for each process/resource."""
    need: Matrix = []
    for p_idx in range(len(max_matrix)):
        row: List[int] = []
        for r_idx in range(len(max_matrix[p_idx])):
            row.append(max_matrix[p_idx][r_idx] - allocation[p_idx][r_idx])
        need.append(row)
    return need


def is_safe_state(
    allocation: Matrix,
    max_matrix: Matrix,
    available: Vector,
) -> Tuple[bool, List[int]]:
    """Return whether the state is safe and one safe sequence if it exists."""
    process_count = len(allocation)
    need = compute_need(max_matrix, allocation)
    work = available[:]
    finish = [False] * process_count
    safe_sequence: List[int] = []

    progress = True
    while progress:
        progress = False
        for p_idx in range(process_count):
            if finish[p_idx]:
                continue

            can_finish = all(
                need[p_idx][r_idx] <= work[r_idx]
                for r_idx in range(len(work))
            )
            if can_finish:
                for r_idx in range(len(work)):
                    work[r_idx] += allocation[p_idx][r_idx]
                finish[p_idx] = True
                safe_sequence.append(p_idx)
                progress = True

    safe = all(finish)
    return safe, safe_sequence


def validate_request(
    process_id: int,
    request: Vector,
    allocation: Matrix,
    max_matrix: Matrix,
    available: Vector,
) -> Tuple[bool, str]:
    """Check if request obeys Need and Available constraints."""
    if process_id < 0 or process_id >= len(allocation):
        return False, "Invalid process id."

    need = compute_need(max_matrix, allocation)

    if len(request) != len(available):
        return False, "Request vector size does not match resource count."

    for r_idx, qty in enumerate(request):
        if qty < 0:
            return False, f"Request cannot contain negative values (resource R{r_idx})."
        if qty > need[process_id][r_idx]:
            return False, f"Request exceeds remaining Need for resource R{r_idx}."
        if qty > available[r_idx]:
            return False, f"Not enough Available instances of resource R{r_idx}."

    return True, "Request is valid."


def can_grant_request(
    process_id: int,
    request: Vector,
    allocation: Matrix,
    max_matrix: Matrix,
    available: Vector,
) -> Tuple[bool, List[int]]:
    """Simulate granting a request and run safe-state check.

    Returns (is_safe_after_grant, safe_sequence).
    """
    valid, _ = validate_request(process_id, request, allocation, max_matrix, available)
    if not valid:
        return False, []

    temp_allocation = [row[:] for row in allocation]
    temp_available = available[:]

    for r_idx, qty in enumerate(request):
        temp_available[r_idx] -= qty
        temp_allocation[process_id][r_idx] += qty

    return is_safe_state(temp_allocation, max_matrix, temp_available)


