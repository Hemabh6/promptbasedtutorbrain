"""Policy parameters — the executable form of Constitution §9.

§9 is the single source of every configurable threshold. This module is its only
representation in code: no other module may define a threshold, and design principle 9
("single source of threshold") makes an inline constant a review failure.

Defaults here MUST match the §9 table. `test_policy.py` asserts that they do.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Self


@dataclass(frozen=True, slots=True)
class PolicyParameters:
    """Configurable thresholds, keyed by their Constitution §9 names.

    Attribute names replace the dotted §9 names with underscores:
    `revision.backlog_threshold` -> `revision_backlog_threshold`.
    """

    # Revision
    revision_backlog_threshold: int = 5
    revision_default_intervals: tuple[int, ...] = (1, 3, 7, 14, 30)
    revision_max_defer_days: int = 2

    # Planning
    planning_capacity_utilization_max: float = 0.85
    planning_min_task_minutes: int = 15

    # Student
    student_mastery_weak_threshold: float = 0.40
    student_mastery_strong_threshold: float = 0.75

    # Memory
    memory_min_confidence_durable: float = 0.60

    # Evaluation
    evaluation_rubric_version: str = "1.0"

    # Prompt
    prompt_validation_retry_max: int = 1

    # Exam
    exam_proximity_compression_days: int = 60

    def __post_init__(self) -> None:
        if not 0 < self.planning_capacity_utilization_max <= 1:
            raise ValueError("planning_capacity_utilization_max must be in (0, 1]")
        weak, strong = self.student_mastery_weak_threshold, self.student_mastery_strong_threshold
        if not 0 <= weak < strong <= 1:
            raise ValueError("mastery thresholds must satisfy 0 <= weak < strong <= 1")
        if not 0 <= self.memory_min_confidence_durable <= 1:
            raise ValueError("memory_min_confidence_durable must be in [0, 1]")
        if not self.revision_default_intervals:
            raise ValueError("revision_default_intervals must not be empty")
        if list(self.revision_default_intervals) != sorted(set(self.revision_default_intervals)):
            raise ValueError("revision_default_intervals must be strictly increasing")
        if self.revision_default_intervals[0] < 1:
            raise ValueError("revision intervals must be at least 1 day")
        if self.planning_min_task_minutes < 1:
            raise ValueError("planning_min_task_minutes must be at least 1")
        if self.prompt_validation_retry_max < 0:
            raise ValueError("prompt_validation_retry_max must not be negative")

    @property
    def recovery_reserve(self) -> float:
        """The fraction of capacity held back for recovery.

        Derived, not configured: it is the complement of the utilisation ceiling, so the two
        can never drift apart.
        """
        return 1.0 - self.planning_capacity_utilization_max

    def usable_capacity(self, declared_minutes: int) -> int:
        """Declared availability reduced by the recovery reserve (Constitution C3)."""
        return int(declared_minutes * self.planning_capacity_utilization_max)

    def is_weak(self, mastery: float) -> bool:
        return mastery < self.student_mastery_weak_threshold

    def is_strong(self, mastery: float) -> bool:
        return mastery >= self.student_mastery_strong_threshold

    def next_interval_after(self, current_days: int) -> int:
        """The next interval in the default ladder.

        Beyond the ladder's end, the last step is applied multiplicatively so intervals keep
        growing rather than silently plateauing.
        """
        ladder = self.revision_default_intervals
        for step in ladder:
            if step > current_days:
                return step
        return current_days * 2

    @classmethod
    def from_file(cls, path: Path) -> Self:
        """Load overrides from JSON.

        Unknown keys are rejected: a typo in a policy file must fail loudly rather than
        silently leave a default in place.
        """
        raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        known = {f.name for f in fields(cls)}
        if unknown := raw.keys() - known:
            raise ValueError(f"unknown policy parameters in {path}: {sorted(unknown)}")
        if "revision_default_intervals" in raw:
            raw["revision_default_intervals"] = tuple(raw["revision_default_intervals"])
        return cls(**raw)


DEFAULT_POLICY = PolicyParameters()
"""The Constitution §9 defaults. Callers requiring different values inject their own."""
