"""Shared primitives for every runtime contract.

Types here mirror the enumerations fixed by the Phase 1 schemas. They exist so that an
invalid value is unrepresentable rather than merely rejected at the boundary.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Final, Literal

from pydantic import BaseModel, ConfigDict, Field

SchemaVersion = Literal["1.0"]
"""The schema version every contract currently declares.

Typed as a Literal rather than `str` so a contract's default cannot drift from its declared
version without a type error.
"""

SCHEMA_VERSION: Final[SchemaVersion] = "1.0"

# Identifiers are distinct string aliases. They document intent at call sites; they are not
# newtypes, because the schemas define them as plain strings and the storage layer round-trips
# them as such.
StudentId = Annotated[str, Field(min_length=1)]
TopicId = Annotated[str, Field(min_length=1)]
SessionId = Annotated[str, Field(min_length=1)]
EventId = Annotated[str, Field(min_length=1)]
MemoryId = Annotated[str, Field(min_length=1)]
RevisionId = Annotated[str, Field(min_length=1)]
PlanId = Annotated[str, Field(min_length=1)]
AnswerId = Annotated[str, Field(min_length=1)]
TaskId = Annotated[str, Field(min_length=1)]
CorrelationId = Annotated[str, Field(min_length=1)]

UnitInterval = Annotated[float, Field(ge=0.0, le=1.0)]
"""A normalised 0-1 value: mastery, confidence, exam weight, effort cost."""


class ActionType(StrEnum):
    """Decision Engine action types.

    Mirrors the action-type table in `docs/03 Decision Engine.md`. Every member except
    CLARIFY resolves to exactly one prompt contract.
    """

    TEACH = "teach"
    DIAGNOSE = "diagnose"
    PRACTICE = "practice"
    RETRIEVE = "retrieve"
    REVISE = "revise"
    EVALUATE_ANSWER = "evaluate_answer"
    DRAFT_CHECK = "draft_check"
    PLAN = "plan"
    RESCHEDULE = "reschedule"
    MENTOR_CHECKIN = "mentor_checkin"
    ANALYSE_PYQ = "analyse_pyq"
    BRIEF_CURRENT_AFFAIRS = "brief_current_affairs"
    CLARIFY = "clarify"


class PriorityBand(StrEnum):
    """Constitution §4 priority bands.

    Ordering is significant: P0 is highest. Comparison is provided by `rank`, because
    StrEnum members compare as strings.
    """

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"

    @property
    def rank(self) -> int:
        """Lower is more urgent. P0 -> 0."""
        return int(self.value[1])


class EvidenceType(StrEnum):
    """Completion evidence a task or action produces."""

    RETRIEVAL = "retrieval"
    PRACTICE = "practice"
    ANSWER = "answer"
    REVIEW = "review"
    ATTENDANCE = "attendance"
    NONE = "none"


class RecallOutcome(StrEnum):
    """Revision quality bands.

    SKIPPED is not a failure: it leaves the item due and MUST NOT advance the interval or
    count as a lapse (`docs/05 Revision Engine.md`).
    """

    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"
    SKIPPED = "skipped"

    @property
    def is_successful_retrieval(self) -> bool:
        return self in (RecallOutcome.GOOD, RecallOutcome.EASY)

    @property
    def is_lapse(self) -> bool:
        return self in (RecallOutcome.AGAIN, RecallOutcome.HARD)


class RubricDimension(StrEnum):
    """The eight scored dimensions fixed by `schemas/answer.json`."""

    RELEVANCE = "relevance"
    COVERAGE = "coverage"
    STRUCTURE = "structure"
    ACCURACY = "accuracy"
    ANALYSIS = "analysis"
    EVIDENCE = "evidence"
    BALANCE = "balance"
    CONCLUSION = "conclusion"


class Contract(BaseModel):
    """Base class for every runtime contract.

    `extra="forbid"` mirrors `additionalProperties: false` across the schemas: an undeclared
    field is a validation failure, never a forward-compatibility mechanism
    (`schemas/README.md` rule 3).

    Instances are frozen. Contracts describe observed or committed state; mutating one in
    place would let a caller bypass the validate-then-commit sequence required by ADR-0003.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=False,
    )
