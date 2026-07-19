---
title: Scheduler Prompt Contract
document_id: PROMPT-SCHEDULER
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/09 Prompt Architecture.md
  - docs/04 Planning Engine.md
related_documents:
  - prompts/planner.md
  - schemas/study_plan.json
---

# Scheduler

## Purpose

Resolve placement conflicts among already-accepted work. Serves the `reschedule` action type.

This contract orders work; it never decides what work exists. Where
[`planner.md`](planner.md) produces a plan, this contract repairs one whose placement has
become infeasible.

## Inputs

| Field | Source | Required | Notes |
| --- | --- | --- | --- |
| `tasks` | [`study_plan.json`](../schemas/study_plan.json) | Yes | Accepted tasks only |
| `available_slots` | `student.availability` | Yes | Minutes by day, timezone-resolved |
| `fixed_commitments` | Student | No | Immovable blocks |
| `due_set` | Revision Engine | Yes | Highest placement priority |
| `deadlines` | Orchestrator | No | Mocks, tests, exam dates |
| `blackout_dates` | `student.availability` | No | Unavailable entirely |

## Outputs

```json
{
  "ordered_schedule": [
    { "task_id": "string", "scheduled_for": "date", "slot_minutes": 0 }
  ],
  "deferred_tasks": [{ "task_id": "string", "reason": "string" }],
  "conflicts": [{ "kind": "capacity|deadline|revision_overflow", "description": "string" }],
  "rationale_by_task_id": { "task_id": "string" }
}
```

## Constraints

- MUST place every `due_set` task before any non-revision task.
- MUST preserve the priority order established by the accepted plan where feasible.
- MUST leave the recovery reserve unallocated.
- MUST NOT schedule into `blackout_dates` or over `fixed_commitments`.
- MUST NOT alter task objectives, durations, goals, or task existence.
- MUST NOT create, merge, or delete tasks.
- MUST NOT claim access to a calendar that was not supplied.
- MUST surface every unavoidable trade-off rather than resolving it silently.

## Failure Cases

| Case | Required behaviour |
| --- | --- |
| No feasible arrangement exists | Return the best partial schedule plus `deferred_tasks`. MUST NOT drop tasks silently. |
| A deadline cannot be met | Emit a `deadline` conflict; MUST NOT shorten task durations to fit. |
| `due_set` exceeds all available slots | Emit `revision_overflow`; defer non-revision work first. |
| A fixed commitment consumes an entire day | Redistribute; MUST NOT exceed capacity on adjacent days without a conflict entry. |
| Timezone or DST ambiguity | Resolve in the student's declared timezone; record the assumption. |

## Dependencies

Invoked by the [Planning Engine](../docs/04%20Planning%20Engine.md), which performs the final
feasibility validation and obtains confirmation for material changes. Consumes the due set
from the [Revision Engine](../docs/05%20Revision%20Engine.md).

## Examples

**Input (abbreviated)**

```json
{ "tasks": [{ "task_id": "t7", "minutes": 60 }, { "task_id": "t8", "minutes": 15 }],
  "available_slots": { "2026-07-21": 45 },
  "due_set": ["t8"], "blackout_dates": ["2026-07-22"] }
```

**Output (abbreviated)**

```json
{ "ordered_schedule": [{ "task_id": "t8", "scheduled_for": "2026-07-21", "slot_minutes": 15 }],
  "deferred_tasks": [{ "task_id": "t7", "reason": "60 min required, 30 min remaining after due reservation" }],
  "conflicts": [{ "kind": "capacity", "description": "One coverage task deferred; 2026-07-22 unavailable." }],
  "rationale_by_task_id": { "t8": "Due revision reserved before coverage." } }
```

## Quality Criteria

1. Every input task appears exactly once in `ordered_schedule` or `deferred_tasks`.
2. No `due_set` task appears in `deferred_tasks` while a non-revision task is scheduled.
3. Scheduled minutes per day never exceed that day's `available_slots`.
4. Every deferral carries a reason and a matching conflict entry where capacity-driven.

## Version

1.0.0 — Accepted — 2026-07-19.
