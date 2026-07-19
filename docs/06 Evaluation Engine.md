# Evaluation Engine

## Purpose

Evaluate UPSC-style answers against an explicit rubric while preserving the distinction between observed text and generated advice. It produces an [`answer`](../schemas/answer.json) record.

## Rubric

Score dimensions are relevance to command word, coverage, structure, factual accuracy, analysis, examples/evidence, balance, and conclusion. Each dimension has a 0–5 score, evidence spans or paraphrases, and one improvement action. The total is derived by code from configured weights; the model MUST NOT be trusted as the source of arithmetic.

## Evaluation sequence

1. Confirm question, word limit, and answer text are present.
2. Extract a neutral outline before scoring.
3. Identify factual claims requiring verification; label unverified claims rather than inventing corrections.
4. Return rubric evidence, strengths, omissions, and a prioritized rewrite plan.
5. Create practice and revision candidates; persistence requires student/system approval.

Comparative scoring requires the same rubric version and prompt conditions. A score is coaching feedback, never a prediction of examination results.
