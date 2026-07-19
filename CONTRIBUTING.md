# Contributing

This repository is a specification source of truth. It contains no code, and contributions
that add code, APIs, databases, or infrastructure are out of scope.

## Scope

| Keep | In |
| --- | --- |
| Product policy and component specifications | `docs/` |
| Machine-validated data contracts | `schemas/` |
| Reasoning instructions | `prompts/` |
| Boundaries and engineering constraints | `architecture/` |
| Trigger-to-outcome sequences | `workflows/` |
| Irreversible choices | `adr/` |

## Change process

1. Read the specifications your change touches, and
   [Constitution §10](docs/01%20Tutor%20Constitution.md#10-extension-rules).
2. Make small, coherent changes using relative Markdown links.
3. Update **every** affected document in the same change — prompt, schema, workflow, and
   architecture drift together or not at all.
4. Add or amend an ADR when changing a boundary, the persistence model, provider policy, or
   the authority hierarchy.
5. Update the document metadata block and [`CHANGELOG.md`](CHANGELOG.md).

## Document metadata

Every **specification** document begins with this block, using the same field order
throughout. Folder `README.md` index files and the root `README.md`, `CONTRIBUTING.md`, and
`CHANGELOG.md` are navigational and carry no metadata block — they specify nothing and are
never depended on.

```yaml
---
title: <human-readable title>
document_id: <DOC-nn | ARCH-nn | ADR-nnnn | PROMPT-NAME | WF-NAME>
version: <semver>
status: Draft | Accepted | Superseded
owner: <team or role, never an individual>
last_updated: <YYYY-MM-DD>
depends_on:
  - <repo-relative path>
related_documents:
  - <repo-relative path>
---
```

`depends_on` lists documents this one cannot be understood without. `related_documents` lists
documents a reader will likely want next. Paths are repo-relative and unencoded; inline
Markdown links encode spaces as `%20`.

## Quality bar

- Use RFC 2119 terms (MUST, SHOULD, MAY) only for testable requirements. Prefer specification
  language over `try`, `usually`, `normally`, `might`.
- Define behaviour, not concepts. "Revision is important" is not a requirement; "the Revision
  Engine SHALL take precedence unless the backlog is below `revision.backlog_threshold`" is.
- Every configurable value belongs in
  [Constitution §9](docs/01%20Tutor%20Constitution.md#9-policy-parameters). Inline constants
  are rejected.
- Define a concept once and link to it. Restating another document is a defect, not emphasis.
- Do not embed provider-specific APIs, model names, SDKs, or secrets.
- Preserve stable identifiers and schema versions. Document migrations rather than silently
  repurposing fields.
- Validate JSON examples against their schema before merging.

## Prompt contracts

Every file in `prompts/` implements the nine-section structure defined in
[Prompt Architecture](docs/09%20Prompt%20Architecture.md). A missing section is a defect. A
change to Outputs or Constraints is a major version bump and requires reviewing the consuming
schema and engine documents in the same change.

## Review checklist

- [ ] Each component still owns exactly one responsibility.
- [ ] No policy is duplicated across documents.
- [ ] All cross-references resolve.
- [ ] Metadata `version` and `last_updated` are current.
- [ ] Thresholds are referenced from Constitution §9, not restated.
- [ ] Any new component-pair conflict is added to Constitution §5.
- [ ] Generated content is treated as untrusted until validated.
- [ ] An ADR accompanies any boundary, persistence, or provider-policy change.

## Commits

Use Conventional Commit style, for example `docs: define revision scheduling precedence`.
