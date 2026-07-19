"""Evaluation rubric contract — mirror of `schemas/rubric.json`.

Holds weights only. Dimension scores live in `schemas/answer.json`. The model never sees or
applies these weights: the total is computed by application code
(`docs/06 Evaluation Engine.md`).
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from tutorbrain.contracts.common import SCHEMA_VERSION, Contract, RubricDimension

WEIGHT_SUM_TOLERANCE = 1e-6


class RubricDimensionWeight(Contract):
    name: RubricDimension
    weight: float = Field(gt=0, le=1)
    descriptor: str | None = Field(default=None, min_length=1)


class Rubric(Contract):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    rubric_version: str = Field(min_length=1)
    max_dimension_score: Literal[5] = 5
    total_scale: float = Field(default=100.0, gt=0)
    dimensions: list[RubricDimensionWeight] = Field(min_length=1)

    @model_validator(mode="after")
    def _weights_complete_and_normalised(self) -> Rubric:
        names = [d.name for d in self.dimensions]
        if len(names) != len(set(names)):
            raise ValueError("duplicate rubric dimension")
        if missing := set(RubricDimension) - set(names):
            raise ValueError(f"rubric must cover all eight dimensions; missing {sorted(missing)}")
        total = sum(d.weight for d in self.dimensions)
        if abs(total - 1.0) > WEIGHT_SUM_TOLERANCE:
            raise ValueError(f"dimension weights must sum to 1.0, got {total}")
        return self

    def weight_for(self, dimension: RubricDimension) -> float:
        return next(d.weight for d in self.dimensions if d.name == dimension)

    def compute_total(self, scores: dict[RubricDimension, int]) -> float:
        """Weighted total on `total_scale`.

        This is the arithmetic the Constitution reserves to application code (C7). A
        model-supplied total is discarded rather than reconciled.
        """
        if missing := set(RubricDimension) - scores.keys():
            raise ValueError(f"cannot total a partial evaluation; missing {sorted(missing)}")
        if bad := {d: s for d, s in scores.items() if not 0 <= s <= self.max_dimension_score}:
            raise ValueError(f"scores outside 0-{self.max_dimension_score}: {bad}")
        fraction = sum(
            self.weight_for(dim) * (score / self.max_dimension_score)
            for dim, score in scores.items()
        )
        return round(fraction * self.total_scale, 2)

    @classmethod
    def uniform(cls, rubric_version: str = "1.0") -> Rubric:
        """The default rubric: eight equally weighted dimensions.

        Uniform weighting is a starting point, not a claim about relative importance. ADR-0005
        records that calibration is deferred to Phase 6.
        """
        weight = 1.0 / len(RubricDimension)
        return cls(
            rubric_version=rubric_version,
            dimensions=[RubricDimensionWeight(name=d, weight=weight) for d in RubricDimension],
        )
