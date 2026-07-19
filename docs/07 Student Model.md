---
title: Student Model
document_id: DOC-07
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/01 Tutor Constitution.md
  - docs/08 Memory Architecture.md
related_documents:
  - docs/03 Decision Engine.md
  - docs/04 Planning Engine.md
  - schemas/student.json
  - adr/ADR-0002.md
---

# Student Model

## Responsibility

**The Student Model stores current learner state. It stores nothing else, and it decides
nothing.**

It is the canonical answer to *who is this learner right now* — goals, availability, declared
exam context, topic mastery, preferences, and consented constraints. Its shape is
[`schemas/student.json`](../schemas/student.json).

## Boundary with Memory

The two stores are not interchangeable, and the distinction is load-bearing:

| | Student Model | [Memory](08%20Memory%20Architecture.md) |
| --- | --- | --- |
| Holds | Current derived state | Append-only evidence and derived facts |
| Cardinality | One record per student | Many records per student |
| Mutability | Versioned overwrite | Immutable once written |
| Authority | Current state | Historical truth |
| Rebuildable | Yes, from Memory | No — it is the source |

Per [Constitution C6](01%20Tutor%20Constitution.md#5-conflict-resolution), a disagreement
between them SHALL trigger recomputation of the Student Model from Memory, never the reverse.

## Identity and ownership

`student_id` is an opaque application identifier. The tutor MUST NOT infer demographic traits
from a name, writing style, or content. The student MAY inspect, correct, export, or delete
their state through the host application; deletion removes source and derived records
together ([ADR-0002](../adr/ADR-0002.md)).

## Topic mastery

Mastery is evidence-backed, never a self-description. Each record carries `topic_id`, a 0–1
`mastery` value, confidence, last evidence timestamp, and evidence count.

Mastery SHALL be computed from retrieval and evaluation events, and the inputs needed to
reproduce it MUST be retained. Self-reported confidence is stored separately and never
substituted for mastery — the gap between them is itself a diagnostic signal.

`student.mastery_weak_threshold` and `student.mastery_strong_threshold` classify a topic. The
thresholds are defined once in
[Constitution §9](01%20Tutor%20Constitution.md#9-policy-parameters).

## Derived fields

`strengths`, `weaknesses`, and `performance_metrics` are **projections** of `topic_mastery`
and Memory evidence. They exist for retrieval efficiency and MUST be recomputable. They are
never authoritative and MUST NOT be edited directly.

Revision history is **not** stored here. It is owned by the
[Revision Engine](05%20Revision%20Engine.md); this model holds summary counters only.

## Constraints and preferences

Availability is expressed as weekly minutes by day. A plan MAY use less than the declared
availability, and MUST NOT use more without confirmation.

`preferences` changes presentation — tone, format, language, pacing. It MUST NOT change
academic standards, rubric strictness, or factual accuracy requirements.

`current_focus` is a selected topic or goal. It is a statement of intent, never proof of
completion or coverage.

## Lifecycle

Create a minimal record at onboarding and enrich it through explicit intake. Immutable
learning events are emitted to Memory, separately from this profile.

Profile writes use optimistic versioning on `profile_version`. A write against a stale
version MUST be rejected, reloaded, recomputed, and re-presented to the student — this
prevents a slow model response from overwriting a newer student choice.
