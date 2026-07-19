---
title: Design Principles
document_id: ARCH-02
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/01 Tutor Constitution.md
related_documents:
  - architecture/architecture.md
  - CONTRIBUTING.md
---

# Design Principles

These principles are **review criteria**. A change that violates one is rejected on that
basis, or the principle is amended first — never silently excepted.

| # | Principle | Statement | Reviewer asks |
| --- | --- | --- | --- |
| 1 | **Policy outside the model** | Code owns authorisation, scheduling, scoring arithmetic, and persistence. | Does any rule exist only in prompt text? |
| 2 | **Evidence before inference** | Persist source events; keep summaries derivable and labelled. | Can this derived value be recomputed from stored evidence? |
| 3 | **One responsibility per component** | Each component owns exactly one responsibility; overlap is a defect. | Does another component already own this? |
| 4 | **Progressive disclosure** | Load the smallest context and ask the smallest useful question. | Is any of this context unused by the contract? |
| 5 | **Recoverable operations** | Validate before writes; make retries idempotent; never commit partially. | What state remains if this fails midway? |
| 6 | **Student agency** | Plans are inspectable, editable, and confirmable; workload increases need consent. | Can the student see and decline this change? |
| 7 | **Portable reasoning** | Depend on declared capabilities, never on a model identity. | Would this still hold on a different provider? |
| 8 | **Measurable learning** | Track attempts, recall, and rubric evidence — not conversational fluency. | Is this metric evidence of learning or of usage? |
| 9 | **Single source of threshold** | Every configurable value is registered in [Constitution §9](../docs/01%20Tutor%20Constitution.md#9-policy-parameters). | Is this number declared anywhere else? |
| 10 | **Documents reference, never duplicate** | A concept is defined once and linked thereafter. | Does this text restate another document? |
