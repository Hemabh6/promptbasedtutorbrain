---
title: Daily Workflow
document_id: WF-DAILY
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/03 Decision Engine.md
  - docs/10 System Integration.md
related_documents:
  - workflows/weekly.md
  - workflows/revision_cycle.md
---

# Daily Workflow

**Trigger:** the student starts a session, or a scheduled daily run fires.

**Owner:** Orchestrator. This workflow selects and adapts within the accepted plan; it does
not create plans.

## Sequence

1. Load the accepted plan, remaining time, the due set, and recent evidence.
2. Request one ranked action from the [Decision Engine](../docs/03%20Decision%20Engine.md).
   Expose its rationale and any recorded assumption to the student.
3. Resolve the action type to its prompt contract and run it through an eligible adapter.
4. Capture the student's attempt, completion, skip reason, or correction.
5. Validate the resulting answer, revision, and memory candidates. Persist approved events
   atomically.
6. Re-rank the next action only if time remains or the student requests it.

## Rules

- The action selected in step 2 MUST carry a `fallback_action`; a session may end with less
  time than the action requires.
- Step 5 is atomic. A validation failure leaves state unchanged
  ([ADR-0003](../adr/ADR-0003.md)).
- An action selected outside the accepted plan signals the
  [Planning Engine](../docs/04%20Planning%20Engine.md) to re-plan the remaining horizon
  ([Constitution C2](../docs/01%20Tutor%20Constitution.md#5-conflict-resolution)).
- Completion MUST NOT be inferred from elapsed time or from the student advancing.

**Exit:** a completed evidence event, an explicitly deferred task, or a recoverable failure.
The session summary states what changed and what is due next.
