---
title: PYQ Analyzer Prompt Contract
document_id: PROMPT-PYQ-ANALYZER
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/09 Prompt Architecture.md
  - docs/01 Tutor Constitution.md
related_documents:
  - docs/04 Planning Engine.md
---

# PYQ Analyzer

## Purpose

Analyse a supplied set of previous-year questions as a **bounded dataset**, reporting observed
distribution and patterns. Serves the `analyse_pyq` action type.

## Inputs

| Field | Source | Required | Notes |
| --- | --- | --- | --- |
| `questions` | Orchestrator | Yes | Each with `question_id`, `year`, `paper`, `marks` |
| `topic_tags` | Orchestrator | No | May be partial or absent |
| `analysis_goal` | Decision Engine | Yes | Bounds the report |
| `syllabus_map` | Knowledge source | No | For mapping questions to syllabus nodes |

## Outputs

```json
{
  "dataset_size": 0,
  "years_covered": ["2020"],
  "topic_distribution": [{ "topic_id": "string", "count": 0, "question_ids": ["string"] }],
  "command_word_patterns": [{ "command_word": "string", "count": 0 }],
  "representative_questions": [{ "question_id": "string", "why": "string" }],
  "coverage_gaps": [{ "topic_id": "string", "note": "string" }],
  "ambiguous_tags": [{ "question_id": "string", "candidate_topics": ["string"] }],
  "recommendations": [{ "topic_id": "string", "action": "string", "evidence_ids": ["string"] }]
}
```

## Constraints

- MUST count only the supplied questions. `dataset_size` MUST equal the input length.
- MUST attach `question_ids` to every count so any figure can be audited.
- MUST distinguish observed pattern from interpretation.
- MUST preserve ambiguous tagging in `ambiguous_tags` rather than forcing a single topic.
- MUST state that gaps reflect the supplied dataset, not the syllabus as a whole.
- MUST NOT forecast, predict, or rank questions as likely, probable, or guaranteed
  ([Constitution §7](../docs/01%20Tutor%20Constitution.md#7-non-goals)).
- MUST NOT introduce questions from memory or outside the supplied set.
- MUST NOT create plan tasks.

## Failure Cases

| Case | Required behaviour |
| --- | --- |
| Dataset too small for a pattern claim | Report counts only; omit `command_word_patterns`. MUST NOT generalise. |
| Years are non-contiguous | Report `years_covered` explicitly; MUST NOT interpolate trends across gaps. |
| A question maps to several topics | List all candidates in `ambiguous_tags`; MUST NOT pick one arbitrarily. |
| Student asks what will be asked next | Decline; return observed distribution instead. |
| `topic_tags` absent entirely | Derive from `syllabus_map` if supplied; otherwise report untagged and continue. |

## Dependencies

Invoked by the [Decision Engine](../docs/03%20Decision%20Engine.md). Accepted
`recommendations` are converted into tasks by the
[Planning Engine](../docs/04%20Planning%20Engine.md) — this contract never creates them.

## Examples

**Input (abbreviated)**

```json
{ "questions": [
    { "question_id": "q1", "year": 2022, "paper": "GS2", "marks": 15 },
    { "question_id": "q2", "year": 2023, "paper": "GS2", "marks": 10 } ],
  "analysis_goal": "Identify GS2 polity emphasis" }
```

**Output (abbreviated)**

```json
{ "dataset_size": 2, "years_covered": ["2022", "2023"],
  "topic_distribution": [{ "topic_id": "polity.federalism", "count": 2, "question_ids": ["q1", "q2"] }],
  "coverage_gaps": [{ "topic_id": "polity.judiciary", "note": "Absent from this 2-question set; not a syllabus claim." }],
  "recommendations": [{ "topic_id": "polity.federalism", "action": "Practise one 15-mark answer", "evidence_ids": ["q1"] }] }
```

## Quality Criteria

1. Every count is reproducible from `question_ids`.
2. `dataset_size` matches the input exactly.
3. No sentence asserts or implies future exam content.
4. Every recommendation carries at least one `evidence_id`.

## Version

1.0.0 — Accepted — 2026-07-19.
