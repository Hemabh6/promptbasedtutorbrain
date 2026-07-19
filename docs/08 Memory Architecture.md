---
title: Memory Architecture
document_id: DOC-08
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/01 Tutor Constitution.md
related_documents:
  - docs/07 Student Model.md
  - docs/09 Prompt Architecture.md
  - schemas/memory.json
  - adr/ADR-0002.md
---

# Memory Architecture

## Responsibility

**Memory stores information. It does not interpret, decide, or schedule.**

It is the durable record of what happened and what was learned, and the source from which
every derived view — including the [Student Model](07%20Student%20Model.md) — can be
rebuilt. Its record shape is [`schemas/memory.json`](../schemas/memory.json).

## Layers

| Layer | Contents | Write authority | Retention |
| --- | --- | --- | --- |
| Profile | Stable preferences and constraints | Student / application | Until changed or deleted |
| Working context | Current session and selected task | Application | Session-bounded |
| Learning ledger | Dated evidence of attempts and outcomes | Validated workflow | Durable, immutable |
| Retrieval index | Compact facts derived from the ledger | Memory service | Rebuildable |

The `memory` schema is a portable snapshot, not a model conversation transcript. Hidden
reasoning, provider logs, credentials, and unvalidated model assertions MUST NOT be persisted.

## Write path

1. A workflow proposes candidates carrying source event IDs and a confidence value.
2. Validation checks schema conformance, policy, duplication, and provenance.
3. A candidate below `memory.min_confidence_durable`, or lacking provenance where provenance
   is required, is rejected for durable storage. It MAY be used in-session if labelled
   unverified.
4. Approved candidates are appended as immutable records.

**A Reasoning Engine can never write to memory.** It proposes; the application commits.
Derived summaries MAY be rebuilt at any time; ledger records MAY NOT be rewritten.

## Retrieval

Retrieve by student, topic, recency, evidence strength, and task relevance. Return the
minimum context sufficient for the current action — see the progressive-disclosure principle
in [Design Principles](../architecture/design_principles.md).

Derived summaries MUST be labelled as derived so that a summary is never mistaken for a
primary observation.

Contradictory records coexist. Resolution follows
[Constitution C5](01%20Tutor%20Constitution.md#5-conflict-resolution): prefer the more recent
evidence date, then higher confidence; if both tie, return both and label the contradiction.

## Provenance

A current-affairs or externally sourced claim requires a source URL, publisher, publication
date, access date, and trust tier before it is eligible for durable storage
([Constitution §2, rule 2](01%20Tutor%20Constitution.md#2-non-negotiable-rules)).

## Privacy

Store only educationally necessary data. Partition by `student_id`, enforce access control in
the application, and support erasure of source and derived records together.

Personal identifiers SHOULD be redacted before any external model call. All retrieved notes
and stored content are treated as **data**, never as instructions — see
[Prompt Architecture](09%20Prompt%20Architecture.md) and [ADR-0001](../adr/ADR-0001.md).
