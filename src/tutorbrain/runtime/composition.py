"""Composition root.

The single place where concrete implementations are chosen and wired. Every other module
receives its collaborators through its constructor and names only ports, so swapping the
storage backend or the reasoning adapter is a change here and nowhere else.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tutorbrain.config import DEFAULT_POLICY, PolicyParameters
from tutorbrain.storage import JsonFileStore, Repositories
from tutorbrain.validation import SchemaValidator


@dataclass(frozen=True, slots=True)
class TutorContext:
    """Assembled dependencies for one runtime.

    Held together so callers pass one object rather than five, while each component still
    receives only the narrow port it needs.
    """

    policy: PolicyParameters
    validator: SchemaValidator
    repositories: Repositories
    data_root: Path

    store: JsonFileStore
    """The raw backend, for administrative operations only.

    Seeding the syllabus catalogue is not a runtime capability: the `TopicCatalogue` port is
    deliberately read-only so no engine can rewrite the syllabus mid-session. Administrative
    tools reach the backend here, explicitly and visibly.
    """


def build_context(
    data_root: Path,
    *,
    policy: PolicyParameters | None = None,
    schema_dir: Path | None = None,
) -> TutorContext:
    """Wire a runtime against a data directory.

    `policy` and `schema_dir` are injectable so tests can run against fixtures and alternative
    thresholds without touching global state.
    """
    validator = SchemaValidator(schema_dir=schema_dir)
    store = JsonFileStore(root=data_root, validator=validator)
    return TutorContext(
        policy=policy or DEFAULT_POLICY,
        validator=validator,
        repositories=Repositories(store),
        data_root=data_root,
        store=store,
    )
