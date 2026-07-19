# Architecture Decision Records

An ADR records a decision that constrains implementation. ADRs are **immutable once accepted**:
supersede one with a later record rather than editing its decision.

| ADR | Decision | Status |
| --- | --- | --- |
| [ADR-0001](ADR-0001.md) | Separate Tutor Brain policy from reasoning engines | Accepted |
| [ADR-0002](ADR-0002.md) | Use append-only learning evidence with derived summaries | Accepted |
| [ADR-0003](ADR-0003.md) | Validate structured outputs before state mutation | Accepted |
| [ADR-0004](ADR-0004.md) | Establish a single authority hierarchy for component conflicts | Accepted |

## Required structure

Every ADR contains these sections, in order:

**Context** · **Problem** · **Decision** · **Alternatives Considered** · **Tradeoffs** ·
**Consequences** · **Future Considerations**

Alternatives MUST state why each was rejected — an alternatives section without rejection
reasoning records nothing. Tradeoffs MUST name the accepted cost, not only the benefit.

## When an ADR is required

A change that alters a system boundary, the persistence model, provider policy, or the
authority hierarchy MUST NOT be merged without an accepted ADR. See
[Constitution §12](../docs/01%20Tutor%20Constitution.md#12-review-process).
