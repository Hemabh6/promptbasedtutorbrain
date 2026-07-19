# Prompt-Based Tutor Brain

**An architecture and specification repository for a model-agnostic AI Tutor Operating System.**

The **Tutor Brain** is the permanent intelligence: policy, state, contracts, workflows, and
validation. ChatGPT, Claude, Gemini, Grok, and future models are interchangeable execution
engines invoked through an adapter. Replacing the model MUST NOT change the tutoring
behaviour, the student's data, or any business rule.

> **Status:** Phase 1 — specification baseline. This repository is not a runnable application.

---

## Project Vision

Tutoring systems built directly on a model inherit that model's lifespan. Prompts drift,
providers deprecate, quality shifts silently, and the student's history is trapped in a
vendor's conversation format.

This project inverts that relationship. The durable asset is the **specification**: what the
tutor knows about the learner, how it decides what to teach next, how it schedules revision,
how it evaluates an answer, and what it is forbidden to do. The model is a rented reasoning
service behind a capability boundary.

The target domain is UPSC preparation — a multi-year syllabus with heavy revision load,
answer-writing assessment, and current-affairs volatility. The architecture generalises to
any long-horizon curriculum.

---

## Repository Purpose

This repository is the **source of truth** for the Tutor Brain's design. It exists to make an
implementation possible, reviewable, and replaceable — not to be the implementation.

Every document here answers one of four questions:

1. **What is the tutor forbidden or required to do?** → [`docs/01 Tutor Constitution.md`](docs/01%20Tutor%20Constitution.md)
2. **Which component owns this decision?** → [`docs/`](docs/) and [`architecture/`](architecture/)
3. **What shape is this data?** → [`schemas/`](schemas/)
4. **Why was it done this way?** → [`adr/`](adr/)

---

## Architecture Overview

Four replaceable boundaries. The Tutor Brain spans the middle two.

```text
          User Interface                    ← replaceable
                │  validated command
                ▼
       Application Orchestrator ◄──────► State Store
                │  action request              ▲  approved events
                ▼                              │
   Decision · Planning · Revision · Evaluation │   ← the Tutor Brain
                │  prompt + bounded context    │
                ▼                              │
          Reasoning Adapter ─────────────────► │
                │                                 
                ▼
      Interchangeable LLM                    ← replaceable
```

Three invariants hold everywhere:

- **Policy lives in code and specification, never in a prompt.** Prompts describe reasoning
  tasks; they never carry authorisation, arithmetic, or scheduling authority.
- **Model output is untrusted.** It is a *candidate* until schema validation, semantic checks,
  and workflow authorisation approve it.
- **Evidence is append-only.** Mastery, plans, and summaries are derived views that can be
  recomputed from their source events.

Full detail: [`architecture/architecture.md`](architecture/architecture.md).

---

## Repository Tour

Start here, in order:

| # | Read | Why |
| --- | --- | --- |
| 1 | [Tutor Constitution](docs/01%20Tutor%20Constitution.md) | Authority hierarchy, priority rules, conflict resolution. Governs everything else. |
| 2 | [Architecture](architecture/architecture.md) | Layers, component responsibilities, execution and data flow. |
| 3 | [Decision Engine](docs/03%20Decision%20Engine.md) | How the next action is chosen. The system's entry point at runtime. |
| 4 | [Student Model](docs/07%20Student%20Model.md) + [Memory Architecture](docs/08%20Memory%20Architecture.md) | What persists, and which store owns which truth. |
| 5 | [Prompt Architecture](docs/09%20Prompt%20Architecture.md) | The contract every file in `prompts/` implements. |
| 6 | [System Integration](docs/10%20System%20Integration.md) | Interfaces, failure handling, observability, versioning. |
| 7 | [ADRs](adr/) | The reasoning behind the irreversible choices. |

---

## Folder Structure

