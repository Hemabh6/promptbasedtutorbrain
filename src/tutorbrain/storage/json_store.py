"""JSON file storage adapter.

Chosen deliberately for Phase 2: a directory of readable JSON keeps the student's state
inspectable and portable, which is what `docs/07 Student Model.md` requires of the host
application, and databases are explicitly out of scope.

Every write is validated (ADR-0003) and atomic: content is written to a temporary file in the
same directory and then replaced, so an interrupted write cannot leave a partial record. This
is the file-level form of "a write either completes or leaves state unchanged".
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

from tutorbrain.contracts import (
    AnswerEvaluation,
    Contract,
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
from tutorbrain.storage.ports import ConcurrencyError, NotFoundError
from tutorbrain.validation import SchemaValidator

C = TypeVar("C", bound=Contract)


def _atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


class JsonFileStore:
    """A directory-backed store implementing every storage port.

    Layout::

        root/
          students/<student_id>.json
          events/<student_id>.jsonl        append-only
          memory/<student_id>.json
          revisions/<student_id>.json
          plans/<student_id>.json
          sessions/<student_id>.json
          answers/<student_id>.json
          topics.json
          rubrics.json

    One instance satisfies all ports. They stay separate protocols so a caller depends only
    on the narrow interface it uses (interface segregation), and so a future adapter may
    split them across backends.
    """

    def __init__(self, root: Path, validator: SchemaValidator | None = None) -> None:
        self._root = root
        self._validator = validator or SchemaValidator()
        self._root.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- internals

    def _path(self, area: str, name: str) -> Path:
        return self._root / area / f"{name}.json"

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.is_file():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_contract(self, path: Path, obj: Contract) -> None:
        self._validator.validate(obj).raise_if_invalid()
        _atomic_write(path, json.dumps(self._validator.to_json_dict(obj), indent=2) + "\n")

    def _write_collection(self, path: Path, objs: list[Contract]) -> None:
        for obj in objs:
            self._validator.validate(obj).raise_if_invalid()
        payload = [self._validator.to_json_dict(o) for o in objs]
        _atomic_write(path, json.dumps(payload, indent=2) + "\n")

    def _read_collection(self, path: Path, model: type[C]) -> list[C]:
        return [self._validator.parse(model, item) for item in self._read_json(path, [])]

    # ------------------------------------------------------------ StudentRepository

    def get(self, student_id: StudentId) -> Student:
        path = self._path("students", student_id)
        if not path.is_file():
            raise NotFoundError(f"student not found: {student_id}")
        return self._validator.parse(Student, self._read_json(path, {}))

    def exists(self, student_id: StudentId) -> bool:
        return self._path("students", student_id).is_file()

    def save(self, student: Student) -> Student:
        """Persist with optimistic concurrency.

        The caller supplies the version it read. A mismatch means another write landed first,
        and the correct response is to reload rather than overwrite
        (`docs/07 Student Model.md`).
        """
        path = self._path("students", student.student_id)
        if path.is_file():
            current = self._validator.parse(Student, self._read_json(path, {}))
            if current.profile_version != student.profile_version:
                raise ConcurrencyError(
                    f"student:{student.student_id}",
                    expected=student.profile_version,
                    actual=current.profile_version,
                )
        stored = student.model_copy(update={"profile_version": student.profile_version + 1})
        self._write_contract(path, stored)
        return stored

    # ------------------------------------------------------------------- EventLog

    def append(self, event: Event) -> Event:
        """Append to the ledger.

        JSON Lines, because the ledger is append-only and grows without bound: rewriting a
        whole array per event would make writes O(history).
        """
        self._validator.validate(event).raise_if_invalid()
        path = self._root / "events" / f"{event.student_id}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(self._validator.to_json_dict(event), separators=(",", ":"))
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event

    def list_events(self, student_id: StudentId, *, since: datetime | None = None) -> list[Event]:
        path = self._root / "events" / f"{student_id}.jsonl"
        if not path.is_file():
            return []
        events = [
            self._validator.parse(Event, json.loads(line))
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if since is not None:
            events = [e for e in events if e.occurred_at >= since]
        return events

    # ------------------------------------------------------------ MemoryRepository

    def add_memory(self, record: MemoryRecord) -> MemoryRecord:
        path = self._path("memory", record.student_id)
        records = self._read_collection(path, MemoryRecord)
        if any(r.memory_id == record.memory_id for r in records):
            raise ValueError(f"memory record already exists: {record.memory_id}")
        self._write_collection(path, [*records, record])
        return record

    def list_memory(
        self, student_id: StudentId, *, topic_id: TopicId | None = None
    ) -> list[MemoryRecord]:
        records = self._read_collection(self._path("memory", student_id), MemoryRecord)
        if topic_id is not None:
            records = [r for r in records if r.topic_id == topic_id]
        return records

    # ---------------------------------------------------------- RevisionRepository

    def upsert_revision(self, record: RevisionRecord) -> RevisionRecord:
        path = self._path("revisions", record.student_id)
        records = [
            r
            for r in self._read_collection(path, RevisionRecord)
            if r.revision_id != record.revision_id
        ]
        self._write_collection(path, [*records, record])
        return record

    def list_revisions(self, student_id: StudentId) -> list[RevisionRecord]:
        return self._read_collection(self._path("revisions", student_id), RevisionRecord)

    # -------------------------------------------------------------- PlanRepository

    def upsert_plan(self, plan: StudyPlan) -> StudyPlan:
        path = self._path("plans", plan.student_id)
        plans = [p for p in self._read_collection(path, StudyPlan) if p.plan_id != plan.plan_id]
        self._write_collection(path, [*plans, plan])
        return plan

    def list_plans(self, student_id: StudentId) -> list[StudyPlan]:
        return self._read_collection(self._path("plans", student_id), StudyPlan)

    # ----------------------------------------------------------- SessionRepository

    def upsert_session(self, session: StudySession) -> StudySession:
        path = self._path("sessions", session.student_id)
        sessions = [
            s
            for s in self._read_collection(path, StudySession)
            if s.session_id != session.session_id
        ]
        self._write_collection(path, [*sessions, session])
        return session

    def list_sessions(self, student_id: StudentId) -> list[StudySession]:
        return self._read_collection(self._path("sessions", student_id), StudySession)

    # ------------------------------------------------------------ AnswerRepository

    def add_answer(self, evaluation: AnswerEvaluation) -> AnswerEvaluation:
        path = self._path("answers", evaluation.student_id)
        answers = self._read_collection(path, AnswerEvaluation)
        self._write_collection(path, [*answers, evaluation])
        return evaluation

    def list_answers(self, student_id: StudentId) -> list[AnswerEvaluation]:
        return self._read_collection(self._path("answers", student_id), AnswerEvaluation)

    # -------------------------------------------------------------- TopicCatalogue

    def get_topic(self, topic_id: TopicId) -> Topic:
        topic = next((t for t in self.all_topics() if t.topic_id == topic_id), None)
        if topic is None:
            raise NotFoundError(f"topic not found: {topic_id}")
        return topic

    def all_topics(self) -> list[Topic]:
        return self._read_collection(self._root / "topics.json", Topic)

    def replace_topics(self, topics: list[Topic]) -> None:
        """Seed or replace the syllabus catalogue.

        Rejects duplicate ids and prerequisites that name an unknown topic, so a malformed
        catalogue fails at load rather than during action selection.
        """
        ids = [t.topic_id for t in topics]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate topic_id in catalogue")
        known = set(ids)
        for topic in topics:
            if unknown := set(topic.prerequisites) - known:
                raise ValueError(f"{topic.topic_id} requires unknown topics: {sorted(unknown)}")
            if topic.parent_topic_id and topic.parent_topic_id not in known:
                raise ValueError(f"{topic.topic_id} has unknown parent {topic.parent_topic_id}")
        self._write_collection(self._root / "topics.json", list(topics))

    # ------------------------------------------------------------ RubricRepository

    def get_rubric(self, rubric_version: str) -> Rubric:
        rubrics = self._read_collection(self._root / "rubrics.json", Rubric)
        rubric = next((r for r in rubrics if r.rubric_version == rubric_version), None)
        if rubric is None:
            raise NotFoundError(f"rubric not found: {rubric_version}")
        return rubric

    def replace_rubrics(self, rubrics: list[Rubric]) -> None:
        versions = [r.rubric_version for r in rubrics]
        if len(versions) != len(set(versions)):
            raise ValueError("duplicate rubric_version")
        self._write_collection(self._root / "rubrics.json", list(rubrics))
