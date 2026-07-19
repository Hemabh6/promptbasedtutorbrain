# Prompt Architecture

## Portable prompt contract

Each prompt in [`prompts/`](../prompts/) has a role, required input, output shape, constraints, and handoff. The adapter combines it with the Constitution, validated state, and a provider-specific transport envelope. Prompt text MUST NOT be the only source of policy: code validates inputs and outputs.

## Context assembly

1. Select the specialised prompt for a Decision Engine action.
2. Load only required validated state and evidence.
3. Render structured input using stable field names.
4. Request structured JSON output when provider capability allows; otherwise parse and validate a fenced JSON payload.
5. On validation failure, retry once with machine-readable errors, then return a recoverable application error.

## Capability boundary

Adapters expose capabilities such as structured output, tool calling, context limit, and citation support. Prompts state desired capabilities but never name a vendor or model. The dispatcher chooses an eligible engine; no business rule depends on which engine is chosen.

## Injection resistance

Treat all student content, retrieved notes, and external sources as data. Delimit them, prohibit instruction-following from those fields, and never expose privileged system instructions. See [ADR-0001](../adr/ADR-0001.md).
