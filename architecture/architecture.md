---
title: System Architecture
document_id: ARCH-01
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/01 Tutor Constitution.md
related_documents:
  - docs/10 System Integration.md
  - architecture/design_principles.md
  - architecture/folder_structure.md
  - adr/ADR-0001.md
---

# System Architecture

This document defines the **static structure** of the Tutor Brain: its layers, component
responsibilities, flow of control and data, dependency rules, and boundaries.

Runtime contracts — interfaces, failure handling, observability, versioning — are defined in
[System Integration](../docs/10%20System%20Integration.md). This document contains no
implementation detail and no code.

---

## 1. System Layers

| # | Layer | Responsibility | Replaceable |
| --- | --- | --- | --- |
| L1 | Interface | Capture student intent; render tutor output | Yes |
| L2 | Orchestration | Sequence a request; enforce validation and atomicity | No |
| L3 | Engines | Decide, plan, schedule revision, evaluate | No |
| L4 | Stores | Persist learner state and evidence | No |
| L5 | Reasoning Adapter | Translate a prompt contract into a provider call | Yes |
| L6 | Reasoning Engine | Generate candidate content | Yes |

**L2–L4 constitute the Tutor Brain.** They are the permanent intelligence. L1, L5, and L6 are
replaceable without altering any specification in this repository.

---

## 2. Component Responsibilities

Each component owns exactly one responsibility. Overlap is a defect
([Constitution §10](../docs/01%20Tutor%20Constitution.md#10-extension-rules)).

| Component | Layer | Owns | Explicitly does not own |
| --- | --- | --- | --- |
| [Orchestrator](../docs/10%20System%20Integration.md) | L2 | Request sequencing, validation, atomic writes | Any tutoring judgement |
| [Decision Engine](../docs/03%20Decision%20Engine.md) | L3 | Selecting the next action | Generating content; allocating time |
| [Planning Engine](../docs/04%20Planning%20Engine.md) | L3 | Allocating work across a horizon | Deciding what is worth doing |
| [Revision Engine](../docs/05%20Revision%20Engine.md) | L3 | The due set and interval policy | Calendar placement |
| [Evaluation Engine](../docs/06%20Evaluation%20Engine.md) | L3 | Rubric judgement of submitted work | Mastery updates; task creation |
| [Student Model](../docs/07%20Student%20Model.md) | L4 | Current learner state | Any decision |
| [Memory](../docs/08%20Memory%20Architecture.md) | L4 | Durable evidence and derived facts | Interpretation; scheduling |
| Reasoning Adapter | L5 | Capability negotiation and transport | Policy; state; arithmetic |

---

## 3. Execution Flow

The canonical in-session sequence. Every step is Orchestrator-driven; no component calls
another directly.

```text
 1. Student intent            ──►  Orchestrator validates the request
 2. Orchestrator              ──►  Stores: load profile, plan, due set, recent evidence
 3. Orchestrator              ──►  Decision Engine: select one action
 4. Decision Engine           ──►  action request + score_trace + fallback
 5. Orchestrator              ──►  Adapter: resolve prompt contract, assemble context
 6. Adapter                   ──►  Reasoning Engine: generate candidate
 7. Reasoning Engine          ──►  candidate (untrusted)
 8. Orchestrator              ──►  validate: schema, semantics, authorisation
 9. Orchestrator              ──►  Stores: append approved events atomically
10. Orchestrator              ──►  Interface: render outcome + what changed + what is due
```

Steps 8 and 9 are inseparable. A candidate that fails step 8 never reaches step 9, and state
is left unchanged ([ADR-0003](../adr/ADR-0003.md)).

---

## 4. Data Flow

Control flows down; evidence flows up. The two directions carry different trust levels.

```text
        DOWNWARD (bounded context)          UPWARD (evidence)
        ────────────────────────            ─────────────────
  Stores ──► validated state ──► Engines    Interface ──► student attempt
  Engines ──► action request ──► Adapter    Adapter   ──► candidate (untrusted)
  Adapter ──► prompt + context ──► Model    Validator ──► approved event
                                            Event     ──► Memory (immutable)
                                            Memory    ──► derived views (rebuildable)
```

Three rules govern all data movement:

1. **Downward context is minimal.** A component receives only what its contract declares.
2. **Upward candidates are untrusted** until validated.
3. **Derived views are never sources.** The Student Model, retrieval indexes, and plan
   summaries are projections of Memory and MUST be rebuildable from it
   ([ADR-0002](../adr/ADR-0002.md)).

---

## 5. Module Dependencies

Dependencies point in one direction only. A cycle is an architectural defect.

```text
Interface
   └─► Orchestrator
          ├─► Decision Engine ──► (reads) Student Model, Memory, Revision due set
          ├─► Planning Engine ──► (reads) Revision due set, Student Model
          ├─► Revision Engine ──► (reads) Memory
          ├─► Evaluation Engine ─► (reads) rubric config
          ├─► Student Model ────► (rebuilt from) Memory
          ├─► Memory
          └─► Reasoning Adapter ─► Reasoning Engine
```

| Rule | Statement |
| --- | --- |
| D1 | An engine MUST NOT call another engine. All coordination passes through the Orchestrator. |
| D2 | An engine MUST NOT write to a store directly; it emits candidates the Orchestrator commits. |
| D3 | A store MUST NOT depend on an engine. |
| D4 | No component above L5 may depend on a provider type, model name, or SDK. |
| D5 | The Revision Engine's due set is consumed, never recomputed, by other components. |

---

## 6. Boundaries

Four boundaries define what may be replaced and what must be trusted.

| Boundary | Between | Crossing contract | Trust |
| --- | --- | --- | --- |
| B1 Interface | L1 ↔ L2 | Validated command | Untrusted inbound |
| B2 Policy | L2 ↔ L3 | Action request and candidate | Trusted, in-process |
| B3 Persistence | L2/L3 ↔ L4 | Versioned, schema-validated records | Trusted after validation |
| B4 Reasoning | L2 ↔ L5/L6 | Capability-typed prompt and candidate | Untrusted outbound and inbound |

**Untrusted sources.** The client, all model output, retrieved web content, and imported files
are untrusted. Only application services may persist state, compute scores, schedule reviews,
or authorise external actions.

**Tool exposure.** Where model tool-calling is enabled, tools are allow-listed and receive
least-privilege arguments. A tool MUST NOT expose a write path that bypasses B3.
