---
title: Answer Checker Prompt Contract
document_id: PROMPT-ANSWER-CHECKER
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/09 Prompt Architecture.md
  - docs/06 Evaluation Engine.md
related_documents:
  - prompts/evaluator.md
---

# Answer Checker

## Purpose

Provide a fast pre-submission quality check on a draft. Serves the `draft_check` action type.

This is explicitly **not** an evaluation. It produces no score and no durable record. Formal
assessment is [`evaluator.md`](evaluator.md).

## Inputs

| Field | Source | Required | Notes |
| --- | --- | --- | --- |
| `question`, `command_word`, `word_limit` | Orchestrator | Yes | Basis of the alignment check |
| `draft_answer` | Student | Yes | Preserved verbatim |
| `checklist` | Evaluation Engine | Yes | Structural criteria only, not the rubric |
| `outline` | Student | No | Compared against the draft when supplied |

## Outputs

```json
{
  "findings": [
    { "check": "string", "result": "pass|warning", "detail": "string" }
  ],
  "missing_elements": ["string"],
  "edit_suggestions": [{ "priority": 1, "suggestion": "string" }],
  "word_count": 0,
  "is_evaluation": false
}
```

## Constraints

- MUST check command-word alignment, structure, coverage, balance, conclusion, and obviously
  unsupported claims.
- MUST order `edit_suggestions` by impact, highest first.
- MUST preserve the student's voice, argument, and stance.
- MUST set `is_evaluation: false` in every response.
- MUST NOT produce a score, grade, band, or rubric dimension.
- MUST NOT rewrite the answer or supply replacement prose beyond a targeted phrase.
- MUST NOT create memory, revision, or plan candidates.
- MUST NOT persist anything; this contract is stateless.

## Failure Cases

| Case | Required behaviour |
| --- | --- |
| Student requests a score | Decline and offer the `evaluate_answer` action. MUST NOT estimate one. |
| Draft is empty or a fragment | Return `missing_elements` only; MUST NOT infer intent. |
| Word count exceeds `word_limit` | Report as a `warning` with the overage; MUST NOT truncate the draft. |
| Draft contradicts itself | Report the contradiction as a finding; MUST NOT choose a side for the student. |
| Command word absent | Request it; MUST NOT infer from question phrasing. |

## Dependencies

Invoked by the [Decision Engine](../docs/03%20Decision%20Engine.md). Hands off to
[`evaluator.md`](evaluator.md) when the student submits the same text for formal assessment.
Uses the checklist supplied by the
[Evaluation Engine](../docs/06%20Evaluation%20Engine.md); it never reads the rubric itself.

## Examples

**Input (abbreviated)**

```json
{ "question": "Examine the fiscal federalism challenges post-GST.",
  "command_word": "examine", "word_limit": 250,
  "draft_answer": "GST reduced state autonomy ...", "checklist": ["has_conclusion", "addresses_command_word"] }
```

**Output (abbreviated)**

```json
{ "findings": [
    { "check": "addresses_command_word", "result": "warning",
      "detail": "Reads as description; 'examine' expects weighing of both sides." },
    { "check": "has_conclusion", "result": "pass", "detail": "Final line states a position." } ],
  "missing_elements": ["counter-perspective on compensation cess"],
  "edit_suggestions": [{ "priority": 1, "suggestion": "Add one sentence on the revenue-gain side before concluding." }],
  "word_count": 268, "is_evaluation": false }
```

## Quality Criteria

1. No score, band, or numeric quality judgement appears anywhere in the output.
2. Every finding names a specific checklist item.
3. Suggestions are edits to the student's text, not replacements for it.
4. `word_count` is reported, never enforced by truncation.

## Version

1.0.0 — Accepted — 2026-07-19.
