# Architecture

## Boundary model

The system has four replaceable boundaries: interface, application orchestration, durable state, and reasoning provider. The Tutor Brain is the policy and data contract spanning the middle two; an LLM sits behind the reasoning-provider boundary.

```text
User Interface
  ↓ validated command
Application Orchestrator ── State Store
  ↓ action request                 ↑ approved events
Decision / Planning / Revision / Evaluation services
  ↓ prompt + bounded context
Reasoning Adapter ── interchangeable LLM
```

## Trust boundaries

The client, LLM output, retrieved web content, and imported files are untrusted. Only application services can persist state, calculate scores, schedule reviews, or authorize external actions. Model tools, if enabled, are allow-listed and receive least-privilege arguments.

## Observability

A trace correlates user command, input record versions, decision, prompt version, engine capability profile, validation result, and state mutations. Metrics track completion, recall quality, plan load, retries, and evaluator calibration without treating a provider's token usage as learning evidence.
