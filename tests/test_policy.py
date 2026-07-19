"""Policy parameters must match Constitution §9 exactly.

This test is the mechanism that makes §9 the single source of threshold: if a default drifts
from the specification, this fails.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tutorbrain.config import DEFAULT_POLICY, PolicyParameters

CONSTITUTION = Path(__file__).resolve().parents[1] / "docs" / "01 Tutor Constitution.md"

# The §9 table, transcribed. Kept literal so a spec change must be made deliberately here.
EXPECTED = {
    "revision.backlog_threshold": "5",
    "revision.default_intervals": "1, 3, 7, 14, 30",
    "revision.max_defer_days": "2",
    "planning.capacity_utilization_max": "0.85",
    "planning.min_task_minutes": "15",
    "student.mastery_weak_threshold": "0.40",
    "student.mastery_strong_threshold": "0.75",
    "memory.min_confidence_durable": "0.60",
    "evaluation.rubric_version": "1.0",
    "prompt.validation_retry_max": "1",
    "exam.proximity_compression_days": "60",
}


def _parse_section_9() -> dict[str, str]:
    """Extract the parameter table from the Constitution."""
    text = CONSTITUTION.read_text(encoding="utf-8")
    section = text.split("## 9. Policy Parameters")[1].split("## 10.")[0]
    found = {}
    for line in section.splitlines():
        if m := re.match(r"\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|", line):
            value = m.group(2).strip("`").replace(" days", "").replace(" due items", "")
            found[m.group(1)] = value
    return found


def test_constitution_section_9_is_parseable() -> None:
    assert _parse_section_9() == EXPECTED


@pytest.mark.parametrize(
    ("spec_name", "attribute"),
    [
        ("revision.backlog_threshold", "revision_backlog_threshold"),
        ("revision.max_defer_days", "revision_max_defer_days"),
        ("planning.capacity_utilization_max", "planning_capacity_utilization_max"),
        ("planning.min_task_minutes", "planning_min_task_minutes"),
        ("student.mastery_weak_threshold", "student_mastery_weak_threshold"),
        ("student.mastery_strong_threshold", "student_mastery_strong_threshold"),
        ("memory.min_confidence_durable", "memory_min_confidence_durable"),
        ("prompt.validation_retry_max", "prompt_validation_retry_max"),
        ("exam.proximity_compression_days", "exam_proximity_compression_days"),
    ],
)
def test_default_matches_constitution(spec_name: str, attribute: str) -> None:
    assert float(EXPECTED[spec_name]) == float(getattr(DEFAULT_POLICY, attribute))


def test_default_intervals_match_constitution() -> None:
    expected = tuple(int(x) for x in EXPECTED["revision.default_intervals"].split(", "))
    assert DEFAULT_POLICY.revision_default_intervals == expected


def test_recovery_reserve_complements_utilisation_ceiling() -> None:
    assert DEFAULT_POLICY.recovery_reserve == pytest.approx(0.15)


def test_usable_capacity_applies_ceiling() -> None:
    assert DEFAULT_POLICY.usable_capacity(1000) == 850


def test_mastery_bands() -> None:
    assert DEFAULT_POLICY.is_weak(0.39)
    assert not DEFAULT_POLICY.is_weak(0.40)
    assert DEFAULT_POLICY.is_strong(0.75)
    assert not DEFAULT_POLICY.is_strong(0.74)


def test_interval_ladder_advances_then_doubles() -> None:
    assert DEFAULT_POLICY.next_interval_after(1) == 3
    assert DEFAULT_POLICY.next_interval_after(14) == 30
    assert DEFAULT_POLICY.next_interval_after(30) == 60


@pytest.mark.parametrize(
    "kwargs",
    [
        {"planning_capacity_utilization_max": 1.5},
        {"student_mastery_weak_threshold": 0.9},  # weak >= strong
        {"revision_default_intervals": (7, 3)},  # not increasing
        {"revision_default_intervals": ()},
        {"planning_min_task_minutes": 0},
        {"memory_min_confidence_durable": 1.4},
    ],
)
def test_invalid_policy_is_rejected(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        PolicyParameters(**kwargs)  # type: ignore[arg-type]


def test_unknown_key_in_policy_file_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "policy.json"
    path.write_text('{"revision_backlog_thresold": 9}', encoding="utf-8")
    with pytest.raises(ValueError, match="unknown policy parameters"):
        PolicyParameters.from_file(path)
