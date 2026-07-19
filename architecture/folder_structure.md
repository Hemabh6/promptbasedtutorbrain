---
title: Folder Structure
document_id: ARCH-03
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

# Folder Structure

## Ownership

| Path | Owns | Must not contain |
| --- | --- | --- |
| `docs/` | Product policy and component specifications | Provider SDK instructions |
| `prompts/` | Portable reasoning contracts | Secrets, durable state, policy |
| `schemas/` | Machine-validated data shapes | Business logic hidden in prose |
| `architecture/` | Boundaries and engineering constraints | Feature-specific tutorial text |
| `workflows/` | Trigger-to-outcome operational flows | Undocumented data fields |
| `adr/` | Accepted architectural decisions | Transient implementation notes |

## Conventions

1. File names are **stable public references**. Renaming a file is a breaking change and
   requires a CHANGELOG entry.
2. Numbered documents in `docs/` express reading order, not runtime dependency.
3. Every major document carries the metadata block defined in
   [CONTRIBUTING.md](../CONTRIBUTING.md).
4. Cross-references use relative Markdown links. Spaces in filenames are encoded as `%20`.
5. Each folder carries a `README.md` that indexes its contents and states what the folder owns.

## Adding to the repository

Extending an existing document is preferred to adding one. A **new document** is justified
only when it owns an artifact type no existing document owns.

A **new folder** is justified only when it owns a distinct artifact type with a documented
lifecycle. Otherwise, extend the closest existing area. See
[Constitution §10](../docs/01%20Tutor%20Constitution.md#10-extension-rules).
