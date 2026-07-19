# Student Model

The canonical student state is [`schemas/student.json`](../schemas/student.json). It contains only information needed to personalise instruction: goals, availability, declared exam context, topic mastery, preferences, and consented constraints.

## Identity and ownership

`student_id` is an opaque application identifier. The tutor never infers demographic traits. The student can inspect, correct, export, or delete their state through the host application.

## Topic mastery

Mastery is evidence-backed, not a self-description. Each topic record has `topic_id`, a 0–1 `mastery`, confidence, last evidence timestamp, and evidence count. Implementations SHOULD calculate mastery from retrieval and evaluation events, then retain the inputs needed to reproduce it. Self-reported confidence is stored separately.

## Constraints

Availability is weekly minutes by day; a plan may use less but not more without confirmation. `preferences` changes presentation, not academic standards. A `current_focus` is a selected topic or goal, not proof of completion.

## Lifecycle

Create a minimal record at onboarding, enrich it through explicit intake, and emit immutable learning events separately from the current profile. Profile changes use optimistic versioning to prevent a stale model response overwriting newer student choices.
