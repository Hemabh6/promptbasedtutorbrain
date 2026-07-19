# Revision Engine

## Goal

Revision converts learning evidence into scheduled retrieval, not repeated passive reading. It owns `revision.json` records and exposes due review candidates to the Decision Engine.

## Scheduling policy

On a successful retrieval, increase the interval; on an unsuccessful retrieval, reset to a short interval and attach a targeted corrective task. Initial defaults are 1, 3, 7, 14, and 30 days, adjusted only by observed recall quality, confidence calibration, and exam proximity. The implementation MUST make the algorithm parameters configurable and auditable.

## Review protocol

1. Present a cue before notes.
2. Capture response quality and confidence.
3. Reveal corrective explanation only after an attempt.
4. Persist a validated outcome and compute `next_due_at`.

Reviews marked skipped remain due; they are not failed attempts. Review load is capped by the accepted daily plan; overflow is surfaced to re-planning.
