---
title: Monthly Workflow
document_id: WF-MONTHLY
version: 1.0.0
status: Accepted
owner: tutor-brain-architecture
last_updated: 2026-07-19
depends_on:
  - docs/04 Planning Engine.md
related_documents:
  - workflows/weekly.md
  - docs/07 Student Model.md
---

# Monthly Workflow

**Trigger:** a calendar month boundary, or a student-selected cycle start.

**Owner:** [Planning Engine](../docs/04%20Planning%20Engine.md). This workflow sets capacity
assumptions and outcomes; it does not produce a schedule.

## Sequence

1. Review syllabus coverage, mastery evidence, rubric trends, and plan adherence.
2. Identify bottlenecks by **evidence quality**, not by time spent.
3. Set measurable monthly outcomes and high-level topic allocation.
4. Reserve mock, answer-practice, and revision capacity around known deadlines.
5. Emit weekly planning inputs.

## Rules

- The workflow MUST NOT produce an unreviewable month-long daily schedule. Daily task
  instances belong to the [weekly workflow](weekly.md).
- Rubric trends MUST be compared only within a single `rubric_version`.
- Within `exam.proximity_compression_days` of the exam, allocation shifts toward retrieval and
  answer practice over new breadth.
- Coverage is measured from evidence, never from `current_focus` or intent
  ([Student Model](../docs/07%20Student%20Model.md)).

**Exit:** confirmed outcomes, recorded capacity assumptions, named risks, and the first weekly
planning trigger.
