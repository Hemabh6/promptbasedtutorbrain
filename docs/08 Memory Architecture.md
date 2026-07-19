# Memory Architecture

## Layers

| Layer | Contents | Write authority | Retention |
| --- | --- | --- | --- |
| Profile | stable preferences and constraints | student/app | until changed or deleted |
| Working context | current session and selected task | application | session-bounded |
| Learning ledger | dated evidence of attempts and outcomes | validated workflow | durable |
| Retrieval index | compact facts derived from ledger | memory service | rebuildable |

The `memory` schema represents a portable snapshot, not a model conversation transcript. Never persist hidden reasoning, provider logs, credentials, or unvalidated model assertions.

## Write path

The workflow proposes memory candidates with source event IDs and confidence. Validation checks schema, policy, duplication, and provenance. Approved candidates are appended as immutable records; derived summaries may be rebuilt. A model cannot directly overwrite memory.

## Retrieval

Retrieve by student, topic, recency, evidence strength, and task relevance. Return the minimum context necessary to solve the current action and label derived summaries. Contradictory records coexist until resolved by newer, higher-quality evidence.

## Privacy

Store only educationally necessary data. Partition by `student_id`, enforce access control in the application, support erasure, and redact personal identifiers before external model calls where possible.
