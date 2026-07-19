# JSON Schemas

Machine-validated state contracts. JSON Schema Draft 2020-12.

| Schema | Represents | Specified by |
| --- | --- | --- |
| [`student.json`](student.json) | Current learner state | [Student Model](../docs/07%20Student%20Model.md) |
| [`memory.json`](memory.json) | One durable evidence or knowledge record | [Memory Architecture](../docs/08%20Memory%20Architecture.md) |
| [`revision.json`](revision.json) | One retrievable item and its attempt history | [Revision Engine](../docs/05%20Revision%20Engine.md) |
| [`study_plan.json`](study_plan.json) | A horizon's allocated work | [Planning Engine](../docs/04%20Planning%20Engine.md) |
| [`answer.json`](answer.json) | One rubric evaluation | [Evaluation Engine](../docs/06%20Evaluation%20Engine.md) |

## Rules

1. Every instance carries `schema_version`. Persisted artifacts also record the prompt version
   that produced them.
2. Schema validation is **necessary but not sufficient**. Cross-record consistency, capacity,
   prerequisite satisfaction, and authorisation are checked in application code.
3. `additionalProperties` is `false` throughout. Undeclared fields are a validation failure,
   not a forward-compatibility mechanism.
4. Thresholds referenced in `description` text are defined in
   [Constitution §9](../docs/01%20Tutor%20Constitution.md#9-policy-parameters) and MUST NOT be
   hardcoded as schema constraints.
5. A change to a required field or to field semantics requires a new `schema_version`,
   migration guidance, and a [CHANGELOG](../CHANGELOG.md) entry.
