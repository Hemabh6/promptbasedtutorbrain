# System Integration

## Runtime components

`Client → API → Orchestrator → Decision Engine → Prompt Adapter → Reasoning Engine`

The Orchestrator validates requests, loads state, invokes the deterministic Decision Engine, selects an adapter, validates generated output, and writes approved events. The Reasoning Engine is stateless from the system's perspective and may be changed per request.

## Required interfaces

- **State store:** versioned read/write of profile, plans, memory, revisions, and answers.
- **Engine adapter:** `capabilities`, `generate`, and normalized error/result types.
- **Knowledge source:** source retrieval with URL, publisher, publication date, access date, and trust tier.
- **Clock/queue:** time-zone-aware due review and scheduled plan operations.

## Failure handling

If a model call, parse, validation, or persistence step fails, do not mutate durable state. Return the action status, a retry-safe correlation ID, and a deterministic fallback where available. Log prompt version, schema version, input record IDs, adapter capability set, and outcome—not raw sensitive content by default.

## Versioning

Every persisted artifact stores schema and prompt version. Backward reads are supported by migrations; breaking contract changes require an ADR and changelog entry.
