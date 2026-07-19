"""Validation failure types.

Validation failure is a first-class outcome with defined behaviour, not an exception path
(ADR-0003). These types carry machine-readable detail so the retry described in
`docs/09 Prompt Architecture.md` can supply the model with actionable errors.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One specific reason a candidate was rejected."""

    path: str
    """Dotted location within the instance, e.g. `tasks.0.minutes`."""

    message: str

    code: str = "invalid"
    """Stable machine-readable classifier, e.g. `schema`, `capacity`, `prerequisite`."""

    def __str__(self) -> str:
        return f"{self.path or '<root>'}: {self.message}"


class ValidationError(Exception):
    """Raised when a candidate fails validation and MUST NOT be persisted."""

    def __init__(self, contract: str, issues: list[ValidationIssue]) -> None:
        self.contract = contract
        self.issues = issues
        detail = "; ".join(str(i) for i in issues) or "no detail"
        super().__init__(f"{contract} failed validation: {detail}")

    def as_machine_readable(self) -> list[dict[str, str]]:
        """Errors in the form supplied to a retry."""
        return [{"path": i.path, "message": i.message, "code": i.code} for i in self.issues]


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Outcome of a validation pass.

    Callers that must not raise — a retry loop, a report — inspect this instead of catching.
    """

    contract: str
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.issues

    def raise_if_invalid(self) -> None:
        if self.issues:
            raise ValidationError(self.contract, self.issues)
