"""Command-line entry point.

Milestone 1 exposes only what the foundation can honestly do: seed a data directory, inspect
validated state, and demonstrate that invalid state is rejected. Action selection arrives in
Milestone 2.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import fields
from pathlib import Path

from tutorbrain.runtime import build_context
from tutorbrain.seed import DEMO_STUDENT_ID, demo_rubric, demo_student, demo_topics
from tutorbrain.storage import NotFoundError
from tutorbrain.validation import ValidationError

DEFAULT_DATA_ROOT = Path("./.tutorbrain-data")


def _cmd_seed(args: argparse.Namespace) -> int:
    ctx = build_context(args.data_root)
    store = ctx.repositories

    if store.students.exists(DEMO_STUDENT_ID) and not args.force:
        print(f"Student {DEMO_STUDENT_ID!r} already exists. Use --force to overwrite.")
        return 1

    # Seeding is an administrative operation: the read-only ports cannot rewrite the
    # syllabus, so this goes through the backend explicitly.
    ctx.store.replace_topics(demo_topics())
    ctx.store.replace_rubrics([demo_rubric()])

    student = demo_student()
    if store.students.exists(DEMO_STUDENT_ID):
        student = student.model_copy(
            update={"profile_version": store.students.get(DEMO_STUDENT_ID).profile_version}
        )
    stored = store.students.save(student)

    print(f"Seeded {args.data_root}")
    print(f"  topics    {len(demo_topics())}")
    print(f"  rubrics   1 (version {demo_rubric().rubric_version})")
    print(f"  student   {stored.student_id} (profile_version {stored.profile_version})")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    ctx = build_context(args.data_root)
    store = ctx.repositories
    try:
        student = store.students.get(args.student_id)
    except NotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print("hint: run `tutorbrain seed` first", file=sys.stderr)
        return 1

    policy = ctx.policy
    ec = student.exam_context
    av = student.availability

    print(f"Student        {student.student_id}  (profile_version {student.profile_version})")
    print(f"Exam           {ec.exam} {ec.target_year} — {ec.stage.value}")
    if ec.optional_subject:
        print(f"Optional       {ec.optional_subject}")
    print(f"Timezone       {av.timezone}")
    print(
        f"Availability   {av.weekly_minutes} min/week declared, "
        f"{policy.usable_capacity(av.weekly_minutes)} usable "
        f"(reserve {policy.recovery_reserve:.0%})"
    )

    print("\nTopic mastery")
    if not student.topic_mastery:
        print("  (no evidence recorded)")
    for m in student.topic_mastery:
        if policy.is_strong(m.mastery):
            band = "strong"
        elif policy.is_weak(m.mastery):
            band = "weak"
        else:
            band = "developing"
        line = f"  {m.topic_id:<34} {m.mastery:.2f}  {band:<10} ({m.evidence_count} evidence)"
        if (err := m.calibration_error) is not None:
            direction = "over" if err > 0 else "under"
            line += f"  [{direction}confident by {abs(err):.2f}]"
        print(line)

    topics = store.topics.all()
    print(f"\nSyllabus catalogue: {len(topics)} topics")
    for t in topics:
        prereq = f"  requires {', '.join(t.prerequisites)}" if t.prerequisites else ""
        print(f"  {t.topic_id:<34} weight {t.exam_weight:.2f}{prereq}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Re-validate everything on disk against the published schemas.

    Reading through the store parses every record, so a drift between stored data and
    `schemas/` surfaces here rather than mid-session.
    """
    ctx = build_context(args.data_root)
    store = ctx.repositories
    checked = 0
    try:
        for sid in [args.student_id]:
            student = store.students.get(sid)
            ctx.validator.validate(student).raise_if_invalid()
            checked += 1
            for collection in (
                store.memory.list_for_student(sid),
                store.revisions.list_for_student(sid),
                store.plans.list_for_student(sid),
                store.sessions.list_for_student(sid),
                store.answers.list_for_student(sid),
                store.events.list_for_student(sid),
            ):
                checked += len(collection)
        checked += len(store.topics.all())
    except (ValidationError, NotFoundError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    print(f"OK — {checked} records validate against schemas/ and the typed contracts.")
    return 0


def _cmd_policy(args: argparse.Namespace) -> int:
    """Print the active Constitution §9 parameters."""
    ctx = build_context(args.data_root)
    print("Policy parameters (Constitution §9)")
    for f in sorted(fields(ctx.policy), key=lambda f: f.name):
        print(f"  {f.name:<42} {getattr(ctx.policy, f.name)}")
    print(f"  {'recovery_reserve (derived)':<42} {ctx.policy.recovery_reserve:.2f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tutorbrain",
        description="Prompt-Based Tutor Brain — reference implementation (Phase 2, Milestone 1)",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_DATA_ROOT,
        help=f"state directory (default: {DEFAULT_DATA_ROOT})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    seed = sub.add_parser("seed", help="create demonstration state")
    seed.add_argument("--force", action="store_true", help="overwrite an existing student")
    seed.set_defaults(func=_cmd_seed)

    show = sub.add_parser("show", help="display validated student state")
    show.add_argument("--student-id", default=DEMO_STUDENT_ID)
    show.set_defaults(func=_cmd_show)

    validate = sub.add_parser("validate", help="re-validate all stored state")
    validate.add_argument("--student-id", default=DEMO_STUDENT_ID)
    validate.set_defaults(func=_cmd_validate)

    policy = sub.add_parser("policy", help="print active policy parameters")
    policy.set_defaults(func=_cmd_policy)

    return parser


def _force_utf8_output() -> None:
    """Render non-ASCII output correctly on consoles defaulting to a legacy code page.

    Windows terminals commonly default to cp1252, which mangles the section signs and dashes
    used in specification references. Reconfiguring is preferred to degrading the text.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main(argv: Sequence[str] | None = None) -> int:
    _force_utf8_output()
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ValidationError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
