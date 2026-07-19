"""Student profile contract — mirror of `schemas/student.json`.

Authoritative for *current derived state* only. Rebuildable from the event ledger; where the
two disagree, this record is recomputed from Memory, never the reverse (Constitution C6).
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator

from tutorbrain.contracts.common import (
    SCHEMA_VERSION,
    Contract,
    StudentId,
    TopicId,
    UnitInterval,
)

DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


class ExamStage(StrEnum):
    PRELIMS = "prelims"
    MAINS = "mains"
    INTERVIEW = "interview"


class ExamContext(Contract):
    exam: str = Field(min_length=1)
    target_year: int = Field(ge=2020)
    stage: ExamStage
    attempt_number: int | None = Field(default=None, ge=1)
    optional_subject: str | None = Field(default=None, min_length=1)
    exam_date: date | None = None


class Availability(Contract):
    timezone: str = Field(min_length=1)
    minutes_by_day: dict[str, int]
    working_professional: bool = False
    blackout_dates: list[date] = Field(default_factory=list)

    @field_validator("minutes_by_day")
    @classmethod
    def _all_days_present(cls, v: dict[str, int]) -> dict[str, int]:
        missing = set(DAYS) - v.keys()
        if missing:
            raise ValueError(f"missing days: {sorted(missing)}")
        if extra := v.keys() - set(DAYS):
            raise ValueError(f"unknown days: {sorted(extra)}")
        if bad := {d: m for d, m in v.items() if not 0 <= m <= 1440}:
            raise ValueError(f"minutes out of range 0-1440: {bad}")
        return v

    def minutes_for(self, day: date) -> int:
        return self.minutes_by_day[DAYS[day.weekday()]]

    @property
    def weekly_minutes(self) -> int:
        return sum(self.minutes_by_day.values())


class TopicMastery(Contract):
    """Evidence-backed mastery.

    `self_reported_confidence` is stored separately and never substituted for `mastery`:
    the gap between them is itself a diagnostic signal (`docs/07 Student Model.md`).
    """

    topic_id: TopicId
    mastery: UnitInterval
    evidence_count: int = Field(ge=0)
    updated_at: datetime
    self_reported_confidence: UnitInterval | None = None
    last_evidence_id: str | None = Field(default=None, min_length=1)

    @property
    def calibration_error(self) -> float | None:
        """Positive indicates overconfidence. None when confidence was never reported."""
        if self.self_reported_confidence is None:
            return None
        return self.self_reported_confidence - self.mastery


class LearningStyle(Contract):
    """Presentation preferences only.

    MUST NOT alter rubric strictness or factual standards (`docs/07 Student Model.md`).
    """

    preferred_modality: Literal["explanation", "example", "question", "diagram", "mixed"] | None = (
        None
    )
    pacing: Literal["slow", "moderate", "fast"] | None = None
    feedback_tone: Literal["direct", "supportive", "neutral"] | None = None
    example_density: Literal["low", "medium", "high"] | None = None


class Constraint(Contract):
    constraint_id: str = Field(min_length=1)
    kind: Literal["time", "modality", "content", "accessibility", "workload"]
    description: str = Field(min_length=1)
    active_from: date | None = None
    active_until: date | None = None

    def is_active_on(self, day: date) -> bool:
        if self.active_from and day < self.active_from:
            return False
        return not (self.active_until and day > self.active_until)


class PerformanceMetrics(Contract):
    plan_adherence: UnitInterval | None = None
    retrieval_success_rate: UnitInterval | None = None
    mean_rubric_score: float | None = Field(default=None, ge=0, le=5)
    answers_evaluated: int | None = Field(default=None, ge=0)
    confidence_calibration_error: float | None = Field(default=None, ge=-1, le=1)


class RevisionSummary(Contract):
    """Counters only. Revision history is owned by `schemas/revision.json`."""

    active_items: int = Field(default=0, ge=0)
    due_now: int = Field(default=0, ge=0)
    overdue_items: int = Field(default=0, ge=0)


class DerivedProfile(Contract):
    """Projections of `topic_mastery` and the ledger.

    Recomputable and non-authoritative. MUST NOT be edited directly
    (`docs/07 Student Model.md`).
    """

    computed_at: datetime | None = None
    strengths: list[TopicId] = Field(default_factory=list)
    weaknesses: list[TopicId] = Field(default_factory=list)
    performance_metrics: PerformanceMetrics | None = None
    revision_summary: RevisionSummary | None = None


class Student(Contract):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    student_id: StudentId
    profile_version: int = Field(ge=1)
    exam_context: ExamContext
    availability: Availability
    topic_mastery: list[TopicMastery] = Field(default_factory=list)
    learning_style: LearningStyle | None = None
    preferences: dict[str, str | int | float | bool] = Field(default_factory=dict)
    constraints: list[Constraint] = Field(default_factory=list)
    current_focus: str | None = None
    derived: DerivedProfile | None = None

    @field_validator("topic_mastery")
    @classmethod
    def _unique_topics(cls, v: list[TopicMastery]) -> list[TopicMastery]:
        seen = [m.topic_id for m in v]
        if len(seen) != len(set(seen)):
            raise ValueError("duplicate topic_id in topic_mastery")
        return v

    def mastery_for(self, topic_id: TopicId) -> TopicMastery | None:
        return next((m for m in self.topic_mastery if m.topic_id == topic_id), None)

    def mastery_value(self, topic_id: TopicId) -> float:
        """Mastery for a topic, or 0.0 when no evidence exists.

        Absence of evidence is treated as absence of mastery, never as a neutral prior:
        the Decision Engine must be able to distinguish 'unseen' from 'known'.
        """
        m = self.mastery_for(topic_id)
        return m.mastery if m else 0.0
