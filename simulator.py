"""Simulation engine for deadlock handling toolkit.

This module coordinates:
- state updates from incoming resource requests
- prevention checks
- Banker's avoidance checks
- deadlock detection and optional recovery triggers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from bankers import can_grant_request, compute_need, is_safe_state, validate_request
from detection import run_detection_algorithm
from prevention import (
    PreventionStrategy,
    check_hold_and_wait,
    check_resource_ordering,
    try_preempt_resources,
)

Matrix = List[List[int]]
Vector = List[int]


@dataclass
class SystemState:
    process_count: int
    resource_count: int
    allocation: Matrix
    max_matrix: Matrix
    available: Vector
    request_matrix: Matrix = field(default_factory=list)
    priorities: List[int] = field(default_factory=list)
    strategy: PreventionStrategy = PreventionStrategy.NONE
    last_requested_resource_idx: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.request_matrix:
            self.request_matrix = [
                [0 for _ in range(self.resource_count)] for _ in range(self.process_count)
            ]
        if not self.priorities:
            self.priorities = [idx for idx in range(self.process_count)]
        if not self.last_requested_resource_idx:
            self.last_requested_resource_idx = [0 for _ in range(self.process_count)]

    @property
    def need(self) -> Matrix:
        return compute_need(self.max_matrix, self.allocation)

    def format_matrix(self, title: str, matrix: Matrix) -> str:
        lines = [title]
        for idx, row in enumerate(matrix):
            lines.append(f"P{idx}: {row}")
        return "\n".join(lines)

    def format_vector(self, title: str, vector: Vector) -> str:
        return f"{title}: {vector}"


class DeadlockSimulator:
    """Main simulation class used by CLI and tests."""

    def __init__(self, state: SystemState):
        self.state = state

    def choose_strategy(self, strategy: PreventionStrategy) -> None:
        self.state.strategy = strategy

    def check_safe_state(self) -> Tuple[bool, List[int]]:
        return is_safe_state(self.state.allocation, self.state.max_matrix, self.state.available)

    def detect(self) -> Tuple[bool, List[int]]:
        return run_detection_algorithm(self.state.allocation, self.state.request_matrix, self.state.available)

    def release_all_of_process(self, process_id: int) -> None:
        released = self.state.allocation[process_id][:]
        for r_idx, qty in enumerate(released):
            self.state.available[r_idx] += qty
            self.state.allocation[process_id][r_idx] = 0
            self.state.request_matrix[process_id][r_idx] = 0

    def process_request(self, process_id: int, request: Vector) -> Tuple[bool, str]:
        """Handle one request in the real-time simulation loop."""
        valid, msg = validate_request(
            process_id,
            request,
            self.state.allocation,
            self.state.max_matrix,
            self.state.available,
        )
        if not valid:
            # Keep outstanding request for detection visibility.
            self.state.request_matrix[process_id] = request[:]
            return False, f"Request rejected (validation): {msg}"

        prevention_ok, prevention_msg = self._apply_prevention(process_id, request)
        if not prevention_ok:
            self.state.request_matrix[process_id] = request[:]
            return False, prevention_msg

        safe, safe_seq = can_grant_request(
            process_id,
            request,
            self.state.allocation,
            self.state.max_matrix,
            self.state.available,
        )
        if not safe:
            self.state.request_matrix[process_id] = request[:]
            return (
                False,
                "Banker's Algorithm rejected request: unsafe state would occur.",
            )

        # Commit the request when it is valid, prevention-approved, and safe.
        for r_idx, qty in enumerate(request):
            self.state.available[r_idx] -= qty
            self.state.allocation[process_id][r_idx] += qty
            self.state.request_matrix[process_id][r_idx] = 0

        return True, f"Request granted. Safe sequence after grant: {self._fmt_sequence(safe_seq)}"

    def _apply_prevention(self, process_id: int, request: Vector) -> Tuple[bool, str]:
        strategy = self.state.strategy

        if strategy == PreventionStrategy.NONE:
            return True, "No prevention strategy selected."

        if strategy == PreventionStrategy.HOLD_AND_WAIT:
            result = check_hold_and_wait(process_id, request, self.state.allocation)
            return result.allowed, result.message

        if strategy == PreventionStrategy.RESOURCE_ORDERING:
            result = check_resource_ordering(
                process_id,
                request,
                self.state.last_requested_resource_idx,
            )
            return result.allowed, result.message

        if strategy == PreventionStrategy.PREEMPTION:
            result, new_alloc, new_avail = try_preempt_resources(
                process_id,
                request,
                self.state.allocation,
                self.state.available,
            )
            if result.allowed:
                self.state.allocation = new_alloc
                self.state.available = new_avail
            return result.allowed, result.message

        return True, "Unknown strategy ignored."

    @staticmethod
    def _fmt_sequence(sequence: List[int]) -> str:
        if not sequence:
            return "None"
        return " -> ".join(f"P{idx}" for idx in sequence)




def build_state_from_input(
    process_count: int,
    resource_count: int,
    allocation: Matrix,
    max_matrix: Matrix,
    available: Vector,
    priorities: Optional[List[int]] = None,
) -> SystemState:
    """Factory helper used by CLI and test cases."""
    return SystemState(
        process_count=process_count,
        resource_count=resource_count,
        allocation=allocation,
        max_matrix=max_matrix,
        available=available,
        priorities=priorities or [],
    )
