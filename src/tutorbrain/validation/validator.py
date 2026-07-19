"""Schema validation — the ADR-0003 gate.

Every runtime object crosses this boundary before persistence. Validation is two-layered
because the two layers catch different failures:

* **Typed layer** (Pydantic) — the in-process contract. Catches shape errors at construction.
* **Published layer** (JSON Schema) — the contract other implementations code against.
  Catches drift between the Python models and `schemas/`.

Passing only the typed layer would let the models silently diverge from the published
schemas, which are the actual specification.
"""

from __future__ import annotations

import json
from functools import cached_property
from pathlib import Path
from typing import Any, TypeVar

from jsonschema import Draft202012Validator
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from tutorbrain.contracts import (
    AnswerEvaluation,
    Contract,
    Event,
    MemoryRecord,
    RevisionRecord,
    Rubric,
    Student,
    StudyPlan,
    StudySession,
    Topic,
)
from tutorbrain.validation.errors import ValidationError, ValidationIssue, ValidationResult

C = TypeVar("C", bound=Contract)

CONTRACT_SCHEMAS: dict[type[Contract], str] = {
    Student: "student.json",
    MemoryRecord: "memory.json",
    Event: "event.json",
    RevisionRecord: "revision.json",
    StudyPlan: "study_plan.json",
    StudySession: "session.json",
    AnswerEvaluation: "answer.json",
    Rubric: "rubric.json",
    Topic: "topic.json",
}
"""Which published schema governs each typed contract."""


def _default_schema_dir() -> Path:
    """Locate `schemas/` relative to the installed package.

    src/tutorbrain/validation/validator.py -> repository root -> schemas/
    """
    return Path(__file__).resolve().parents[3] / "schemas"


class SchemaValidator:
    """Validates runtime objects against both contract layers.

    Schemas are read once and cached; a long-lived runtime should hold one instance.
    """

    def __init__(self, schema_dir: Path | None = None) -> None:
        self._schema_dir = schema_dir or _default_schema_dir()
        if not self._schema_dir.is_dir():
            raise FileNotFoundError(f"schema directory not found: {self._schema_dir}")
        self._validators: dict[str, Draft202012Validator] = {}

    @cached_property
    def available_schemas(self) -> tuple[str, ...]:
        return tuple(sorted(p.name for p in self._schema_dir.glob("*.json")))

    def _validator_for(self, schema_file: str) -> Draft202012Validator:
        if schema_file not in self._validators:
            path = self._schema_dir / schema_file
            if not path.is_file():
                raise FileNotFoundError(f"schema not found: {path}")
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            self._validators[schema_file] = Draft202012Validator(schema)
        return self._validators[schema_file]

    def validate_instance(self, instance: dict[str, Any], schema_file: str) -> ValidationResult:
        """Validate raw JSON data against a published schema."""
        issues = [
            ValidationIssue(
                path=".".join(str(p) for p in error.absolute_path),
                message=error.message,
                code="schema",
            )
            for error in sorted(
                self._validator_for(schema_file).iter_errors(instance),
                key=lambda e: list(e.absolute_path),
            )
        ]
        return ValidationResult(contract=schema_file, issues=issues)

    def validate(self, obj: Contract) -> ValidationResult:
        """Validate a typed contract against its published schema.

        The object already satisfies the typed layer by virtue of existing. This confirms the
        published layer agrees.
        """
        schema_file = CONTRACT_SCHEMAS.get(type(obj))
        if schema_file is None:
            raise KeyError(f"no published schema registered for {type(obj).__name__}")
        return self.validate_instance(self.to_json_dict(obj), schema_file)

    def parse(self, model: type[C], data: dict[str, Any]) -> C:
        """Build a typed contract from raw data, checking both layers.

        Raises `ValidationError` on failure. This is the only sanctioned way to admit
        externally sourced data — a model candidate, a stored file — into the runtime.
        """
        schema_file = CONTRACT_SCHEMAS.get(model)
        if schema_file is not None:
            self.validate_instance(data, schema_file).raise_if_invalid()
        try:
            return model.model_validate(data)
        except PydanticValidationError as exc:
            issues = [
                ValidationIssue(
                    path=".".join(str(p) for p in err["loc"]),
                    message=err["msg"],
                    code=str(err["type"]),
                )
                for err in exc.errors()
            ]
            raise ValidationError(model.__name__, issues) from exc

    @staticmethod
    def to_json_dict(obj: BaseModel) -> dict[str, Any]:
        """Serialise a contract to JSON-compatible data.

        `mode="json"` renders dates, datetimes, and enums as the strings the published
        schemas declare. `exclude_none` keeps optional absent fields out of the payload
        rather than emitting explicit nulls, which `additionalProperties: false` schemas
        with typed fields would reject.
        """
        return obj.model_dump(mode="json", exclude_none=True)
