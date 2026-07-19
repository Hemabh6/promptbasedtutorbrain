"""Study plan contract — mirror of `schemas/study_plan.json`.

A capacity-bounded allocation of work across one horizon. Proposed until the student accepts
it; at most one accepted plan may exist per student and horizon
(`docs/04 Planning Engine.md`).
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from tutorbrain.contracts.common import (
    SCHEMA_VERSION,
    Contract,
    EvidenceType,
    PlanId,
    RevisionId,
    StudentId,
    TaskId,
    TopicId,
)


class PlanStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    SUPERSEDED = "superseded"
    COMPLETED = "completed"


class TaskStatus(StrEnum):
    PLANNED = "planned"
    BLOCKED = "blocked"
    DONE = "done"
    SKIPPED = "skipped"
    DEFERRED = "deferred"


class TaskSource(StrEnum):
    REVISION_DUE = "revision_due"
    COVERAGE = "coverage"
    PREREQUISITE = "prerequisite"
    ANSWER_PRACTICE = "answer_practice"
    STUDENT_REQUEST = "student_request"


class ConflictKind(StrEnum):
    CAPACITY = "capacity"
    PREREQUISITE = "prerequisite"
    DEADLINE = "deadline"
    REVISION_OVERFLOW = "revision_overflow"


class PlanConflict(Contract):
    kind: ConflictKind
    description: str = Field(min_length=1)
    affected_task_ids: list[TaskId] = Field(default_factory=list)


class PlanTask(Contract):
    task_id: TaskId
    topic_id: TopicId
    objective: str = Field(min_length=1)
    scheduled_for: date
    minutes: int = Field(ge=1)
    evidence_type: EvidenceType
    status: TaskStatus
    source: TaskSource | None = None
    prerequisites: list[TopicId] = Field(default_factory=list)
    revision_id: RevisionId | None = None

    @model_validator(mode="after")
    def _revision_tasks_are_linked(self) -> PlanTask:
        if self.source is TaskSource.REVISION_DUE and self.revision_id is None:
            raise ValueError("revision_due task must carry revision_id")
        return self


class StudyPlan(Contract):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    plan_id: PlanId
    student_id: StudentId
    status: PlanStatus
    horizon_start: date
    horizon_end: date
    capacity_minutes: int = Field(ge=0)
    tasks: list[PlanTask] = Field(default_factory=list)
    supersedes_plan_id: PlanId | None = None
    reserved_revision_minutes: int = Field(default=0, ge=0)
    accepted_at: datetime | None = None
    assumptions: list[str] = Field(default_factory=list)
    conflicts: list[PlanConflict] = Field(default_factory=list)

    @model_validator(mode="after")
    def _structural_invariants(self) -> StudyPlan:
        if self.horizon_end < self.horizon_start:
            raise ValueError("horizon_end precedes horizon_start")
        ids = [t.task_id for t in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate task_id")
        outside = [
            t.task_id
            for t in self.tasks
            if not self.horizon_start <= t.scheduled_for <= self.horizon_end
        ]
        if outside:
            raise ValueError(f"tasks scheduled outside horizon: {outside}")
        if self.status is PlanStatus.ACCEPTED and self.accepted_at is None:
            raise ValueError("accepted plan must record accepted_at")
        return self

    @property
    def scheduled_minutes(self) -> int:
        return sum(t.minutes for t in self.tasks if t.status is not TaskStatus.SKIPPED)

    def minutes_on(self, day: date) -> int:
        return sum(t.minutes for t in self.tasks if t.scheduled_for == day)

    def tasks_on(self, day: date) -> list[PlanTask]:
        return [t for t in self.tasks if t.scheduled_for == day]
