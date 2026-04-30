"""Deadlock prevention strategies.

Strategies included:
1) Eliminate Hold and Wait
2) Enforce Resource Ordering
3) Allow Resource Preemption
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

Matrix = List[List[int]]
Vector = List[int]


class PreventionStrategy(str, Enum):
    NONE = "none"
    HOLD_AND_WAIT = "hold_and_wait"
    RESOURCE_ORDERING = "resource_ordering"
    PREEMPTION = "preemption"


@dataclass
class PreventionResult:
    allowed: bool
    message: str
    preempted_from: Optional[int] = None
    preempted_resource: Optional[int] = None
    preempted_amount: int = 0


def check_hold_and_wait(process_id: int, request: Vector, allocation: Matrix) -> PreventionResult:
    """Prevent hold-and-wait by requiring empty allocation before requesting.

    Educational simplification: a process must request resources only when it
    currently holds none.
    """
    if any(value > 0 for value in allocation[process_id]) and any(q > 0 for q in request):
        return PreventionResult(
            allowed=False,
            message=(
                "Hold-and-Wait prevention blocked request: process already holds "
                "resources and cannot request more."
            ),
        )
    return PreventionResult(True, "Request passes Hold-and-Wait prevention.")


def check_resource_ordering(process_id: int, request: Vector, last_resource_index: List[int]) -> PreventionResult:
    """Enforce increasing resource index order for requests.

    If process requested Rk previously, next requested resource index must be >= k.
    """
    requested_indices = [idx for idx, qty in enumerate(request) if qty > 0]
    if not requested_indices:
        return PreventionResult(True, "Empty request passes resource ordering.")

    smallest_requested = min(requested_indices)
    if smallest_requested < last_resource_index[process_id]:
        return PreventionResult(
            allowed=False,
            message=(
                "Resource ordering violation: requested lower-order resource "
                f"R{smallest_requested} after previously requesting "
                f"R{last_resource_index[process_id]}."
            ),
        )

    last_resource_index[process_id] = max(requested_indices)
    return PreventionResult(True, "Request follows resource ordering.")


def try_preempt_resources(
    process_id: int,
    request: Vector,
    allocation: Matrix,
    available: Vector,
) -> Tuple[PreventionResult, Matrix, Vector]:
    """Try to free resources from another process so request can proceed.

    This is a simplified preemption strategy for educational simulations.
    """
    new_allocation = [row[:] for row in allocation]
    new_available = available[:]

    for r_idx, needed in enumerate(request):
        shortage = needed - new_available[r_idx]
        if shortage <= 0:
            continue

        donor = _find_best_donor(process_id, r_idx, shortage, new_allocation)
        if donor is None:
            return (
                PreventionResult(
                    allowed=False,
                    message=(
                        f"Preemption failed: no donor found for R{r_idx} "
                        f"(shortage={shortage})."
                    ),
                ),
                allocation,
                available,
            )

        taken = min(shortage, new_allocation[donor][r_idx])
        new_allocation[donor][r_idx] -= taken
        new_available[r_idx] += taken

        return (
            PreventionResult(
                allowed=True,
                message=(
                    f"Preempted {taken} unit(s) of R{r_idx} from P{donor} to "
                    "help satisfy request."
                ),
                preempted_from=donor,
                preempted_resource=r_idx,
                preempted_amount=taken,
            ),
            new_allocation,
            new_available,
        )

    return PreventionResult(True, "No preemption required."), new_allocation, new_available


def _find_best_donor(process_id: int, resource_idx: int, shortage: int, allocation: Matrix) -> Optional[int]:
    """Pick process with highest allocation of a resource as donor."""
    donor = None
    best = 0
    for p_idx in range(len(allocation)):
        if p_idx == process_id:
            continue
        owned = allocation[p_idx][resource_idx]
        if owned > best:
            best = owned
            donor = p_idx

    if best <= 0 or best < 1:
        return None

    _ = shortage
    return donor
