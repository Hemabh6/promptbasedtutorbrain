# Contributing

## Scope

This repository is a specification source of truth. Keep product policy in `docs/`, executable data contracts in `schemas/`, reasoning instructions in `prompts/`, and irreversible choices in `adr/`.

## Change process

1. Read the linked specifications before editing a contract.
2. Make small, coherent changes with relative Markdown links.
3. Update every affected prompt, schema, workflow, and architecture document in the same change.
4. Add or amend an ADR when changing a boundary, persistence model, or model-provider policy.
5. Update `CHANGELOG.md` for user-visible or contract changes.

## Quality bar

- Use RFC 2119 terms (MUST, SHOULD, MAY) only for testable requirements.
- Do not embed provider-specific APIs, model names, or secrets.
- Preserve stable identifiers and schema versions; document migrations instead of silently repurposing fields.
- Validate JSON examples against their schema before merging.

## Commits and reviews

Use Conventional Commit style, for example `docs: define revision scheduling policy`. Reviews should verify cross-references, schema compatibility, and that generated content is treated as untrusted until validated.
