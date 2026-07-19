"""Syllabus topic contract — mirror of `schemas/topic.json`.

Static syllabus reference, not learner state. Added by ADR-0005 as the referent of every
`topic_id` and the source of `exam_weight` for Decision Engine scoring.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import Field, field_validator

from tutorbrain.contracts.common import SCHEMA_VERSION, Contract, TopicId, UnitInterval

TOPIC_ID_PATTERN = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")


class Topic(Contract):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    topic_id: TopicId
    title: str = Field(min_length=1)
    paper: str = Field(min_length=1)
    exam_weight: UnitInterval
    aliases: list[str] = Field(default_factory=list)
    parent_topic_id: TopicId | None = None
    baseline_effort_cost: UnitInterval = 0.5
    prerequisites: list[TopicId] = Field(default_factory=list)
    typical_minutes: int | None = Field(default=None, ge=1)
    command_words: list[str] = Field(default_factory=list)

    @field_validator("topic_id", "parent_topic_id")
    @classmethod
    def _well_formed_id(cls, v: str | None) -> str | None:
        if v is not None and not TOPIC_ID_PATTERN.match(v):
            raise ValueError(f"malformed topic_id: {v!r}")
        return v

    @field_validator("prerequisites")
    @classmethod
    def _no_self_prerequisite(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("duplicate prerequisite")
        return v

    @property
    def match_terms(self) -> set[str]:
        """Normalised forms this topic answers to, for deterministic resolution."""
        return {t.strip().casefold() for t in [self.title, *self.aliases, self.topic_id]}
