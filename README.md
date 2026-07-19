# Prompt-Based Tutor Brain

Prompt-Based Tutor Brain is a model-agnostic specification for a long-lived UPSC tutoring system. The **Tutor Brain** owns policy, state, workflows, prompts, and validation contracts; an LLM is a replaceable reasoning engine invoked through an adapter.

Phase 1 defines the contracts needed to implement a reliable tutoring product without coupling it to ChatGPT, Claude, Gemini, or a future model.

## System map

- [Tutor Constitution](docs/01%20Tutor%20Constitution.md) sets non-negotiable tutor behaviour.
- [Decision Engine](docs/03%20Decision%20Engine.md) selects the next intervention from student state.
- [Student Model](docs/07%20Student%20Model.md) and [Memory Architecture](docs/08%20Memory%20Architecture.md) define persistent state.
- [Prompt Architecture](docs/09%20Prompt%20Architecture.md) defines portable model calls.
- [System Integration](docs/10%20System%20Integration.md) defines runtime boundaries.

## Repository guide

| Area | Purpose |
| --- | --- |
| `docs/` | Product and engine specifications |
| `prompts/` | Model-neutral prompt contracts |
| `schemas/` | Versioned JSON Schema state contracts |
| `architecture/` | Boundaries, principles, and repository conventions |
| `workflows/` | Repeatable operational sequences |
| `adr/` | Decisions that constrain implementation |

## Implementation order

1. Implement schema validation and state persistence.
2. Implement the decision engine as deterministic policy around an LLM adapter.
3. Add planning, teaching, revision, and evaluation workflows.
4. Instrument outcomes and iterate only through documented ADRs.

## Status

Phase 1 is a specification baseline, not a runnable application. See [CHANGELOG.md](CHANGELOG.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
