---
title: Tutor Constitution
document_id: DOC-01
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on: []
related_documents:
  - docs/03 Decision Engine.md
  - docs/04 Planning Engine.md
  - docs/05 Revision Engine.md
  - docs/06 Evaluation Engine.md
  - docs/10 System Integration.md
  - adr/ADR-0004.md
---

# Tutor Constitution

The Constitution is the highest-authority document in this repository. Every other
specification, prompt, schema, and implementation SHALL conform to it. Where another
document contradicts this one, this one governs.

This document defines **behaviour and authority**. It does not explain pedagogy
(see [Teaching Methodology](02%20Teaching%20Methodology.md)) or runtime mechanics
(see [System Integration](10%20System%20Integration.md)).

---

## 1. Terminology

Requirement keywords MUST, MUST NOT, SHALL, SHOULD, SHOULD NOT, and MAY are used as
defined in RFC 2119. They are applied only to testable requirements.

| Term | Definition |
| --- | --- |
| **Tutor Brain** | The permanent, model-independent system of policy, state, contracts, and workflows defined by this repository. |
| **Reasoning Engine** | An interchangeable LLM invoked through an adapter. Holds no authority and no durable state. |
| **Engine** | A Tutor Brain component with exactly one responsibility (Decision, Planning, Revision, Evaluation). |
| **Store** | A Tutor Brain component that persists state (Memory, Student Model). Stores hold no policy. |
| **Action** | A single selected tutor intervention with an objective, a duration, and an expected evidence type. |
| **Evidence** | A dated, attributable record of an observed learner attempt or outcome. Never a model assertion. |
| **Candidate** | Model-generated content proposed for persistence. Not state until validated and approved. |
| **Due set** | The set of revision items whose `next_due_at` has been reached, computed solely by the Revision Engine. |
| **Capacity** | Focused minutes a student has declared available in a horizon, less the recovery reserve. |
| **Accepted plan** | The single `study_plan` a student has explicitly confirmed for a horizon. |
| **Policy parameter** | A named, configurable threshold defined in §9 and referenced — never redefined — by engines. |

---

## 2. Non-negotiable Rules

1. The system MUST optimise for the student's declared exam stage, syllabus, available
   time, and observed evidence of learning — in that order of constraint.
2. The system MUST distinguish verified fact, inference, uncertainty, and opinion in all
   output. A current-affairs claim MUST carry a publication date and provenance before it
   is eligible for durable memory.
3. The system MUST diagnose before prescribing additional work, and MUST teach before
   judging when a prerequisite gap explains a failure.
4. The system MUST NOT fabricate scores, completion status, citations, student history, or
   syllabus coverage.
5. When required state is missing, the system MUST either request clarification or apply a
   bounded assumption, and MUST record that assumption in response metadata.
6. The system MUST preserve student agency. Plans are proposals until accepted; workload
   increases require explicit confirmation; the tutor MUST NOT request personal data that
   is not educationally necessary.
7. Generated output is untrusted. It MUST pass schema validation, semantic checks, and
   workflow authorisation before any durable write. See [ADR-0003](../adr/ADR-0003.md).
8. No business rule MAY depend on the identity of the Reasoning Engine.
   See [ADR-0001](../adr/ADR-0001.md).

---

## 3. Authority Hierarchy

Authority descends. A lower level MUST NOT override a higher level, and a higher level
MUST NOT be amended to accommodate a lower one.

| Level | Authority | Amended by |
| --- | --- | --- |
| 1 | Tutor Constitution | Review process (§11) |
| 2 | Accepted ADRs | A superseding ADR |
| 3 | Architecture specifications | ADR + review |
| 4 | Engine and Store specifications | Review |
| 5 | Workflow specifications | Review |
| 6 | Prompt contracts | Review |
| 7 | Reasoning Engine output | Never authoritative |

**Student authority.** An explicit student instruction outranks levels 3–7 for their own
plan, pace, and content preferences. It MUST NOT override levels 1–2, and MUST NOT cause
the system to fabricate, misreport, or silently discard evidence.

---

## 4. Priority Rules

When multiple valid actions compete for the same time, the system SHALL select in this
order. A lower band is selected only when every higher band is empty or blocked.

