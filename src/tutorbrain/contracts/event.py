"""Learning event contract — mirror of `schemas/event.json`.

The append-only ledger record mandated by ADR-0002 and the referent of every
`source_event_id`. Added by ADR-0005 to close that dangling reference.

Events are immutable. Nothing in this module offers a mutation path.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import Field

from tutorbrain.contracts.common import (
    SCHEMA_VERSION,
    Contract,
    CorrelationId,
    EventId,
    SessionId,
    StudentId,
    TopicId,
)


class EventKind(StrEnum):
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    TEACHING_DELIVERED = "teaching_delivered"
    RETRIEVAL_ATTEMPTED = "retrieval_attempted"
    ANSWER_SUBMITTED = "answer_submitted"
    ANSWER_EVALUATED = "answer_evaluated"
    TASK_COMPLETED = "task_completed"
    TASK_SKIPPED = "task_skipped"
    PLAN_ACCEPTED = "plan_accepted"
    PLAN_DECLINED = "plan_declined"
    MEMORY_COMMITTED = "memory_committed"
    REVISION_SCHEDULED = "revision_scheduled"
    ASSUMPTION_RECORDED = "assumption_recorded"


class EventProvenance(Contract):
    """Which component produced this event, and under what prompt and capabilities.

    Required for the audit trail described in `docs/10 System Integration.md`.
    """

    component: str = Field(min_length=1)
    prompt_version: str | None = Field(default=None, min_length=1)
    adapter_capabilities: list[str] = Field(default_factory=list)


class Event(Contract):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    event_id: EventId
    student_id: StudentId
    kind: EventKind
    occurred_at: datetime
    recorded_at: datetime
    session_id: SessionId | None = None
    topic_id: TopicId | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    produced_by: EventProvenance | None = None
    correlation_id: CorrelationId | None = None
