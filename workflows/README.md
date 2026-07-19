# Workflows

Application-owned transitions from trigger to outcome. Every write is validated and
attributable; model output proposes content but never commits it.

| Workflow | Trigger | Owner |
| --- | --- | --- |
| [daily.md](daily.md) | Session start or scheduled daily run | Orchestrator |
| [weekly.md](weekly.md) | Weekly planning boundary | [Planning Engine](../docs/04%20Planning%20Engine.md) |
| [monthly.md](monthly.md) | Month boundary or cycle start | Planning Engine |
| [revision_cycle.md](revision_cycle.md) | `next_due_at` reached | [Revision Engine](../docs/05%20Revision%20Engine.md) |
| [answer_evaluation.md](answer_evaluation.md) | Answer submitted | [Evaluation Engine](../docs/06%20Evaluation%20Engine.md) |

Monthly sets capacity and outcomes; weekly produces the plan; daily selects within it. Each
horizon feeds the next and none reaches past its own scope.
