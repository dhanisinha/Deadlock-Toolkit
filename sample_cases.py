"""Sample test cases for quick experimentation."""

from __future__ import annotations

from typing import Any, Dict


SAMPLE_CASES: Dict[str, Dict[str, Any]] = {
    "safe_case": {
        "process_count": 5,
        "resource_count": 3,
        "allocation": [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ],
        "max_matrix": [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ],
        "available": [3, 3, 2],
        "priorities": [1, 2, 0, 3, 4],
    },
    "deadlock_case": {
        "process_count": 3,
        "resource_count": 3,
        "allocation": [
            [1, 0, 1],
            [1, 1, 0],
            [0, 1, 1],
        ],
        "max_matrix": [
            [2, 1, 2],
            [2, 2, 1],
            [1, 2, 2],
        ],
        "available": [0, 0, 0],
        "priorities": [2, 1, 0],
    },
}
