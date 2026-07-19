# Design Principles

1. **Policy outside the model.** Code owns authorization, scheduling, scoring arithmetic, and persistence.
2. **Evidence before inference.** Persist source events and distinguish them from summaries.
3. **Progressive disclosure.** Load the smallest context and ask the smallest useful question.
4. **Recoverable operations.** Validate before writes; make retries idempotent.
5. **Student agency.** Make plans inspectable, editable, and confirmable.
6. **Portable reasoning.** Depend on declared capabilities, never a model identity.
7. **Measurable learning.** Track attempts, recall, and rubric evidence—not conversational fluency.
