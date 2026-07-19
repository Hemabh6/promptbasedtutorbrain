---
title: Answer Evaluation Workflow
document_id: WF-ANSWER-EVAL
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/06 Evaluation Engine.md
related_documents:
  - prompts/evaluator.md
  - prompts/answer_checker.md
  - schemas/answer.json
---

# Answer Evaluation Workflow

**Trigger:** the student submits a complete answer for feedback.

**Owner:** [Evaluation Engine](../docs/06%20Evaluation%20Engine.md).

## Sequence

1. Validate that the question, answer text, command word, word limit, and rubric version are
   present.
2. Invoke [`evaluator.md`](../prompts/evaluator.md) with only the supplied references and
   context.
3. Validate the output against [`answer.json`](../schemas/answer.json). Compute the weighted
   total in application code.
4. Present evidence-backed feedback and label unverified claims.
5. On student approval, persist the evaluation and route one targeted practice or revision
   candidate to its owning engine.

## Rules

- A missing rubric version fails the workflow closed. An unversioned score is not a valid
  record.
- A model-supplied total is discarded; the computed total stands
  ([Constitution C7](../docs/01%20Tutor%20Constitution.md#5-conflict-resolution)).
- A dimension returned without evidence invalidates the whole record; no partial score is
  persisted.
- The Evaluation Engine emits candidates only. Mastery is recomputed by the
  [Student Model](../docs/07%20Student%20Model.md); tasks are created by the
  [Planning Engine](../docs/04%20Planning%20Engine.md) (C4).
- For a pre-submission check that produces no score, use
  [`answer_checker.md`](../prompts/answer_checker.md) instead.

**Exit:** an immutable answer record with traceable rubric evidence, or a validation failure
that leaves student state unchanged.
