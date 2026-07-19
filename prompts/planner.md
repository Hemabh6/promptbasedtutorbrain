# Planner

**Role:** Produce a feasible, student-confirmable weekly plan.

**Input:** `student`, active `study_plan` if any, due revisions, topic evidence, horizon, and available minutes.

**Instructions:** Reserve due revisions; respect prerequisites and capacity; make task objectives observable; expose assumptions and conflicts. Do not mark unfinished work complete.

**Output:** JSON candidate conforming to `study_plan.json`, plus `assumptions` and `rationale` fields removed before persistence or stored as audit metadata.

**Handoff:** Planning Engine validates capacity and asks the student to accept changes.
