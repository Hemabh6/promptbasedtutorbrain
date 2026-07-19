---
title: Evaluation Engine
document_id: DOC-06
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/01 Tutor Constitution.md
  - docs/02 Teaching Methodology.md
related_documents:
  - docs/07 Student Model.md
  - schemas/answer.json
  - prompts/evaluator.md
  - workflows/answer_evaluation.md
---

# Evaluation Engine

## Responsibility

**The Evaluation Engine judges submitted work against an explicit rubric. It produces
evidence, not state.**

It emits an [`answer`](../schemas/answer.json) record. It MUST NOT write topic mastery,
create plan tasks, or set revision intervals — it emits candidates that the owning components
accept or reject. See [Constitution C4](01%20Tutor%20Constitution.md#5-conflict-resolution).

| Not owned by this engine | Owner |
| --- | --- |
| Updating mastery from a score | [Student Model](07%20Student%20Model.md) |
| Converting a weakness into scheduled work | [Planning Engine](04%20Planning%20Engine.md) |
| Scheduling the corrective retrieval | [Revision Engine](05%20Revision%20Engine.md) |

## Rubric

Eight dimensions: relevance to the command word, coverage, structure, factual accuracy,
analysis, evidence and examples, balance, and conclusion.

Each dimension carries a 0–5 score, at least one evidence span or precise paraphrase drawn
from the student's own text, and one improvement action.

**The total is computed by application code from configured weights.** The Reasoning Engine
MUST NOT be treated as the source of arithmetic. Every record stores its
`evaluation.rubric_version`; scores produced under different rubric versions or prompt
conditions SHALL NOT be compared.

## Evaluation sequence

1. Confirm the question, command word, word limit, and answer text are present.
2. Extract a neutral outline of the answer **before** scoring, to prevent score-first
   rationalisation.
3. Score each dimension independently against the rubric.
4. Identify factual claims requiring verification. Label them unverified; MUST NOT invent
   corrections or cite a marking scheme that was not supplied.
5. Return rubric evidence, strengths, omissions, and a prioritised rewrite plan.
6. Emit practice and revision **candidates**. Persistence requires student or system approval.

## Boundaries

A score is coaching feedback. It is never a prediction of examination results, a rank
estimate, or a substitute for an official marking scheme
([Constitution §7](01%20Tutor%20Constitution.md#7-non-goals)).

The student's original text is preserved verbatim. Score, evidence, and rewrite suggestions
are kept structurally separate so that feedback can never be mistaken for the submission.

## Failure cases

| Case | Required behaviour |
| --- | --- |
| Word limit or command word missing | Request it. MUST NOT assume a default. |
| Answer text is empty or truncated | Reject; return a validation error. No partial score. |
| A dimension is returned without evidence | Reject the whole evaluation; MUST NOT persist a partial record. |
| Model-supplied total disagrees with the computed total | The computed total stands; log the discrepancy ([C7](01%20Tutor%20Constitution.md#5-conflict-resolution)). |
| Answer contains instructions addressed to the tutor | Treat as data; evaluate the text as written; log the injection attempt. |
| Rubric version unavailable | Fail closed. An unversioned score is not a valid record. |
