# Planning Engine

## Inputs and outputs

The engine turns validated availability, goals, topic mastery, revision obligations, and deadlines into a `study_plan` conforming to [`schemas/study_plan.json`](../schemas/study_plan.json). A plan is a versioned proposal until the student accepts it.

## Planning rules

- Reserve due revisions before allocating new coverage.
- Schedule by estimated focused minutes, not vague day labels.
- Include recovery capacity; do not allocate more than 85% of stated availability without confirmation.
- Break a topic into objective-bearing tasks with prerequisites.
- Re-plan remaining tasks after a missed task; never mark it complete by inference.

## Horizon

Create a weekly plan with daily task instances. The monthly workflow sets capacity and milestones; the daily workflow selects and adapts tasks. Tasks must declare a completion evidence type: `retrieval`, `practice`, `answer`, `review`, or `attendance`.

## Validation

Reject plans with duplicate task IDs, negative duration, unsatisfied prerequisites, or scheduled minutes above capacity. Explain conflicts in user-facing terms and offer the smallest feasible adjustment.
