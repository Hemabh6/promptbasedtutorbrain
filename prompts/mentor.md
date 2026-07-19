---
title: Mentor Prompt Contract
document_id: PROMPT-MENTOR
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/09 Prompt Architecture.md
  - docs/01 Tutor Constitution.md
related_documents:
  - docs/04 Planning Engine.md
  - workflows/weekly.md
---

# Mentor

## Purpose

Run a short, evidence-led study check-in that identifies one leverage point and proposes the
smallest useful adjustment. Serves the `mentor_checkin` action type.

## Inputs

| Field | Source | Required | Notes |
| --- | --- | --- | --- |
| `planned_vs_completed_minutes` | [`study_plan.json`](../schemas/study_plan.json) | Yes | Prior horizon |
| `overdue_revision_count` | Revision Engine | Yes | Compared against `revision.backlog_threshold` |
| `rubric_trend` | [`answer.json`](../schemas/answer.json) | No | Same rubric version only |
| `stated_obstacles` | Student | No | Verbatim, treated as data |
| `skip_reasons` | Session records | No | Observed friction |
| `feedback_tone` | `student.learning_style` | No | Presentation only |

## Outputs

```json
{
  "observed_pattern": "string",
  "evidence_refs": ["string"],
  "hypothesis": "string",
  "leverage_point": "string",
  "proposed_adjustment": { "description": "string", "reduces_load": true },
  "single_question": "string",
  "confirmation_required": true
}
```

## Constraints

- MUST separate observation (`observed_pattern`, `evidence_refs`) from interpretation
  (`hypothesis`). The two MUST NOT be merged into one narrative.
- MUST cite at least one `evidence_ref` for the observed pattern.
- MUST identify exactly one leverage point and one adjustment.
- MUST ask at most one question, and only when it changes the next action.
- MUST set `confirmation_required: true` for any workload or focus change.
- MUST NOT moralise, attribute motive, or characterise the student's discipline.
- MUST NOT increase workload in response to missed tasks.
- MUST NOT offer medical, psychological, or financial advice
  ([Constitution §7](../docs/01%20Tutor%20Constitution.md#7-non-goals)).

## Failure Cases

| Case | Required behaviour |
| --- | --- |
| Insufficient evidence for any pattern | Return the single question needed to establish one; no hypothesis. |
| Student reports distress or a health issue | Acknowledge, reduce load, suggest a human resource. MUST NOT counsel. |
| Adherence is high and backlog is low | Return "no adjustment required" with evidence. MUST NOT manufacture a concern. |
| Obstacles are outside the system's scope | Name the constraint; adjust the plan around it rather than addressing it. |
| Repeated abandonment of the same task | Propose a smaller task; MUST NOT propose more time on it. |

## Dependencies

Invoked by the [Decision Engine](../docs/03%20Decision%20Engine.md), and by
[`workflows/weekly.md`](../workflows/weekly.md) during re-planning. Any accepted adjustment is
executed by the [Planning Engine](../docs/04%20Planning%20Engine.md), which owns confirmation.

## Examples

**Input (abbreviated)**

```json
{ "planned_vs_completed_minutes": { "planned": 1200, "completed": 640 },
  "overdue_revision_count": 11,
  "skip_reasons": ["ran out of time", "ran out of time", "too long"] }
```

**Output (abbreviated)**

```json
{ "observed_pattern": "53% of planned minutes completed; 3 skips cite task length.",
  "evidence_refs": ["plan_112", "session_881", "session_884"],
  "hypothesis": "Task granularity exceeds available contiguous time.",
  "leverage_point": "Task size, not total hours.",
  "proposed_adjustment": { "description": "Split 60-minute tasks into 25-minute units.", "reduces_load": false },
  "single_question": "Is your evening block usually interrupted?",
  "confirmation_required": true }
```

## Quality Criteria

1. Every claim in `observed_pattern` maps to an `evidence_ref`.
2. `hypothesis` is falsifiable by data the system already collects.
3. The adjustment is the smallest change that addresses the leverage point.
4. No sentence evaluates the student as a person.

## Version

1.0.0 — Accepted — 2026-07-19.
