"""Revision record contract — mirror of `schemas/revision.json`.

Owns the interval state for one retrievable item. The due set derived from these records is
the sole authority on revision obligation (`docs/05 Revision Engine.md`).
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field

from tutorbrain.contracts.common import (
    SCHEMA_VERSION,
    Contract,
    EventId,
    MemoryId,
    RecallOutcome,
    RevisionId,
    StudentId,
    TopicId,
    UnitInterval,
)


class RevisionStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class RevisionAttempt(Contract):
    attempted_at: datetime
    outcome: RecallOutcome
    confidence: UnitInterval
    cue_presented_first: bool = True
    interval_days_before: int | None = Field(default=None, ge=1)
    interval_days_after: int | None = Field(default=None, ge=1)
    source_event_id: EventId | None = None

    @property
    def counts_toward_interval(self) -> bool:
        """An attempt only advances the interval if the protocol was honoured.

        Revealing the answer before an attempt invalidates the outcome, and a skip leaves the
        item due (`docs/05 Revision Engine.md`).
        """
        return self.cue_presented_first and self.outcome is not RecallOutcome.SKIPPED


class RevisionRecord(Contract):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    revision_id: RevisionId
    student_id: StudentId
    topic_id: TopicId
    cue: str = Field(min_length=1)
    status: RevisionStatus
    interval_days: int = Field(ge=1)
    next_due_at: datetime
    attempts: list[RevisionAttempt] = Field(default_factory=list)
    expected_features: list[str] = Field(default_factory=list)
    source_memory_id: MemoryId | None = None
    ease_factor: float = Field(default=2.5, ge=1.3, le=3.0)
    lapse_count: int = Field(default=0, ge=0)

    def is_due_at(self, moment: datetime) -> bool:
        """Due state at a given instant.

        The caller supplies the moment in the student's declared timezone; this contract
        never reads a clock (`docs/05 Revision Engine.md`).
        """
        return self.status is RevisionStatus.ACTIVE and self.next_due_at <= moment

    @property
    def last_attempt(self) -> RevisionAttempt | None:
        return self.attempts[-1] if self.attempts else None
