from __future__ import annotations

from pathlib import Path

import pytest

from tutorbrain.runtime import TutorContext, build_context
from tutorbrain.seed import demo_rubric, demo_student, demo_topics

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"


@pytest.fixture
def schema_dir() -> Path:
    return SCHEMA_DIR


@pytest.fixture
def context(tmp_path: Path) -> TutorContext:
    """A runtime wired to an isolated temporary data directory."""
    return build_context(tmp_path / "data", schema_dir=SCHEMA_DIR)


@pytest.fixture
def seeded(context: TutorContext) -> TutorContext:
    context.store.replace_topics(demo_topics())
    context.store.replace_rubrics([demo_rubric()])
    context.repositories.students.save(demo_student())
    return context
