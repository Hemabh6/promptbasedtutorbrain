"""Answer evaluation contract — mirror of `schemas/answer.json`.

Evidence, not state. The Evaluation Engine emits this record and candidates; mastery updates
and task creation belong to their owning components (Constitution C4).
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from tutorbrain.contracts.common import (
    SCHEMA_VERSION,
    AnswerId,
    Contract,
    RubricDimension,
    StudentId,
    TopicId,
)


class UnverifiedReason(StrEnum):
    NO_SOURCE = "no_source"
    CONFLICTING_SOURCE = "conflicting_source"
    OUTDATED = "outdated"
    UNCLEAR = "unclear"


class CandidateKind(StrEnum):
    PRACTICE = "practice"
    REVISION = "revision"
    TEACH = "teach"


class DimensionScore(Contract):
    """One scored dimension.

    `evidence` is non-empty by construction: a dimension without evidence invalidates the
    whole record (`docs/06 Evaluation Engine.md`).
    """

    name: RubricDimension
    score: int = Field(ge=0, le=5)
    evidence: list[str] = Field(min_length=1)
    improvement: str = Field(min_length=1)


class UnverifiedClaim(Contract):
    claim: str = Field(min_length=1)
    reason: UnverifiedReason | None = None


class FollowUpCandidate(Contract):
    kind: CandidateKind
    topic_id: TopicId
    rationale: str = Field(min_length=1)


class AnswerEvaluation(Contract):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    answer_id: AnswerId
    student_id: StudentId
    question: str = Field(min_length=1)
    answer_text: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    dimensions: list[DimensionScore] = Field(min_length=1)
    evaluated_at: datetime
    topic_id: TopicId | None = None
    command_word: str | None = Field(default=None, min_length=1)
    word_limit: int | None = Field(default=None, ge=1)
    prompt_version: str | None = Field(default=None, min_length=1)
    outline: list[str] = Field(default_factory=list)
    total_score: float | None = Field(default=None, ge=0)
    strengths: list[str] = Field(default_factory=list)
    omissions: list[str] = Field(default_factory=list)
    unverified_claims: list[UnverifiedClaim] = Field(default_factory=list)
    rewrite_plan: list[str] = Field(default_factory=list)
    candidates: list[FollowUpCandidate] = Field(default_factory=list)

    @model_validator(mode="after")
    def _no_duplicate_dimensions(self) -> AnswerEvaluation:
        names = [d.name for d in self.dimensions]
        if len(names) != len(set(names)):
            raise ValueError("duplicate rubric dimension in evaluation")
        return self

    @property
    def is_complete(self) -> bool:
        """True when all eight dimensions are scored and a total may be computed."""
        return {d.name for d in self.dimensions} == set(RubricDimension)

    def score_map(self) -> dict[RubricDimension, int]:
        return {d.name: d.score for d in self.dimensions}
