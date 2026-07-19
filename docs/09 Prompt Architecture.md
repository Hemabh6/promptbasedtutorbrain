---
title: Prompt Architecture
document_id: DOC-09
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/01 Tutor Constitution.md
  - docs/03 Decision Engine.md
related_documents:
  - docs/10 System Integration.md
  - prompts/README.md
  - adr/ADR-0001.md
  - adr/ADR-0003.md
---

# Prompt Architecture

## Responsibility

This document defines the **contract that every file in [`prompts/`](../prompts/) implements**.
It is a meta-specification: it governs the shape of prompt contracts, not the content of any
one of them.

A prompt contract is an API specification for a reasoning task. It is not a snippet, not a
persona, and not a policy carrier.

## The prompt contract

Every prompt document SHALL contain these nine sections, in this order. A missing section is
a specification defect.

| Section | Defines |
| --- | --- |
| **Purpose** | The single reasoning task, in one or two sentences. |
| **Inputs** | Every field supplied, its source, and whether it is required. |
| **Outputs** | The exact structure returned, and the schema it must validate against. |
| **Constraints** | What the model MUST and MUST NOT do within the task. |
| **Failure Cases** | Each anticipated failure and the required behaviour. |
| **Dependencies** | The engine that invokes it, the schemas it touches, the prompts it hands off to. |
| **Examples** | One representative input/output pair, abbreviated but structurally valid. |
| **Quality Criteria** | Testable conditions under which the output is acceptable. |
| **Version** | Semantic version, status, and last-updated date. |

## Policy boundary

**Prompt text MUST NOT be the only place a rule exists.** Any requirement that matters is
enforced by code: schema validation, capacity checks, arithmetic, authorisation, persistence.

A prompt that says "do not exceed capacity" is a hint. The Planning Engine's validation is the
control. Where the two disagree, the control wins
([Constitution C7](01%20Tutor%20Constitution.md#5-conflict-resolution)).

Prompts therefore MUST NOT contain: authorisation rules, scoring arithmetic, scheduling
computation, persistence instructions, secrets, or durable state.

## Context assembly

1. Select the prompt contract for the Decision Engine's chosen action type.
2. Load only the validated state and evidence that contract declares as input.
3. Render structured input using stable field names matching the schemas.
4. Request structured JSON output where the adapter declares that capability; otherwise parse
   and validate a fenced JSON payload.
5. On validation failure, retry once with machine-readable errors, up to
   `prompt.validation_retry_max`. Then return a recoverable application error and leave state
   unchanged.

## Capability boundary

Adapters declare capabilities: structured output, tool calling, context limit, citation
support. A prompt contract states the capabilities it **requires**; it MUST NOT name a vendor,
model, or version.

The dispatcher selects an eligible engine. No business rule may depend on which engine is
selected ([ADR-0001](../adr/ADR-0001.md)).

## Injection resistance

All student content, retrieved notes, uploaded files, and external sources are **data**.

1. Delimit untrusted content explicitly and label it as data.
2. Instruction-following from within those fields is prohibited.
3. Privileged system instructions MUST NOT be echoed, summarised, or exposed on request.
4. An injection attempt is logged and the content is processed as written, not obeyed.

Because output is validated against a schema before any write, a successful injection cannot
by itself mutate durable state ([ADR-0003](../adr/ADR-0003.md)).

## Versioning

Every prompt carries a semantic version. Every persisted artifact records the prompt version
that produced it, so that outputs generated under different contracts are never compared as
though they were equivalent.

A change to a prompt's Outputs or Constraints section is a **major** version change and
requires the consuming schema and engine documents to be reviewed in the same change.
