# Decision Engine

## Responsibility

The Decision Engine selects the next best tutor action; it does not generate the lesson itself. Its inputs are validated `student`, `memory`, recent answers, due revisions, and current session constraints. Its output is an action request for a specialised prompt.

## Priority order

1. Safety, explicit student request, and blocking constraints.
2. Due revisions and urgent exam deadlines.
3. Diagnosed prerequisite gaps and low-confidence high-weight topics.
4. Current-plan tasks and answer-writing practice.
5. Enrichment.

## Deterministic policy

Filter candidates by available minutes, syllabus scope, and prerequisites. Rank remaining candidates by `urgency + exam_weight + weakness + forgetting_risk - effort_cost`. The LLM MAY propose a rationale or tie-breaker, but application code MUST retain the scored inputs and final decision trace.

## Action types

`teach`, `diagnose`, `practice`, `retrieve`, `evaluate_answer`, `revise`, `plan`, `mentor_checkin`, and `clarify`. Every action includes `topic_id`, objective, duration, evidence expected, and a fallback when time is insufficient.

See [Planning Engine](04%20Planning%20Engine.md) and [Revision Engine](05%20Revision%20Engine.md).