| Path | Owns | Must not contain |
| --- | --- | --- |
| `docs/` | Product policy and component specifications | Provider SDK instructions |
| `prompts/` | Portable reasoning contracts, one per action type | Secrets, durable state, policy |
| `schemas/` | Machine-validated data shapes (JSON Schema 2020-12) | Business logic hidden in prose |
| `architecture/` | Boundaries, layers, and engineering constraints | Feature-specific tutorial text |
| `workflows/` | Trigger-to-outcome operational sequences | Undocumented data fields |
| `adr/` | Accepted architectural decisions, immutable once accepted | Transient implementation notes |

Conventions and ownership rules: [`architecture/folder_structure.md`](architecture/folder_structure.md).

---

## Current Phase

**Phase 1 — Specification Baseline.** Complete and frozen for review.

Delivered: the Constitution, six component specifications, five state schemas, nine prompt
contracts, five workflows, the architecture set, and four ADRs. Every threshold is registered
in [Constitution §9](docs/01%20Tutor%20Constitution.md#9-policy-parameters); every component
declares exactly one responsibility.

---

## Future Roadmap

Phases are sequential. Each depends on the contracts frozen by its predecessor.

| Phase | Scope | Gate to enter |
| --- | --- | --- |
| **1** | Specification baseline | — |
| **2** | Reference implementation of schema validation and state persistence | Phase 1 accepted, schemas stable |
| **3** | Deterministic Decision Engine over a single adapter | Phase 2 state store operational |
| **4** | Planning, revision, and evaluation workflows end to end | Phase 3 decision traces auditable |
| **5** | Multi-provider adapter dispatch and capability negotiation | Phase 4 outcomes instrumented |
| **6** | Outcome instrumentation and calibration of policy parameters | Phase 5 in production use |

Roadmap changes are made through ADRs, not by editing this table alone.

---

## Contribution Workflow

1. Read the specifications your change touches, and the Constitution's
   [Extension Rules](docs/01%20Tutor%20Constitution.md#10-extension-rules).
2. Branch from `main`. Keep changes small and coherent.
3. Update **every** affected document in the same change — prompt, schema, workflow, and
   architecture drift together or not at all.
4. Add or amend an ADR when changing a boundary, the persistence model, or provider policy.
5. Update document metadata (`version`, `last_updated`) and [`CHANGELOG.md`](CHANGELOG.md).
6. Open a PR using the template. Reviewers verify single responsibility, resolved
   cross-references, and schema compatibility.

Full rules: [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Design Principles

1. **Policy outside the model.** Code owns authorisation, scheduling, scoring, and persistence.
2. **Evidence before inference.** Persist source events; keep summaries derivable.
3. **One responsibility per component.** Overlap is a defect, not a convenience.
4. **Progressive disclosure.** Load the smallest context; ask the smallest useful question.
5. **Recoverable operations.** Validate before writes; make retries idempotent.
6. **Student agency.** Plans are inspectable, editable, and confirmable.
7. **Portable reasoning.** Depend on declared capabilities, never a model identity.
8. **Measurable learning.** Track attempts, recall, and rubric evidence — not fluency.

Expanded, with review criteria: [`architecture/design_principles.md`](architecture/design_principles.md).

---

## What This Repository IS

- A governing specification for a long-lived tutoring system.
- A set of versioned data contracts an implementation can validate against.
- A set of provider-neutral prompt contracts written as API specifications.
- A decision record explaining why the boundaries sit where they do.
- A review standard: a change that violates the Constitution is rejected on that basis alone.

## What This Repository IS NOT

- **Not an implementation.** There is no application code, and none is planned here.
- **Not a prompt library.** Prompts here are contracts with inputs, outputs, and failure
  cases — not snippets to paste into a chat window.
- **Not model-specific.** No provider name, model ID, SDK, or pricing assumption appears in
  any specification.
- **Not infrastructure.** No API definitions, databases, containers, orchestration
  frameworks, or authentication schemes.
- **Not a syllabus or content bank.** It specifies how content is selected, taught, and
  assessed — it does not contain the content.
- **Not a guarantee of outcomes.** See
  [Constitution §7](docs/01%20Tutor%20Constitution.md#7-non-goals).

---

## License

[MIT](LICENSE). See [CHANGELOG.md](CHANGELOG.md) for version history.
