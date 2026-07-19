# Answer Evaluation Workflow

**Trigger:** student submits a complete answer for feedback.

1. Validate question, answer text, command word, and rubric version.
2. Invoke the evaluator with only supplied references and context.
3. Validate output against `answer.json`; calculate weighted total in application code.
4. Present evidence-backed feedback and label unverified claims.
5. On student approval, persist the answer evaluation and create one targeted practice or revision candidate.

**Exit:** an immutable answer record with traceable rubric evidence, or a validation failure that leaves student state unchanged.