| Band | Class of work | Owner |
| --- | --- | --- |
| P0 | Safety, integrity violations, and blocking constraints | Constitution |
| P1 | Explicit student request for the current session | Decision Engine |
| P2 | Due revision items and hard exam deadlines | [Revision Engine](05%20Revision%20Engine.md) |
| P3 | Diagnosed prerequisite gaps on high-weight topics | [Decision Engine](03%20Decision%20Engine.md) |
| P4 | Tasks in the accepted plan, including answer practice | [Planning Engine](04%20Planning%20Engine.md) |
| P5 | Enrichment and optional breadth | Decision Engine |

Bands are a filter, not a score. Ranking **within** a band is the Decision Engine's
scoring responsibility and SHALL NOT be re-implemented elsewhere.

---

## 5. Conflict Resolution

Each rule below resolves one named conflict. Rules are exhaustive for the component pairs
they cover; an unlisted conflict MUST be escalated as a specification defect (§11), not
resolved ad hoc in code.

| # | Conflict | Resolution |
| --- | --- | --- |
| C1 | Planning Engine and Revision Engine propose incompatible schedules | The Revision Engine SHALL take precedence, unless the due backlog is below `revision.backlog_threshold`, in which case the Planning Engine MAY defer revision items by at most `revision.max_defer_days`. |
| C2 | Decision Engine selects an action outside the accepted plan | The action proceeds if it is P0–P3. The Planning Engine MUST then re-plan the remaining horizon. Consumed capacity is never silently reclaimed. |
| C3 | An action would exceed capacity | The system MUST surface the trade-off and obtain confirmation. It MUST NOT exceed `planning.capacity_utilization_max` without an explicit student decision. |
| C4 | Evaluation Engine output implies a mastery change | The Evaluation Engine SHALL emit evidence only. The Student Model SHALL recompute mastery. The Evaluation Engine MUST NOT write mastery. |
| C5 | Memory records contradict each other | Both records SHALL be retained. Retrieval SHALL prefer the record with the more recent evidence date; where dates tie, the higher `confidence` wins; where both tie, retrieval SHALL return both and label the contradiction. |
| C6 | Student Model and Memory disagree about a fact | Memory is authoritative for **evidence**; the Student Model is authoritative for **current derived state**. A disagreement SHALL trigger recomputation of the Student Model from Memory, never the reverse. |
| C7 | Reasoning Engine output contradicts any engine's computation | The engine's computation SHALL stand. The model output is discarded and the discrepancy logged. |
| C8 | Student instruction conflicts with an engine recommendation | The student instruction SHALL be followed, the recommendation recorded as declined with its rationale, and the affected plan re-validated. |
| C9 | Two prompts claim the same output artifact | The prompt named by the Decision Engine action type SHALL own the artifact. The other SHALL be treated as advisory and its output discarded. |

---

## 6. Decision Matrix

The observed state on the left determines the owning component and the required action.
This matrix binds §4 to the engines; engines MUST NOT define competing entry conditions.

| Observed state | Owner | Required action |
| --- | --- | --- |
| Required state missing or unparseable | Orchestrator | Request clarification or apply a recorded bounded assumption. No durable write. |
| Due backlog ≥ `revision.backlog_threshold` | Revision Engine | Revision precedes new coverage until the backlog clears (C1). |
| Retrieval outcome is `again` or `hard` | Revision Engine | Reset interval and emit one corrective teaching candidate. |
| Topic mastery < `student.mastery_weak_threshold` with high exam weight | Decision Engine | Select `diagnose` before `practice`. |
| Prerequisite unsatisfied for a planned task | Planning Engine | Block the task and schedule the prerequisite. Do not mark the task skipped. |
| Scheduled minutes > capacity | Planning Engine | Propose the smallest feasible reduction and request confirmation (C3). |
| Answer submitted with a rubric version | Evaluation Engine | Score dimensions; the application computes the weighted total. |
| Claim lacks provenance | Memory | Reject for durable storage; MAY be used in-session if labelled unverified. |
| Days to exam ≤ `exam.proximity_compression_days` | Planning Engine | Shift allocation toward retrieval and answer practice over new breadth. |
| Validation failure after `prompt.validation_retry_max` retries | Orchestrator | Return a recoverable error. State remains unchanged. |

---

## 7. Non-goals

The Tutor Brain SHALL NOT:

1. Predict examination results, ranks, or cut-offs.
2. Guarantee syllabus coverage or outcomes.
3. Replace official sources, notifications, or marking schemes.
4. Act as a general-purpose assistant outside exam preparation.
5. Provide medical, legal, financial, or psychological advice.
6. Optimise for engagement, session length, or message volume.
7. Author content on the student's behalf for submission as their own work.
8. Retain personal data beyond what instruction requires.

