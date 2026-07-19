"""Port-satisfying adapters over a shared backend.

Several ports declare the same method names (`get`, `add`, `list_for_student`) at different
types, so a single class cannot structurally satisfy all of them. Each adapter here exposes
exactly one port and delegates to the shared `JsonFileStore`.

This is interface segregation made concrete: a component that only reads topics receives a
`TopicCatalogue` and cannot reach the event ledger, regardless of what the backend can do.
"""

from __future__ import annotations

from datetime import datetime

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
from tutorbrain.storage.json_store import JsonFileStore


class _Backed:
    __slots__ = ("_store",)

    def __init__(self, store: JsonFileStore) -> None:
        self._store = store


class JsonStudentRepository(_Backed):
    def get(self, student_id: StudentId) -> Student:
        return self._store.get(student_id)

    def save(self, student: Student) -> Student:
        return self._store.save(student)

    def exists(self, student_id: StudentId) -> bool:
        return self._store.exists(student_id)


class JsonEventLog(_Backed):
    def append(self, event: Event) -> Event:
        return self._store.append(event)

    def list_for_student(
        self, student_id: StudentId, *, since: datetime | None = None
    ) -> list[Event]:
        return self._store.list_events(student_id, since=since)


class JsonMemoryRepository(_Backed):
    def add(self, record: MemoryRecord) -> MemoryRecord:
        return self._store.add_memory(record)

    def list_for_student(
        self, student_id: StudentId, *, topic_id: TopicId | None = None
    ) -> list[MemoryRecord]:
        return self._store.list_memory(student_id, topic_id=topic_id)


class JsonRevisionRepository(_Backed):
    def upsert(self, record: RevisionRecord) -> RevisionRecord:
        return self._store.upsert_revision(record)

    def list_for_student(self, student_id: StudentId) -> list[RevisionRecord]:
        return self._store.list_revisions(student_id)


class JsonPlanRepository(_Backed):
    def upsert(self, plan: StudyPlan) -> StudyPlan:
        return self._store.upsert_plan(plan)

    def list_for_student(self, student_id: StudentId) -> list[StudyPlan]:
        return self._store.list_plans(student_id)


class JsonSessionRepository(_Backed):
    def upsert(self, session: StudySession) -> StudySession:
        return self._store.upsert_session(session)

    def list_for_student(self, student_id: StudentId) -> list[StudySession]:
        return self._store.list_sessions(student_id)


class JsonAnswerRepository(_Backed):
    def add(self, evaluation: AnswerEvaluation) -> AnswerEvaluation:
        return self._store.add_answer(evaluation)

    def list_for_student(self, student_id: StudentId) -> list[AnswerEvaluation]:
        return self._store.list_answers(student_id)


class JsonTopicCatalogue(_Backed):
    def get(self, topic_id: TopicId) -> Topic:
        return self._store.get_topic(topic_id)

    def all(self) -> list[Topic]:
        return self._store.all_topics()


class JsonRubricRepository(_Backed):
    def get(self, rubric_version: str) -> Rubric:
        return self._store.get_rubric(rubric_version)


class Repositories:
    """Every port, wired to one backend.

    Assembled once at the composition root and injected downward, so no component constructs
    its own storage.
    """

    __slots__ = (
        "answers",
        "events",
        "memory",
        "plans",
        "revisions",
        "rubrics",
        "sessions",
        "students",
        "topics",
    )

    def __init__(self, store: JsonFileStore) -> None:
        self.students = JsonStudentRepository(store)
        self.events = JsonEventLog(store)
        self.memory = JsonMemoryRepository(store)
        self.revisions = JsonRevisionRepository(store)
        self.plans = JsonPlanRepository(store)
        self.sessions = JsonSessionRepository(store)
        self.answers = JsonAnswerRepository(store)
        self.topics = JsonTopicCatalogue(store)
        self.rubrics = JsonRubricRepository(store)
