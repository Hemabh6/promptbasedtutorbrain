"""Contract invariants.

These assert the rules the Phase 1 specifications state in prose — that a skipped revision is
not a lapse, that an evidence-free dimension is invalid, that a terminal session is closed.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from tutorbrain.contracts import (
    ActionRecord,
    ActionStatus,
    ActionType,
    Availability,
    DimensionScore,
    EvidenceType,
    MemoryKind,
    MemoryRecord,
    PlanStatus,
    PlanTask,
    PriorityBand,
    RecallOutcome,
    RevisionAttempt,
    RubricDimension,
    SessionStatus,
    StudyPlan,
    StudySession,
    TaskSource,
    TaskStatus,
    Topic,
)
from tutorbrain.contracts.rubric import Rubric, RubricDimensionWeight
from tutorbrain.seed import demo_student

NOW = datetime(2026, 7, 19, 10, 0, tzinfo=UTC)


class TestPriorityBand:
    def test_p0_outranks_p5(self) -> None:
        assert PriorityBand.P0.rank < PriorityBand.P5.rank

    def test_bands_sort_by_urgency(self) -> None:
        bands = sorted(PriorityBand, key=lambda b: b.rank)
        assert bands[0] is PriorityBand.P0
        assert bands[-1] is PriorityBand.P5


class TestRecallOutcome:
    def test_skipped_is_neither_success_nor_lapse(self) -> None:
        """A skip leaves the item due; it is not a failed attempt."""
        assert not RecallOutcome.SKIPPED.is_successful_retrieval
        assert not RecallOutcome.SKIPPED.is_lapse

    @pytest.mark.parametrize("outcome", [RecallOutcome.GOOD, RecallOutcome.EASY])
    def test_successful_outcomes(self, outcome: RecallOutcome) -> None:
        assert outcome.is_successful_retrieval

    @pytest.mark.parametrize("outcome", [RecallOutcome.AGAIN, RecallOutcome.HARD])
    def test_lapses(self, outcome: RecallOutcome) -> None:
        assert outcome.is_lapse


class TestRevisionAttempt:
    def test_answer_revealed_first_does_not_count(self) -> None:
        attempt = RevisionAttempt(
            attempted_at=NOW, outcome=RecallOutcome.GOOD, confidence=0.9, cue_presented_first=False
        )
        assert not attempt.counts_toward_interval

    def test_skip_does_not_count(self) -> None:
        attempt = RevisionAttempt(attempted_at=NOW, outcome=RecallOutcome.SKIPPED, confidence=0.1)
        assert not attempt.counts_toward_interval

    def test_honoured_protocol_counts(self) -> None:
        attempt = RevisionAttempt(attempted_at=NOW, outcome=RecallOutcome.GOOD, confidence=0.8)
        assert attempt.counts_toward_interval


class TestContractStrictness:
    def test_undeclared_field_is_rejected(self) -> None:
        """additionalProperties: false is mirrored by extra='forbid'."""
        with pytest.raises(PydanticValidationError):
            Topic(topic_id="a", title="A", paper="GS2", exam_weight=0.5, surprise=1)  # type: ignore[call-arg]

    def test_contracts_are_frozen(self) -> None:
        topic = Topic(topic_id="a", title="A", paper="GS2", exam_weight=0.5)
        with pytest.raises(PydanticValidationError):
            topic.title = "B"  # type: ignore[misc]

    def test_malformed_topic_id_is_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            Topic(topic_id="Polity Rights", title="X", paper="GS2", exam_weight=0.5)


class TestTopic:
    def test_match_terms_are_case_folded(self) -> None:
        topic = Topic(
            topic_id="polity.fundamental_rights",
            title="Fundamental Rights",
            aliases=["FR", "Part III"],
            paper="GS2",
            exam_weight=0.85,
        )
        assert "fundamental rights" in topic.match_terms
        assert "fr" in topic.match_terms
        assert "polity.fundamental_rights" in topic.match_terms


class TestStudent:
    def test_availability_requires_all_seven_days(self) -> None:
        with pytest.raises(PydanticValidationError):
            Availability(timezone="Asia/Kolkata", minutes_by_day={"mon": 60})

    def test_unknown_day_rejected(self) -> None:
        days = dict.fromkeys(["mon", "tue", "wed", "thu", "fri", "sat", "sun"], 60)
        with pytest.raises(PydanticValidationError):
            Availability(timezone="Asia/Kolkata", minutes_by_day={**days, "funday": 60})

    def test_unseen_topic_has_zero_mastery(self) -> None:
        """Absence of evidence is absence of mastery, not a neutral prior."""
        assert demo_student().mastery_value("polity.fundamental_rights") == 0.0

    def test_known_topic_returns_recorded_mastery(self) -> None:
        assert demo_student().mastery_value("polity.constitution_basics") == pytest.approx(0.62)

    def test_calibration_error_detects_overconfidence(self) -> None:
        mastery = demo_student().mastery_for("polity.constitution_basics")
        assert mastery is not None
        assert mastery.calibration_error == pytest.approx(0.18)

    def test_weekly_minutes(self) -> None:
        assert demo_student().availability.weekly_minutes == 900


class TestRubric:
    def test_partial_rubric_is_rejected(self) -> None:
        with pytest.raises(PydanticValidationError, match="all eight dimensions"):
            Rubric(
                rubric_version="1.0",
                dimensions=[RubricDimensionWeight(name=RubricDimension.RELEVANCE, weight=1.0)],
            )

    def test_weights_must_sum_to_one(self) -> None:
        with pytest.raises(PydanticValidationError, match=r"sum to 1\.0"):
            Rubric(
                rubric_version="1.0",
                dimensions=[
                    RubricDimensionWeight(name=d, weight=0.5) for d in RubricDimension
                ],
            )

    def test_uniform_rubric_is_valid(self) -> None:
        assert len(Rubric.uniform().dimensions) == 8

    def test_perfect_answer_scores_full_scale(self) -> None:
        rubric = Rubric.uniform()
        assert rubric.compute_total(dict.fromkeys(RubricDimension, 5)) == pytest.approx(100.0)

    def test_zero_answer_scores_zero(self) -> None:
        rubric = Rubric.uniform()
        assert rubric.compute_total(dict.fromkeys(RubricDimension, 0)) == pytest.approx(0.0)

    def test_partial_evaluation_cannot_be_totalled(self) -> None:
        rubric = Rubric.uniform()
        with pytest.raises(ValueError, match="partial evaluation"):
            rubric.compute_total({RubricDimension.RELEVANCE: 5})

    def test_out_of_range_score_rejected(self) -> None:
        rubric = Rubric.uniform()
        with pytest.raises(ValueError, match="outside"):
            rubric.compute_total(dict.fromkeys(RubricDimension, 9))


class TestAnswer:
    def test_dimension_requires_evidence(self) -> None:
        with pytest.raises(PydanticValidationError):
            DimensionScore(
                name=RubricDimension.RELEVANCE, score=4, evidence=[], improvement="tighten"
            )


class TestStudyPlan:
    def _plan(self, **overrides: object) -> StudyPlan:
        base: dict[str, object] = {
            "plan_id": "plan_1",
            "student_id": "stu_demo",
            "status": PlanStatus.PROPOSED,
            "horizon_start": date(2026, 7, 20),
            "horizon_end": date(2026, 7, 26),
            "capacity_minutes": 765,
            "tasks": [],
        }
        return StudyPlan(**{**base, **overrides})  # type: ignore[arg-type]

    def _task(self, task_id: str = "t1", **overrides: object) -> PlanTask:
        base: dict[str, object] = {
            "task_id": task_id,
            "topic_id": "polity.fundamental_rights",
            "objective": "State the scope of Article 21",
            "scheduled_for": date(2026, 7, 21),
            "minutes": 30,
            "evidence_type": EvidenceType.RETRIEVAL,
            "status": TaskStatus.PLANNED,
        }
        return PlanTask(**{**base, **overrides})  # type: ignore[arg-type]

    def test_duplicate_task_id_rejected(self) -> None:
        with pytest.raises(PydanticValidationError, match="duplicate task_id"):
            self._plan(tasks=[self._task("t1"), self._task("t1")])

    def test_task_outside_horizon_rejected(self) -> None:
        with pytest.raises(PydanticValidationError, match="outside horizon"):
            self._plan(tasks=[self._task(scheduled_for=date(2026, 8, 30))])

    def test_inverted_horizon_rejected(self) -> None:
        with pytest.raises(PydanticValidationError, match="precedes"):
            self._plan(horizon_start=date(2026, 7, 26), horizon_end=date(2026, 7, 20))

    def test_accepted_plan_requires_timestamp(self) -> None:
        with pytest.raises(PydanticValidationError, match="accepted_at"):
            self._plan(status=PlanStatus.ACCEPTED)

    def test_revision_task_must_link_revision_id(self) -> None:
        with pytest.raises(PydanticValidationError, match="revision_id"):
            self._task(source=TaskSource.REVISION_DUE)

    def test_scheduled_minutes_excludes_skipped(self) -> None:
        plan = self._plan(
            tasks=[
                self._task("t1", minutes=30),
                self._task("t2", minutes=45, status=TaskStatus.SKIPPED),
            ]
        )
        assert plan.scheduled_minutes == 30


class TestSession:
    def _session(self, **overrides: object) -> StudySession:
        base: dict[str, object] = {
            "session_id": "sess_1",
            "student_id": "stu_demo",
            "status": SessionStatus.ACTIVE,
            "started_at": NOW,
            "timezone": "Asia/Kolkata",
            "planned_minutes": 60,
        }
        return StudySession(**{**base, **overrides})  # type: ignore[arg-type]

    def test_completed_session_requires_end_time(self) -> None:
        with pytest.raises(PydanticValidationError, match="ended_at"):
            self._session(status=SessionStatus.COMPLETED)

    def test_open_session_must_not_have_end_time(self) -> None:
        with pytest.raises(PydanticValidationError, match="must not record ended_at"):
            self._session(ended_at=NOW)

    def test_completed_session_cannot_hold_in_flight_action(self) -> None:
        action = ActionRecord(
            action_type=ActionType.TEACH,
            topic_id="polity.fundamental_rights",
            objective="Explain Article 21",
            status=ActionStatus.IN_PROGRESS,
        )
        with pytest.raises(PydanticValidationError, match="in-flight"):
            self._session(status=SessionStatus.COMPLETED, ended_at=NOW, current_action=action)

    def test_suspended_session_is_resumable(self) -> None:
        assert self._session(status=SessionStatus.SUSPENDED).status.is_resumable
        assert not SessionStatus.COMPLETED.is_resumable

    def test_remaining_minutes_never_negative(self) -> None:
        assert self._session(planned_minutes=60, elapsed_minutes=90).remaining_minutes == 0


class TestMemory:
    def test_derived_record_requires_sources(self) -> None:
        with pytest.raises(PydanticValidationError, match="derived_from"):
            MemoryRecord(
                memory_id="m1",
                student_id="stu_demo",
                kind=MemoryKind.SUMMARY,
                topic_id="polity",
                content="summary",
                source_event_id="ev1",
                recorded_at=NOW,
                confidence=0.8,
                derived=True,
            )

    def test_resolution_prefers_evidence_date(self) -> None:
        """C5 compares when a fact was observed, not when it was written."""
        observed = datetime(2026, 7, 1, tzinfo=UTC)
        record = MemoryRecord(
            memory_id="m1",
            student_id="stu_demo",
            kind=MemoryKind.FACT,
            topic_id="polity",
            content="x",
            source_event_id="ev1",
            recorded_at=NOW,
            evidence_at=observed,
            confidence=0.8,
        )
        assert record.resolution_timestamp == observed
