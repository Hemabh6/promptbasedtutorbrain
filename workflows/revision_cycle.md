# Revision Cycle

**Trigger:** `next_due_at` is reached, or student elects early review.

1. Fetch the revision record and bounded source context.
2. Present the cue and collect an attempt before feedback.
3. Validate the outcome and confidence; retain skipped attempts distinctly.
4. Compute the next interval using configured policy and write an immutable attempt event.
5. If quality is `again` or `hard`, create a corrective teaching/practice candidate.

**Exit:** updated due date or surfaced scheduling overflow. The model never computes or persists scheduling state on its own.
