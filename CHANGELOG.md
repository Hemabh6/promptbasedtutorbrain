# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/) conventions. This
repository versions its specifications independently of any model provider.

## [0.2.0] - 2026-07-19

Phase 1 hardening. No new features; no architectural redesign.

### Added

- Tutor Constitution expanded into a governing specification: terminology, authority
  hierarchy, priority rules, a nine-entry conflict resolution table, decision matrix,
  non-goals, failure modes, extension rules, versioning, and review process.
- Policy parameter registry (Constitution §9) as the single source of configurable thresholds.
- [ADR-0004](adr/ADR-0004.md) recording the authority hierarchy and conflict precedence model.
- Consistent metadata blocks on every major document.
- Architecture document sections for system layers, component responsibilities, execution
  flow, data flow, module dependency rules, and boundary definitions.
- Nine-section contract structure applied to all nine prompt documents.
- Alternatives Considered, Problem, Tradeoffs, and Future Considerations sections on all ADRs.

### Changed

- Component responsibilities narrowed to remove overlap. The Revision Engine owns the due set
  and interval policy; the Planning Engine owns calendar allocation and consumes the due set
  as a fixed reservation. The Evaluation Engine emits evidence only and no longer implies
  mastery updates.
- Student Model and Memory boundary made explicit: Memory is authoritative for evidence, the
  Student Model for current derived state, and the latter is rebuildable from the former.
- `architecture/architecture.md` now owns static structure; `docs/10 System Integration.md`
  owns runtime contracts. Observability moved to the latter.
- README restructured as a project landing page with vision, roadmap, and explicit
  IS / IS NOT scope statements.
- Schemas reformatted for readability and expanded with realistic fields: exam stage and
  attempt, optional subject, working-professional flag, learning style, constraints, derived
  strengths/weaknesses and performance metrics, plan conflicts and task provenance, answer
  outline and unverified-claim reasons, revision ease factor and attempt lineage, memory
  provenance and contradiction links.
- Decision Engine action types extended to cover every prompt contract; each action type now
  resolves to exactly one prompt.

### Compatibility

- Schemas remain at `schema_version` `1.0`; all additions are optional fields.
- Schema documents target JSON Schema Draft 2020-12.
- Changes to required fields or semantics require a new schema version and migration guidance.

## [0.1.0] - 2026-07-19

### Added

- Phase 1 Tutor Brain constitution, engines, workflows, prompts, schemas, architecture
  documents, and ADRs.
- Model-agnostic contracts for persistent student state and generated outputs.

### Compatibility

- Schema documents target JSON Schema Draft 2020-12.
