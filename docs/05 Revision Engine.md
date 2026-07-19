---
title: Revision Engine
document_id: DOC-05
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/01 Tutor Constitution.md
  - docs/08 Memory Architecture.md
related_documents:
  - docs/03 Decision Engine.md
  - docs/04 Planning Engine.md
  - schemas/revision.json
  - workflows/revision_cycle.md
---

# Revision Engine

## Responsibility

**The Revision Engine determines what needs retrieving and when. It does not place work in a
calendar.**

It owns [`schemas/revision.json`](../schemas/revision.json) records, the interval algorithm,
the **due set**, and each topic's forgetting risk. The due set is the engine's public output
and the sole authority on revision obligation.

| Not owned by this engine | Owner |
| --- | --- |
| Fitting revision into available time | [Planning Engine](04%20Planning%20Engine.md) |
| Choosing revision over teaching in-session | [Decision Engine](03%20Decision%20Engine.md) |
| Storing the underlying facts being retrieved | [Memory](08%20Memory%20Architecture.md) |

Revision converts learning evidence into scheduled retrieval. Passive re-reading is not
revision and SHALL NOT satisfy a review obligation.

## Scheduling policy

Intervals begin at `revision.default_intervals`. On a successful retrieval the interval
advances; on an unsuccessful retrieval it resets to the shortest interval and the engine
emits one targeted corrective candidate.

Intervals SHALL be adjusted only by observed recall quality, confidence calibration, and exam
proximity. They MUST NOT be adjusted by elapsed session time, student mood, or model
suggestion. All algorithm parameters MUST be configurable and auditable.

## Review protocol

1. Present the cue before any notes or reference material.
2. Capture response quality and self-reported confidence.
3. Reveal the corrective explanation only after a recorded attempt.
4. Persist a validated outcome and compute `next_due_at`.

Quality bands are `again`, `hard`, `good`, `easy`, and `skipped`. A **skipped** item remains
due and is not recorded as a failed attempt — conflating the two corrupts the interval
calculation.

## Interaction with planning

The engine publishes the due set; the Planning Engine reserves it. Where the two conflict,
[Constitution C1](01%20Tutor%20Constitution.md#5-conflict-resolution) governs: revision takes
precedence unless the backlog is below `revision.backlog_threshold`, in which case items MAY
be deferred by at most `revision.max_defer_days`.

Overflow beyond the accepted plan's review capacity is surfaced to re-planning. The Revision
Engine MUST NOT discard due items to fit capacity.

## Failure cases

| Case | Required behaviour |
| --- | --- |
| Attempt recorded without a cue presentation | Reject the outcome; the interval is unchanged. |
| Answer revealed before an attempt | Record the event as `skipped`; it MUST NOT advance the interval. |
| Backlog grows across consecutive horizons | Raise a re-planning signal and trigger `mentor_checkin`. MUST NOT auto-retire items. |
| Source fact for a cue is deleted | Set the record to `paused`; MUST NOT delete the attempt history. |
| Clock or timezone skew | Compute due state in the student's declared timezone; never in server-local time. |
