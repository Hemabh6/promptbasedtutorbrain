"""Memory record contract — mirror of `schemas/memory.json`.

Authoritative for evidence. Immutable once written: contradictions coexist and are resolved
at retrieval time under Constitution C5, never by overwriting.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from tutorbrain.contracts.common import (
    SCHEMA_VERSION,
    Contract,
    EventId,
    MemoryId,
    StudentId,
    TopicId,
    UnitInterval,
)


class MemoryKind(StrEnum):
    FACT = "fact"
    MISCONCEPTION = "misconception"
    PREFERENCE = "preference"
    STRATEGY = "strategy"
    SUMMARY = "summary"


class MemoryLayer(StrEnum):
    PROFILE = "profile"
    LEDGER = "ledger"
    INDEX = "index"


class TrustTier(StrEnum):
    OFFICIAL = "official"
    ESTABLISHED = "established"
    SECONDARY = "secondary"
    UNVERIFIED = "unverified"


class Provenance(Contract):
    """Source metadata.

    Required for externally sourced and current-affairs claims; without it a claim is
    ineligible for durable memory (Constitution §2 rule 2).
    """

    source_url: str = Field(min_length=1)
    published_at: datetime
    accessed_at: datetime
    publisher: str | None = Field(default=None, min_length=1)
    trust_tier: TrustTier | None = None


class MemoryRecord(Contract):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    memory_id: MemoryId
    student_id: StudentId
    kind: MemoryKind
    topic_id: TopicId
    content: str = Field(min_length=1)
    source_event_id: EventId
    recorded_at: datetime
    confidence: UnitInterval
    layer: MemoryLayer | None = None
    derived: bool = False
    derived_from: list[MemoryId] = Field(default_factory=list)
    evidence_at: datetime | None = None
    provenance: Provenance | None = None
    contradicts: list[MemoryId] = Field(default_factory=list)
    superseded_by: MemoryId | None = None

    @model_validator(mode="after")
    def _derived_requires_sources(self) -> MemoryRecord:
        if self.derived and not self.derived_from:
            raise ValueError("derived record must declare derived_from")
        return self

    @property
    def resolution_timestamp(self) -> datetime:
        """The date C5 compares when resolving contradictions.

        Evidence date wins over record date: when a fact was *observed* determines
        precedence, not when it happened to be written.
        """
        return self.evidence_at or self.recorded_at
