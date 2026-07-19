---
title: Decision Engine
document_id: DOC-03
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/01 Tutor Constitution.md
  - docs/07 Student Model.md
  - docs/08 Memory Architecture.md
related_documents:
  - docs/04 Planning Engine.md
  - docs/05 Revision Engine.md
  - docs/09 Prompt Architecture.md
  - workflows/daily.md
---

# Decision Engine

## Responsibility

**The Decision Engine selects the next action. It does nothing else.**

It does not generate lessons, allocate calendar time, compute revision intervals, or score
answers. It answers exactly one question: *given the current state, what is the single best
next intervention?*

| Not owned by this engine | Owner |
| --- | --- |
| Placing work into a horizon | [Planning Engine](04%20Planning%20Engine.md) |
| Computing the due set and intervals | [Revision Engine](05%20Revision%20Engine.md) |
| Scoring answers | [Evaluation Engine](06%20Evaluation%20Engine.md) |
| Reading or writing learner state | [Student Model](07%20Student%20Model.md), [Memory](08%20Memory%20Architecture.md) |

## Inputs

All inputs MUST be validated before selection. The engine SHALL NOT read a store directly;
the Orchestrator supplies the following:

| Input | Source | Required |
| --- | --- | --- |
| Student profile and topic mastery | [`schemas/student.json`](../schemas/student.json) | Yes |
| Due set | Revision Engine | Yes |
| Accepted plan tasks for the horizon | [`schemas/study_plan.json`](../schemas/study_plan.json) | Yes |
| Recent evidence and answers | [`schemas/answer.json`](../schemas/answer.json), Memory | Yes |
| Session constraints (minutes remaining, modality, explicit request) | Orchestrator | Yes |

## Output

A single **action request**, containing:

`action_type`, `topic_id`, `objective`, `duration_minutes`, `evidence_expected`,
`selected_band`, `score_trace`, `assumptions`, and `fallback_action`.

`score_trace` and `fallback_action` are mandatory. An action without a fallback is invalid,
because a session may end with less time than the action requires.

## Selection procedure

1. **Filter.** Discard candidates that exceed available minutes, fall outside syllabus scope,
   or have unsatisfied prerequisites.
2. **Band.** Assign each surviving candidate to a priority band per
   [Constitution §4](01%20Tutor%20Constitution.md#4-priority-rules). Select the highest
   non-empty band; discard all lower bands.
3. **Rank within the band.** Score each candidate:

   `score = urgency + exam_weight + weakness + forgetting_risk − effort_cost`

   Weakness derives from mastery below `student.mastery_weak_threshold`. Forgetting risk is
   supplied by the Revision Engine and MUST NOT be recomputed here.
4. **Resolve.** The highest score wins. The Reasoning Engine MAY propose a rationale or break
   a tie, but application code MUST retain the scored inputs and the final decision. Per
   [Constitution C7](01%20Tutor%20Constitution.md#5-conflict-resolution), a model
   disagreement with the computed score is discarded.

The band filter is absolute: a high-scoring P5 candidate never outranks any P2 candidate.

## Action types

Every action type resolves to exactly one prompt contract. `clarify` is Orchestrator-owned
and makes no model call.

| Action type | Prompt contract | Evidence produced |
| --- | --- | --- |
| `teach` | [`teacher.md`](../prompts/teacher.md) | retrieval |
| `diagnose` | [`teacher.md`](../prompts/teacher.md) | retrieval |
| `practice` | [`teacher.md`](../prompts/teacher.md) | practice |
| `retrieve` | [`revision.md`](../prompts/revision.md) | retrieval |
| `revise` | [`revision.md`](../prompts/revision.md) | review |
| `evaluate_answer` | [`evaluator.md`](../prompts/evaluator.md) | answer |
| `draft_check` | [`answer_checker.md`](../prompts/answer_checker.md) | none |
| `plan` | [`planner.md`](../prompts/planner.md) | none |
| `reschedule` | [`scheduler.md`](../prompts/scheduler.md) | none |
| `mentor_checkin` | [`mentor.md`](../prompts/mentor.md) | attendance |
| `analyse_pyq` | [`pyq_analyzer.md`](../prompts/pyq_analyzer.md) | none |
| `brief_current_affairs` | [`current_affairs.md`](../prompts/current_affairs.md) | none |
| `clarify` | — (Orchestrator) | none |

## Failure cases

| Case | Required behaviour |
| --- | --- |
| No candidate survives filtering | Return `clarify` or `mentor_checkin`; never fabricate a task. |
| Available minutes below `planning.min_task_minutes` | Select a retrieval action or end the session explicitly. |
| Due set unavailable | Fail closed. The engine MUST NOT infer a due set. |
| Selected action falls outside the accepted plan | Proceed if P0–P3 and signal the Planning Engine to re-plan ([Constitution C2](01%20Tutor%20Constitution.md#5-conflict-resolution)). |
| Two candidates tie after ranking | Prefer the lower `effort_cost`; if still tied, prefer the earlier `next_due_at`. |
