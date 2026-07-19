"""Study session contract — mirror of `schemas/session.json`.

Durable working context. Persisting this is what lets a student resume tomorrow from where
they stopped. Holds no evidence: evidence lives in the event ledger (ADR-0005).
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from tutorbrain.contracts.common import (
    SCHEMA_VERSION,
    ActionType,
    Contract,
    CorrelationId,
    EventId,
    EvidenceType,
    PlanId,
    PriorityBand,
    SessionId,
    StudentId,
    TopicId,
)


class SessionStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

    @property
    def is_resumable(self) -> bool:
        return self in (SessionStatus.ACTIVE, SessionStatus.SUSPENDED)


class ActionStatus(StrEnum):
    SELECTED = "selected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"
    FAILED = "failed"


class ActionRecord(Contract):
    """An action as recorded in session context.

    Distinct from the Decision Engine's `ActionRequest`: that is a selection with a score
    trace, this is the durable trace of what the session did with it.
    """

    action_type: ActionType
    topic_id: TopicId
    objective: str = Field(min_length=1)
    status: ActionStatus
    duration_minutes: int = Field(default=0, ge=0)
    evidence_expected: EvidenceType = EvidenceType.NONE
    selected_band: PriorityBand | None = None
    fallback_action: str | None = Field(default=None, min_length=1)
    correlation_id: CorrelationId | None = None


class StudySession(Contract):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    session_id: SessionId
    student_id: StudentId
    status: SessionStatus
    started_at: datetime
    timezone: str = Field(min_length=1)
    planned_minutes: int = Field(ge=0)
    plan_id: PlanId | None = None
    last_activity_at: datetime | None = None
    ended_at: datetime | None = None
    elapsed_minutes: int = Field(default=0, ge=0)
    current_action: ActionRecord | None = None
    completed_actions: list[ActionRecord] = Field(default_factory=list)
    emitted_event_ids: list[EventId] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    resume_hint: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _terminal_sessions_are_closed(self) -> StudySession:
        terminal = self.status in (SessionStatus.COMPLETED, SessionStatus.ABANDONED)
        if terminal and self.ended_at is None:
            raise ValueError(f"{self.status.value} session must record ended_at")
        if not terminal and self.ended_at is not None:
            raise ValueError("open session must not record ended_at")
        if terminal and self.current_action is not None:
            raise ValueError("terminal session must not hold an in-flight action")
        return self

    @property
    def remaining_minutes(self) -> int:
        return max(0, self.planned_minutes - self.elapsed_minutes)
