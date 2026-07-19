---
title: Weekly Workflow
document_id: WF-WEEKLY
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/04 Planning Engine.md
related_documents:
  - workflows/monthly.md
  - workflows/daily.md
  - prompts/planner.md
---

# Weekly Workflow

**Trigger:** a weekly planning boundary, or an explicit student request.

**Owner:** [Planning Engine](../docs/04%20Planning%20Engine.md), sequenced by the Orchestrator.

## Sequence

1. Aggregate the prior week: planned versus completed minutes, evidence produced, overdue
   revisions, and upcoming deadlines.
2. Run [`mentor.md`](../prompts/mentor.md) to identify one evidence-based adjustment.
3. Run the Planning Engine with availability, recovery capacity, the due set, and accepted
   monthly goals.
4. Validate the proposed [`study_plan`](../schemas/study_plan.json): capacity, task identity,
   dates, prerequisites, and due-set reservation.
5. Present trade-offs and obtain explicit acceptance before setting status to `accepted`.

## Rules

- The due set is reserved before any new coverage is allocated
  ([Constitution C1](../docs/01%20Tutor%20Constitution.md#5-conflict-resolution)).
- A capacity conflict MUST be surfaced with the smallest feasible adjustment, never resolved
  silently (C3).
- A declined proposal retains the prior accepted plan and records the decline with its
  rationale (C8).
- The mentor adjustment in step 2 is advisory; the Planning Engine owns feasibility.

**Exit:** exactly one `accepted` plan per student and horizon. The prior plan becomes
`superseded` and is never rewritten in place.
