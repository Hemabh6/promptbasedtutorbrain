"""Demonstration seed data.

A minimal syllabus slice and one student, sufficient to exercise the Definition of Done
scenario ("Teach me Fundamental Rights") end to end. This is sample data, not a syllabus
import: ADR-0005 records that a real import path is still needed.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from tutorbrain.contracts import (
    Availability,
    ExamContext,
    ExamStage,
    LearningStyle,
    Rubric,
    Student,
    Topic,
    TopicMastery,
)

DEMO_STUDENT_ID = "stu_demo"


def demo_topics() -> list[Topic]:
    """A GS2 polity slice with a real prerequisite chain.

    `fundamental_rights` depends on `constitution_basics`, so the Definition of Done scenario
    exercises prerequisite handling rather than a flat lookup.
    """
    return [
        Topic(
            topic_id="polity",
            title="Indian Polity and Governance",
            paper="GS2",
            exam_weight=0.9,
            typical_minutes=60,
        ),
        Topic(
            topic_id="polity.constitution_basics",
            title="Constitutional Framework",
            aliases=["Constitution basics", "Constitutional framework"],
            paper="GS2",
            parent_topic_id="polity",
            exam_weight=0.7,
            baseline_effort_cost=0.4,
            typical_minutes=45,
            command_words=["explain", "describe"],
        ),
        Topic(
            topic_id="polity.fundamental_rights",
            title="Fundamental Rights",
            aliases=[
                "Fundamental Rights",
                "FR",
                "Part III",
                "rights",
            ],
            paper="GS2",
            parent_topic_id="polity",
            exam_weight=0.85,
            baseline_effort_cost=0.55,
            prerequisites=["polity.constitution_basics"],
            typical_minutes=50,
            command_words=["examine", "critically examine", "discuss"],
        ),
        Topic(
            topic_id="polity.dpsp",
            title="Directive Principles of State Policy",
            aliases=["DPSP", "Directive Principles"],
            paper="GS2",
            parent_topic_id="polity",
            exam_weight=0.6,
            baseline_effort_cost=0.5,
            prerequisites=["polity.constitution_basics"],
            typical_minutes=40,
            command_words=["discuss", "compare"],
        ),
        Topic(
            topic_id="polity.basic_structure",
            title="Basic Structure Doctrine",
            aliases=["Basic structure", "Kesavananda"],
            paper="GS2",
            parent_topic_id="polity",
            exam_weight=0.8,
            baseline_effort_cost=0.7,
            prerequisites=["polity.fundamental_rights"],
            typical_minutes=45,
            command_words=["critically examine", "analyse"],
        ),
    ]


def demo_student() -> Student:
    """A working professional with uneven weekday availability.

    `constitution_basics` carries partial mastery and `fundamental_rights` none, so the
    prerequisite for the demo request is satisfied but the target topic is genuinely unseen.
    """
    return Student(
        student_id=DEMO_STUDENT_ID,
        profile_version=1,
        exam_context=ExamContext(
            exam="UPSC Civil Services",
            target_year=2027,
            stage=ExamStage.PRELIMS,
            attempt_number=1,
            optional_subject="Public Administration",
            exam_date=date(2027, 6, 6),
        ),
        availability=Availability(
            timezone="Asia/Kolkata",
            minutes_by_day={
                "mon": 90,
                "tue": 90,
                "wed": 90,
                "thu": 90,
                "fri": 60,
                "sat": 240,
                "sun": 240,
            },
            working_professional=True,
        ),
        topic_mastery=[
            TopicMastery(
                topic_id="polity.constitution_basics",
                mastery=0.62,
                self_reported_confidence=0.8,
                evidence_count=4,
                updated_at=datetime(2026, 7, 15, 19, 30, tzinfo=UTC),
            ),
        ],
        learning_style=LearningStyle(
            preferred_modality="example",
            pacing="moderate",
            feedback_tone="direct",
            example_density="medium",
        ),
        current_focus="polity",
    )


def demo_rubric() -> Rubric:
    """The default uniform rubric. Calibration is deferred to Phase 6 (ADR-0005)."""
    return Rubric.uniform(rubric_version="1.0")
