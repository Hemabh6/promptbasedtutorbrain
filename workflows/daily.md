# Daily Workflow

**Trigger:** student starts a session or scheduled daily run.

1. Load accepted plan, time remaining, due revisions, and recent evidence.
2. Ask the Decision Engine for one ranked action; expose its rationale and any assumption.
3. Run the specialised prompt through an eligible reasoning adapter.
4. Capture the student's attempt, completion, skip reason, or correction.
5. Validate resulting answer/revision/memory candidates and persist approved events atomically.
6. Re-rank the next action only if time remains or the student requests it.

**Exit:** a completed evidence event, an explicitly deferred task, or a recoverable failure. A session summary states what changed and what is due next.
