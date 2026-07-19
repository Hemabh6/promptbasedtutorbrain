---
title: Revision Prompt Contract
document_id: PROMPT-REVISION
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/09 Prompt Architecture.md
  - docs/05 Revision Engine.md
related_documents:
  - schemas/revision.json
  - workflows/revision_cycle.md
---

# Revision

## Purpose

Conduct one retrieval-based revision event: present a cue, elicit an attempt, then correct.
Serves the `retrieve` and `revise` action types.

## Inputs

| Field | Source | Required | Notes |
| --- | --- | --- | --- |
| `revision_id`, `cue`, `expected_features` | [`revision.json`](../schemas/revision.json) | Yes | `expected_features` withheld from the student until an attempt |
| `source_facts` | [`memory.json`](../schemas/memory.json) | Yes | Reference for correction |
| `recent_outcomes` | Revision Engine | No | Last attempts and confidence |
| `time_box_minutes` | Decision Engine | Yes | Bounds the exchange |
| `accessibility_mode` | `student.constraints` | No | Only permitted reason to alter the protocol |

## Outputs

```json
{
  "cue_presented": "string",
  "attempt_recorded": true,
  "correction": "string",
  "misconceptions_identified": ["string"],
  "follow_up_question": "string",
  "proposed_quality": "again|hard|good|easy|skipped",
  "reported_confidence": 0.0
}
```

`proposed_quality` is a proposal. `next_due_at`, `interval_days`, and `ease_factor` are
computed by the Revision Engine and MUST NOT appear in this output.

## Constraints

- MUST present `cue` before any notes, `source_facts`, or `expected_features`.
- MUST wait for an attempt where the transport permits interaction, and set
  `attempt_recorded` accordingly.
- MUST elicit self-reported confidence after the attempt, not before.
- MUST correct against `source_facts` only.
- MUST NOT reveal the answer before a recorded attempt, except under `accessibility_mode`.
- MUST NOT compute or propose any date, interval, or ease factor.
- MUST NOT convert a `skipped` item into a failed attempt.

## Failure Cases

| Case | Required behaviour |
| --- | --- |
| Non-interactive transport | Set `attempt_recorded: false` and `proposed_quality: "skipped"`. The item remains due. |
| Student declines to attempt | Record `skipped`; MUST NOT grade an absent attempt. |
| `source_facts` missing or deleted | Return without a correction; signal the engine to set the record `paused`. |
| Attempt is partially correct | Propose `hard`, name the missing feature, and return one corrective follow-up. |
| Answer revealed before the attempt | Record `skipped` with `cue_presented_first: false`; the interval MUST NOT advance. |
| `time_box_minutes` exhausted mid-exchange | Record the attempt as made; defer the follow-up question. |

## Dependencies

Invoked by the [Decision Engine](../docs/03%20Decision%20Engine.md); validated and persisted
by the [Revision Engine](../docs/05%20Revision%20Engine.md). Reads
[`memory.json`](../schemas/memory.json). Workflow:
[`revision_cycle.md`](../workflows/revision_cycle.md).

## Examples

**Input (abbreviated)**

```json
{ "revision_id": "rev_44", "cue": "Distinguish CPI from WPI by coverage and use.",
  "expected_features": ["consumer vs wholesale basket", "CPI drives monetary policy"],
  "time_box_minutes": 5 }
```

**Output (abbreviated)**

```json
{ "cue_presented": "Distinguish CPI from WPI by coverage and use.",
  "attempt_recorded": true,
  "correction": "Coverage was correct; the policy-target link was missing.",
  "misconceptions_identified": ["Believes WPI anchors the inflation target"],
  "follow_up_question": "Which index does the MPC target?",
  "proposed_quality": "hard", "reported_confidence": 0.5 }
```

## Quality Criteria

1. `cue_presented` appears before any correction content in the exchange.
2. `proposed_quality` is justified by an identified gap in `expected_features`.
3. No scheduling field appears anywhere in the output.
4. A `skipped` outcome is never accompanied by a graded correction.

## Version

1.0.0 — Accepted — 2026-07-19.
