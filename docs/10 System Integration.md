---
title: System Integration
document_id: DOC-10
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/01 Tutor Constitution.md
  - architecture/architecture.md
related_documents:
  - docs/09 Prompt Architecture.md
  - adr/ADR-0003.md
  - workflows/daily.md
---

# System Integration

## Responsibility

This document defines **runtime contracts**: the interfaces components expose, how failures
are handled, what is observed, and how versions evolve.

Static structure — layers, dependencies, and data flow — is defined in
[`architecture/architecture.md`](../architecture/architecture.md) and is not repeated here.

## Orchestrator obligations

The Orchestrator is the only component that may sequence a request. It SHALL, in order:

1. Validate the incoming request.
2. Load required state from the stores.
3. Invoke the deterministic [Decision Engine](03%20Decision%20Engine.md).
4. Select an adapter whose capabilities satisfy the chosen prompt contract.
5. Validate generated output against its schema and semantic checks.
6. Write approved events atomically.

The Orchestrator holds no tutoring policy of its own. It enforces the Constitution's failure
modes and delegates every judgement to an owning component.

## Required interfaces

| Interface | Contract |
| --- | --- |
| **State store** | Versioned read/write of profile, plans, memory, revisions, and answers. Optimistic concurrency on `profile_version` and `plan_id`. |
| **Engine adapter** | `capabilities`, `generate`, and normalised error and result types. No provider-specific types cross this boundary. |
| **Knowledge source** | Source retrieval returning URL, publisher, publication date, access date, and trust tier. Sources without this metadata are ineligible for durable memory. |
| **Clock and queue** | Timezone-aware evaluation of due reviews and scheduled plan operations, in the student's declared timezone. |

The Reasoning Engine is stateless from the system's perspective and MAY be changed between
requests without migration.

## Failure handling

If a model call, parse, validation, or persistence step fails, the system MUST NOT mutate
durable state. It SHALL return the action status, a retry-safe correlation ID, and a
deterministic fallback where one is available.

Partial commits are prohibited. A multi-record write either completes or leaves state
unchanged.

The full failure-mode table — missing state, adapter unavailability, stale versions, capacity
overflow, injection, and erasure — is defined once in
[Constitution §8](01%20Tutor%20Constitution.md#8-failure-modes).

## Observability

A trace SHALL correlate: user command, input record versions, decision and its `score_trace`,
prompt version, adapter capability profile, validation result, and resulting state mutations.

Logs record prompt version, schema version, input record IDs, capability set, and outcome.
They MUST NOT record raw sensitive content by default.

Metrics track task completion, recall quality, plan load, retry rate, and evaluator
calibration. A provider's token usage is a cost signal and SHALL NOT be treated as learning
evidence.

## Versioning

Every persisted artifact stores its `schema_version` and the prompt version that produced it.

Backward reads are supported through migrations. A breaking contract change requires an
accepted ADR and a [CHANGELOG](../CHANGELOG.md) entry, per
[Constitution §11](01%20Tutor%20Constitution.md#11-versioning).
