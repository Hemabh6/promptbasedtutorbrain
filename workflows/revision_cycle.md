---
title: Revision Cycle Workflow
document_id: WF-REVISION
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/05 Revision Engine.md
related_documents:
  - prompts/revision.md
  - schemas/revision.json
  - workflows/daily.md
---

# Revision Cycle

**Trigger:** `next_due_at` is reached, or the student elects an early review.

**Owner:** [Revision Engine](../docs/05%20Revision%20Engine.md).

## Sequence

1. Fetch the revision record and its bounded source context.
2. Present the cue and collect an attempt **before** any feedback.
3. Validate the outcome and confidence. Retain `skipped` attempts distinctly from failures.
4. Compute the next interval using configured policy and append an immutable attempt event.
5. If quality is `again` or `hard`, emit one corrective teaching or practice candidate.

## Rules

- The model never computes or persists scheduling state. `next_due_at`, `interval_days`, and
  `ease_factor` are engine-computed.
- An attempt recorded with `cue_presented_first: false` MUST NOT advance the interval.
- A `skipped` item remains due and is not a lapse.
- Due state is evaluated in the student's declared timezone, never in server-local time.
- Backlog is never relieved by auto-retiring items; overflow is surfaced to re-planning
  ([Constitution C1](../docs/01%20Tutor%20Constitution.md#5-conflict-resolution)).

**Exit:** an updated due date, or surfaced scheduling overflow.
