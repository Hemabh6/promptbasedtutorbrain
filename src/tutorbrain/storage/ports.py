"""Storage ports.

Protocols, not base classes: an adapter satisfies a port by shape, so no storage
implementation needs to import the runtime. This is the dependency direction rule D3 —
a store never depends on an engine — expressed structurally.

The state store is the only component permitted to persist. Engines emit candidates; the
Orchestrator commits them (rule D2).
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from tutorbrain.contracts import (
    AnswerEvaluation,
    Event,
    MemoryRecord,
    RevisionRecord,
    Rubric,
    Student,
    StudentId,
    StudyPlan,
    StudySession,
    Topic,
    TopicId,
)


class ConcurrencyError(Exception):
    """Raised when a write is attempted against a stale version.

    The required behaviour is to reload, recompute, and re-present to the student — never to
    force the write (`docs/07 Student Model.md`).
    """

    def __init__(self, entity: str, expected: int, actual: int) -> None:
        super().__init__(f"{entity} version conflict: expected {expected}, found {actual}")
        self.entity = entity
        self.expected = expected
        self.actual = actual


class NotFoundError(Exception):
    """Raised when a required record is absent.

    Distinct from an empty collection: a missing student is a failure, whereas a student with
    no revisions is a valid state.
    """


@runtime_checkable
class StudentRepository(Protocol):
    def get(self, student_id: StudentId) -> Student: ...

    def save(self, student: Student) -> Student:
        """Persist with optimistic concurrency on `profile_version`.

        Returns the stored record with its incremented version. Raises `ConcurrencyError`
        when the supplied version is stale.
        """
        ...

    def exists(self, student_id: StudentId) -> bool: ...


@runtime_checkable
class EventLog(Protocol):
    """Append-only ledger (ADR-0002). Offers no update or delete."""

    def append(self, event: Event) -> Event: ...

    def list_for_student(
        self, student_id: StudentId, *, since: datetime | None = None
    ) -> list[Event]: ...


@runtime_checkable
class MemoryRepository(Protocol):
    def add(self, record: MemoryRecord) -> MemoryRecord: ...

    def list_for_student(
        self, student_id: StudentId, *, topic_id: TopicId | None = None
    ) -> list[MemoryRecord]: ...


@runtime_checkable
class RevisionRepository(Protocol):
    def upsert(self, record: RevisionRecord) -> RevisionRecord: ...

    def list_for_student(self, student_id: StudentId) -> list[RevisionRecord]: ...


@runtime_checkable
class PlanRepository(Protocol):
    def upsert(self, plan: StudyPlan) -> StudyPlan: ...

    def list_for_student(self, student_id: StudentId) -> list[StudyPlan]: ...


@runtime_checkable
class SessionRepository(Protocol):
    def upsert(self, session: StudySession) -> StudySession: ...

    def list_for_student(self, student_id: StudentId) -> list[StudySession]: ...


@runtime_checkable
class AnswerRepository(Protocol):
    def add(self, evaluation: AnswerEvaluation) -> AnswerEvaluation: ...

    def list_for_student(self, student_id: StudentId) -> list[AnswerEvaluation]: ...


@runtime_checkable
class TopicCatalogue(Protocol):
    """Read-only syllabus reference. Static data, not learner state."""

    def get(self, topic_id: TopicId) -> Topic: ...

    def all(self) -> list[Topic]: ...


@runtime_checkable
class RubricRepository(Protocol):
    def get(self, rubric_version: str) -> Rubric: ...
