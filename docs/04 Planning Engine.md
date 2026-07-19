---
title: Planning Engine
document_id: DOC-04
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/01 Tutor Constitution.md
  - docs/05 Revision Engine.md
  - docs/07 Student Model.md
related_documents:
  - docs/03 Decision Engine.md
  - schemas/study_plan.json
  - workflows/weekly.md
  - workflows/monthly.md
---

# Planning Engine

## Responsibility

**The Planning Engine allocates accepted work across a horizon. It does not decide what work
is worth doing.**

It converts obligations — the due set, prerequisite gaps, deadlines — into a feasible,
capacity-bounded [`study_plan`](../schemas/study_plan.json). It is the only component that
may declare a plan feasible.

| Not owned by this engine | Owner |
| --- | --- |
| Choosing the next action in-session | [Decision Engine](03%20Decision%20Engine.md) |
| Computing which items are due | [Revision Engine](05%20Revision%20Engine.md) |
| Judging mastery | [Student Model](07%20Student%20Model.md) |

## Inputs

Availability and mastery from the Student Model; the **due set as a fixed reservation** from
the Revision Engine; deadlines; the active plan, if any; and accepted goals from the monthly
workflow. The engine consumes the due set — it MUST NOT recompute or reorder it.

## Output

A `study_plan` conforming to [`schemas/study_plan.json`](../schemas/study_plan.json), with
status `proposed`. A plan becomes `accepted` only on explicit student confirmation. At most
one `accepted` plan MAY exist per student and horizon; a replaced plan becomes `superseded`
and is never rewritten in place.

## Allocation rules

1. Reserve the due set before allocating any new coverage. Deferral is permitted only under
   [Constitution C1](01%20Tutor%20Constitution.md#5-conflict-resolution).
2. Schedule in estimated focused minutes, never in vague day labels.
3. Allocate no more than `planning.capacity_utilization_max` of declared availability without
   explicit confirmation. The remainder is recovery capacity and is not spare capacity.
4. No task SHALL be shorter than `planning.min_task_minutes`.
5. Decompose topics into tasks that each carry one observable objective and a declared
   `evidence_type`: `retrieval`, `practice`, `answer`, `review`, or `attendance`.
6. Block a task whose prerequisites are unsatisfied and schedule the prerequisite first. A
   blocked task is not a skipped task.
7. Re-plan the remaining horizon after a missed task. Completion SHALL NOT be inferred.
8. Within `exam.proximity_compression_days` of the exam, shift allocation toward retrieval
   and answer practice over new breadth.

## Horizon model

The monthly workflow sets capacity assumptions and measurable outcomes. The Planning Engine
produces a **weekly** plan with daily task instances. It SHALL NOT emit an unreviewable
month-long daily schedule. The daily workflow selects and adapts within the accepted plan; it
does not create plans.

See [`workflows/monthly.md`](../workflows/monthly.md) and [`workflows/weekly.md`](../workflows/weekly.md).

## Validation

A plan is rejected when it contains duplicate task IDs, a duration below
`planning.min_task_minutes`, unsatisfied prerequisites, a horizon mismatch, unreserved due
items, or scheduled minutes above capacity.

Rejections MUST be explained in user-facing terms and accompanied by the smallest feasible
adjustment that would make the plan valid.

## Failure cases

| Case | Required behaviour |
| --- | --- |
| Due set exceeds total capacity | Surface the overflow; propose reduced new coverage. MUST NOT silently drop due items. |
| Student declines the proposal | Retain the prior accepted plan; record the decline with its rationale ([C8](01%20Tutor%20Constitution.md#5-conflict-resolution)). |
| Availability changes mid-horizon | Re-plan remaining tasks only. Completed evidence is immutable. |
| Prerequisite cycle detected | Reject the plan and report the cycle. MUST NOT break it arbitrarily. |
| Capacity would be exceeded | Apply [C3](01%20Tutor%20Constitution.md#5-conflict-resolution): surface the trade-off and request confirmation. |
