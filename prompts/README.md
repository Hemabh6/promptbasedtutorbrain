# Prompt Contracts

Provider-neutral reasoning contracts. Each is an API specification, not a snippet.

Every contract implements the nine-section structure defined in
[Prompt Architecture](../docs/09%20Prompt%20Architecture.md): Purpose, Inputs, Outputs,
Constraints, Failure Cases, Dependencies, Examples, Quality Criteria, Version.

| Contract | Serves action types | Invoked by |
| --- | --- | --- |
| [teacher.md](teacher.md) | `teach`, `diagnose`, `practice` | [Decision Engine](../docs/03%20Decision%20Engine.md) |
| [revision.md](revision.md) | `retrieve`, `revise` | Decision Engine |
| [evaluator.md](evaluator.md) | `evaluate_answer` | [Evaluation Engine](../docs/06%20Evaluation%20Engine.md) |
| [answer_checker.md](answer_checker.md) | `draft_check` | Decision Engine |
| [planner.md](planner.md) | `plan` | [Planning Engine](../docs/04%20Planning%20Engine.md) |
| [scheduler.md](scheduler.md) | `reschedule` | Planning Engine |
| [mentor.md](mentor.md) | `mentor_checkin` | Decision Engine |
| [pyq_analyzer.md](pyq_analyzer.md) | `analyse_pyq` | Decision Engine |
| [current_affairs.md](current_affairs.md) | `brief_current_affairs` | Decision Engine |

The `clarify` action type is Orchestrator-owned and makes no model call.

## Rules

1. A contract is rendered with validated JSON input, the
   [Tutor Constitution](../docs/01%20Tutor%20Constitution.md), and a provider adapter.
2. Output is **advisory** until the application validates it. No prompt may persist state.
3. Prompts MUST NOT contain authorisation rules, arithmetic, scheduling computation, secrets,
   vendor names, or model identifiers.
4. A change to a contract's Outputs or Constraints is a major version change and requires the
   consuming schema and engine documents to be reviewed in the same change.
