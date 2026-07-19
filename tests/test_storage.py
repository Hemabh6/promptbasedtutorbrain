"""Storage behaviour.

Covers the properties the specifications require of persistence: optimistic concurrency,
append-only events, validated writes, and structural conformance to the ports.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from tutorbrain.contracts import (
    Event,
    EventKind,
    MemoryKind,
    MemoryRecord,
    RecallOutcome,
    RevisionAttempt,
    RevisionRecord,
    RevisionStatus,
    Topic,
)
from tutorbrain.runtime import TutorContext
from tutorbrain.seed import DEMO_STUDENT_ID, demo_student, demo_topics
from tutorbrain.storage import (
    ConcurrencyError,
    EventLog,
    MemoryRepository,
    NotFoundError,
    StudentRepository,
    TopicCatalogue,
)

NOW = datetime(2026, 7, 19, 10, 0, tzinfo=UTC)


def _event(event_id: str, kind: EventKind = EventKind.SESSION_STARTED) -> Event:
    return Event(
        event_id=event_id,
        student_id=DEMO_STUDENT_ID,
        kind=kind,
        occurred_at=NOW,
        recorded_at=NOW,
    )


class TestPortConformance:
    """Adapters satisfy their ports structurally, without inheritance."""

    def test_repositories_satisfy_protocols(self, context: TutorContext) -> None:
        repos = context.repositories
        assert isinstance(repos.students, StudentRepository)
        assert isinstance(repos.events, EventLog)
        assert isinstance(repos.memory, MemoryRepository)
        assert isinstance(repos.topics, TopicCatalogue)


class TestStudentRepository:
    def test_missing_student_raises(self, context: TutorContext) -> None:
        with pytest.raises(NotFoundError):
            context.repositories.students.get("nobody")

    def test_save_increments_profile_version(self, context: TutorContext) -> None:
        stored = context.repositories.students.save(demo_student())
        assert stored.profile_version == 2

    def test_round_trip(self, context: TutorContext) -> None:
        context.repositories.students.save(demo_student())
        loaded = context.repositories.students.get(DEMO_STUDENT_ID)
        assert loaded.exam_context.exam == "UPSC Civil Services"
        assert loaded.availability.weekly_minutes == 900

    def test_stale_write_is_rejected(self, context: TutorContext) -> None:
        """A slow response must not overwrite a newer student choice."""
        repo = context.repositories.students
        repo.save(demo_student())  # stored at version 2
        stale = demo_student()  # still claims version 1
        with pytest.raises(ConcurrencyError) as exc:
            repo.save(stale)
        assert exc.value.expected == 1
        assert exc.value.actual == 2

    def test_sequential_writes_succeed(self, context: TutorContext) -> None:
        repo = context.repositories.students
        current = repo.save(demo_student())
        again = repo.save(current)
        assert again.profile_version == 3

    def test_exists(self, context: TutorContext) -> None:
        repo = context.repositories.students
        assert not repo.exists(DEMO_STUDENT_ID)
        repo.save(demo_student())
        assert repo.exists(DEMO_STUDENT_ID)


class TestEventLog:
    def test_append_and_read_back(self, context: TutorContext) -> None:
        log = context.repositories.events
        log.append(_event("ev_1"))
        log.append(_event("ev_2", EventKind.TEACHING_DELIVERED))
        events = log.list_for_student(DEMO_STUDENT_ID)
        assert [e.event_id for e in events] == ["ev_1", "ev_2"]

    def test_empty_log_is_not_an_error(self, context: TutorContext) -> None:
        assert context.repositories.events.list_for_student(DEMO_STUDENT_ID) == []

    def test_filter_by_time(self, context: TutorContext) -> None:
        log = context.repositories.events
        old = Event(
            event_id="old",
            student_id=DEMO_STUDENT_ID,
            kind=EventKind.SESSION_STARTED,
            occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
            recorded_at=NOW,
        )
        log.append(old)
        log.append(_event("new"))
        recent = log.list_for_student(DEMO_STUDENT_ID, since=datetime(2026, 6, 1, tzinfo=UTC))
        assert [e.event_id for e in recent] == ["new"]

    def test_log_offers_no_mutation(self, context: TutorContext) -> None:
        """ADR-0002: the ledger is append-only."""
        log = context.repositories.events
        assert not hasattr(log, "update")
        assert not hasattr(log, "delete")


class TestMemoryRepository:
    def _record(self, memory_id: str, topic_id: str = "polity") -> MemoryRecord:
        return MemoryRecord(
            memory_id=memory_id,
            student_id=DEMO_STUDENT_ID,
            kind=MemoryKind.FACT,
            topic_id=topic_id,
            content="Article 21 protects life and personal liberty.",
            source_event_id="ev_1",
            recorded_at=NOW,
            confidence=0.9,
        )

    def test_add_and_list(self, context: TutorContext) -> None:
        repo = context.repositories.memory
        repo.add(self._record("m1"))
        assert len(repo.list_for_student(DEMO_STUDENT_ID)) == 1

    def test_duplicate_id_rejected(self, context: TutorContext) -> None:
        repo = context.repositories.memory
        repo.add(self._record("m1"))
        with pytest.raises(ValueError, match="already exists"):
            repo.add(self._record("m1"))

    def test_filter_by_topic(self, context: TutorContext) -> None:
        repo = context.repositories.memory
        repo.add(self._record("m1", "polity"))
        repo.add(self._record("m2", "polity.fundamental_rights"))
        found = repo.list_for_student(DEMO_STUDENT_ID, topic_id="polity.fundamental_rights")
        assert [r.memory_id for r in found] == ["m2"]


class TestRevisionRepository:
    def test_upsert_replaces_in_place(self, context: TutorContext) -> None:
        repo = context.repositories.revisions
        record = RevisionRecord(
            revision_id="rev_1",
            student_id=DEMO_STUDENT_ID,
            topic_id="polity.fundamental_rights",
            cue="Which article protects life and personal liberty?",
            status=RevisionStatus.ACTIVE,
            interval_days=1,
            next_due_at=NOW,
        )
        repo.upsert(record)
        attempted = record.model_copy(
            update={
                "interval_days": 3,
                "attempts": [
                    RevisionAttempt(
                        attempted_at=NOW, outcome=RecallOutcome.GOOD, confidence=0.8
                    )
                ],
            }
        )
        repo.upsert(attempted)
        stored = repo.list_for_student(DEMO_STUDENT_ID)
        assert len(stored) == 1
        assert stored[0].interval_days == 3


class TestTopicCatalogue:
    def test_seeded_catalogue_reads_back(self, seeded: TutorContext) -> None:
        assert len(seeded.repositories.topics.all()) == len(demo_topics())

    def test_get_by_id(self, seeded: TutorContext) -> None:
        topic = seeded.repositories.topics.get("polity.fundamental_rights")
        assert topic.title == "Fundamental Rights"

    def test_unknown_topic_raises(self, seeded: TutorContext) -> None:
        with pytest.raises(NotFoundError):
            seeded.repositories.topics.get("polity.nonexistent")

    def test_catalogue_is_read_only(self, seeded: TutorContext) -> None:
        """No engine can rewrite the syllabus mid-session."""
        assert not hasattr(seeded.repositories.topics, "replace")
        assert not hasattr(seeded.repositories.topics, "add")

    def test_unknown_prerequisite_rejected(self, context: TutorContext) -> None:
        bad = Topic(
            topic_id="polity.orphan",
            title="Orphan",
            paper="GS2",
            exam_weight=0.5,
            prerequisites=["polity.does_not_exist"],
        )
        with pytest.raises(ValueError, match="unknown topics"):
            context.store.replace_topics([bad])

    def test_duplicate_topic_id_rejected(self, context: TutorContext) -> None:
        topic = Topic(topic_id="polity", title="A", paper="GS2", exam_weight=0.5)
        with pytest.raises(ValueError, match="duplicate topic_id"):
            context.store.replace_topics([topic, topic])


class TestDurability:
    def test_state_survives_a_new_runtime(self, context: TutorContext) -> None:
        """The property behind 'continue tomorrow': a fresh process sees prior state."""
        from tutorbrain.runtime import build_context

        context.repositories.students.save(demo_student())
        context.store.replace_topics(demo_topics())

        reopened = build_context(context.data_root, schema_dir=context.validator._schema_dir)
        assert reopened.repositories.students.get(DEMO_STUDENT_ID).student_id == DEMO_STUDENT_ID
        assert len(reopened.repositories.topics.all()) == len(demo_topics())

    def test_written_files_are_human_readable_json(self, context: TutorContext) -> None:
        import json

        context.repositories.students.save(demo_student())
        path = context.data_root / "students" / f"{DEMO_STUDENT_ID}.json"
        assert path.is_file()
        assert json.loads(path.read_text(encoding="utf-8"))["student_id"] == DEMO_STUDENT_ID