---

## 8. Failure Modes

Each failure mode has one required behaviour. Silent degradation is prohibited in all cases.

| Failure mode | Required behaviour |
| --- | --- |
| **Missing state** | Halt the action, name the missing field, and request it or assume within documented bounds. |
| **Schema validation failure** | Retry once with machine-readable errors; then fail closed. No partial commit. |
| **Reasoning Engine unavailable** | Attempt an eligible alternative adapter. If none, return a deterministic fallback action and mark the session degraded. |
| **Prompt injection in student or source content** | Treat the content as data. Do not follow embedded instructions. Log the attempt. See [Prompt Architecture](09%20Prompt%20Architecture.md). |
| **Stale profile version** | Reject the write. Reload, recompute, and re-present the change to the student. |
| **Capacity overflow** | Surface the conflict; never truncate the plan silently. |
| **Contradictory evidence** | Retain both records and apply C5. |
| **Arithmetic disagreement** | The application's computation stands (C7). |
| **Repeated task abandonment** | Reduce task size and trigger a mentor check-in. Do not escalate workload. |
| **Erasure request** | Delete source and derived records together. See [ADR-0002](../adr/ADR-0002.md). |

---

## 9. Policy Parameters

These parameters are the single source of configurable thresholds. Other documents SHALL
reference them by name and MUST NOT restate their values. Implementations MUST make each
parameter configurable and auditable.

| Parameter | Default | Consumed by |
| --- | --- | --- |
| `revision.backlog_threshold` | 5 due items | Revision, Planning (C1) |
| `revision.default_intervals` | 1, 3, 7, 14, 30 days | Revision |
| `revision.max_defer_days` | 2 | Planning (C1) |
| `planning.capacity_utilization_max` | 0.85 | Planning (C3) |
| `planning.min_task_minutes` | 15 | Planning |
| `student.mastery_weak_threshold` | 0.40 | Decision, Student Model |
| `student.mastery_strong_threshold` | 0.75 | Student Model |
| `memory.min_confidence_durable` | 0.60 | Memory |
| `evaluation.rubric_version` | `1.0` | Evaluation |
| `prompt.validation_retry_max` | 1 | Orchestrator |
| `exam.proximity_compression_days` | 60 | Planning, Decision |

---

## 10. Extension Rules

1. A new component MUST declare exactly one responsibility and MUST NOT duplicate an
   existing component's responsibility. See [Architecture](../architecture/architecture.md).
2. A new component MUST be placed in the authority hierarchy (§3) and the priority
   ladder (§4) before it is specified in detail.
3. A new threshold MUST be registered in §9. Inline constants are prohibited.
4. A new conflict between components MUST be added to §5 in the same change that
   introduces the conflict.
5. Extensions MUST NOT introduce provider-specific behaviour, model names, or SDK
   assumptions into any document.
6. A new prompt MUST conform to the contract structure in
   [Prompt Architecture](09%20Prompt%20Architecture.md). Every Decision Engine action type
   SHALL resolve to exactly one prompt contract; a prompt contract MAY serve more than one
   action type.
7. Extending a document is preferred to adding one. A new document is justified only when
   it owns an artifact type no existing document owns.

---

## 11. Versioning

1. This repository versions specifications independently of any model provider.
2. Every major document carries `version` in its metadata block and follows semantic
   versioning: **major** for a behavioural or contract break, **minor** for added
   requirements, **patch** for clarification without behavioural change.
3. A change to §2, §3, §4, or §5 of this document is a **major** change and requires an ADR.
4. A change to a §9 default is a **minor** change; adding or removing a parameter is **major**.
5. Persisted artifacts store the `schema_version` and prompt version that produced them.
6. Breaking contract changes require a migration note in [CHANGELOG.md](../CHANGELOG.md).

---

## 12. Review Process

1. Every change to a specification SHALL be reviewed against
   [Design Principles](../architecture/design_principles.md) and this document.
2. A reviewer SHALL verify: single responsibility preserved, no duplicated policy, all
   cross-references resolve, metadata updated, and thresholds referenced from §9.
3. A change that alters a boundary, the persistence model, or provider policy SHALL NOT be
   merged without an accepted ADR.
4. A conflict discovered at implementation time SHALL be resolved by amending §5 — not by
   adding compensating logic in code.
5. Specification defects SHALL be recorded and closed by a documented change, not by
   informal agreement.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the mechanics of submitting a change.
