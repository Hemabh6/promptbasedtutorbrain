"""Validation boundary tests.

The critical property under test is drift: the Pydantic models and the published JSON Schemas
must agree. If they diverge, `schemas/` stops being the specification.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from tutorbrain.contracts import Event, EventKind, Student, Topic
from tutorbrain.seed import demo_rubric, demo_student, demo_topics
from tutorbrain.validation import CONTRACT_SCHEMAS, SchemaValidator, ValidationError


@pytest.fixture
def validator(schema_dir: Path) -> SchemaValidator:
    return SchemaValidator(schema_dir=schema_dir)


def test_every_registered_schema_file_exists(validator: SchemaValidator) -> None:
    for schema_file in CONTRACT_SCHEMAS.values():
        assert schema_file in validator.available_schemas


def test_all_nine_contracts_are_registered() -> None:
    assert len(CONTRACT_SCHEMAS) == 9


def test_seeded_student_satisfies_published_schema(validator: SchemaValidator) -> None:
    assert validator.validate(demo_student()).is_valid


def test_seeded_topics_satisfy_published_schema(validator: SchemaValidator) -> None:
    for topic in demo_topics():
        assert validator.validate(topic).is_valid, topic.topic_id


def test_seeded_rubric_satisfies_published_schema(validator: SchemaValidator) -> None:
    assert validator.validate(demo_rubric()).is_valid


def test_event_satisfies_published_schema(validator: SchemaValidator) -> None:
    event = Event(
        event_id="ev_1",
        student_id="stu_demo",
        kind=EventKind.SESSION_STARTED,
        occurred_at=datetime(2026, 7, 19, 10, 0, tzinfo=UTC),
        recorded_at=datetime(2026, 7, 19, 10, 0, tzinfo=UTC),
    )
    assert validator.validate(event).is_valid


def test_round_trip_preserves_contract(validator: SchemaValidator) -> None:
    """Serialise then parse must yield an equal object."""
    original = demo_student()
    restored = validator.parse(Student, validator.to_json_dict(original))
    assert restored == original


def test_invalid_instance_is_rejected_with_paths(validator: SchemaValidator) -> None:
    bad = {"schema_version": "1.0", "topic_id": "ok.id", "title": "T"}  # missing paper, weight
    result = validator.validate_instance(bad, "topic.json")
    assert not result.is_valid
    assert result.issues


def test_parse_rejects_undeclared_field(validator: SchemaValidator) -> None:
    data = validator.to_json_dict(demo_topics()[0]) | {"unexpected": True}
    with pytest.raises(ValidationError):
        validator.parse(Topic, data)


def test_parse_rejects_out_of_range_value(validator: SchemaValidator) -> None:
    data = validator.to_json_dict(demo_topics()[0]) | {"exam_weight": 4.2}
    with pytest.raises(ValidationError):
        validator.parse(Topic, data)


def test_validation_error_is_machine_readable(validator: SchemaValidator) -> None:
    """The retry path needs actionable errors, not a formatted string."""
    data = validator.to_json_dict(demo_topics()[0]) | {"exam_weight": 4.2}
    with pytest.raises(ValidationError) as exc:
        validator.parse(Topic, data)
    payload = exc.value.as_machine_readable()
    assert payload and all({"path", "message", "code"} <= item.keys() for item in payload)


def test_unregistered_contract_raises(validator: SchemaValidator) -> None:
    class Unregistered(Topic):
        pass

    with pytest.raises(KeyError):
        validator.validate(Unregistered(topic_id="a", title="A", paper="GS2", exam_weight=0.1))


def test_missing_schema_dir_fails_fast(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        SchemaValidator(schema_dir=tmp_path / "nope")
