---
title: Planner Prompt Contract
document_id: PROMPT-PLANNER
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/09 Prompt Architecture.md
  - docs/04 Planning Engine.md
related_documents:
  - schemas/study_plan.json
  - prompts/scheduler.md
  - workflows/weekly.md
---

# Planner

## Purpose

Propose a feasible, student-confirmable weekly plan from declared capacity and existing
obligations. Serves the `plan` action type.

## Inputs

| Field | Source | Required | Notes |
| --- | --- | --- | --- |
| `student` | [`student.json`](../schemas/student.json) | Yes | Availability, mastery, constraints |
| `due_set` | [Revision Engine](../docs/05%20Revision%20Engine.md) | Yes | Consumed as a fixed reservation |
| `active_plan` | [`study_plan.json`](../schemas/study_plan.json) | No | Present when re-planning |
| `horizon_start`, `horizon_end` | Planning Engine | Yes | One week |
| `capacity_minutes` | Planning Engine | Yes | Already net of recovery reserve |
| `monthly_outcomes` | [`workflows/monthly.md`](../workflows/monthly.md) | Yes | Accepted goals |
| `deadlines` | Orchestrator | No | Mocks, tests, exam dates |

## Outputs

A candidate conforming to [`study_plan.json`](../schemas/study_plan.json) with
`status: "proposed"`, plus `assumptions` and `conflicts` arrays.

`rationale` MAY be returned as audit metadata. It is stripped before persistence and never
becomes part of the plan record.

## Constraints

- MUST reserve every `due_set` item before allocating new coverage.
- MUST set `source: "revision_due"` and `revision_id` on each reserved task.
- MUST NOT exceed `planning.capacity_utilization_max` of `capacity_minutes`.
- MUST NOT emit a task shorter than `planning.min_task_minutes`.
- MUST express every objective as one observable outcome, never a topic label.
- MUST mark a task with unsatisfied prerequisites as `blocked`, not `skipped`.
- MUST record every bounded assumption in `assumptions`.
- MUST NOT mark unfinished work complete, reorder the due set, or compute revision intervals.
- MUST NOT emit a plan longer than one week.

## Failure Cases

| Case | Required behaviour |
| --- | --- |
| `due_set` alone exceeds capacity | Emit a `revision_overflow` conflict; allocate zero new coverage. MUST NOT drop due items. |
| Prerequisite cycle among tasks | Return no plan; emit a `prerequisite` conflict naming the cycle. |
| `capacity_minutes` is zero | Return an empty task list with an explanatory conflict, not a minimal plan. |
| Deadline unreachable within the horizon | Emit a `deadline` conflict; MUST NOT silently compress task durations. |
| Missing availability data | Apply a bounded assumption and record it; MUST NOT infer from past behaviour. |

## Dependencies

Invoked by the [Planning Engine](../docs/04%20Planning%20Engine.md), which validates capacity
and feasibility and requests student acceptance. Conflict resolution between competing
placements is delegated to [`scheduler.md`](scheduler.md). Consumes the due set from the
[Revision Engine](../docs/05%20Revision%20Engine.md).

## Examples

**Input (abbreviated)**

```json
{ "horizon_start": "2026-07-20", "horizon_end": "2026-07-26",
  "capacity_minutes": 1200, "due_set": [{ "revision_id": "rev_44", "topic_id": "econ.inflation", "minutes": 15 }],
  "monthly_outcomes": ["Complete GS3 economy fundamentals"] }
```

**Output (abbreviated)**

```json
{ "schema_version": "1.0", "plan_id": "plan_112", "status": "proposed",
  "capacity_minutes": 1200, "reserved_revision_minutes": 15,
  "tasks": [
    { "task_id": "t1", "topic_id": "econ.inflation", "objective": "Recall the CPI vs WPI distinction",
      "scheduled_for": "2026-07-20", "minutes": 15, "evidence_type": "review",
      "status": "planned", "source": "revision_due", "revision_id": "rev_44" }
  ],
  "assumptions": ["Assumed Sunday availability unchanged from prior week"], "conflicts": [] }
```

## Quality Criteria

1. Sum of task minutes ≤ `planning.capacity_utilization_max` × `capacity_minutes`.
2. Every `due_set` item appears exactly once as a `revision_due` task.
3. Every task ID is unique and every prerequisite resolves to a task or a satisfied mastery.
4. The output validates against [`study_plan.json`](../schemas/study_plan.json).

## Version

1.0.0 — Accepted — 2026-07-19.
