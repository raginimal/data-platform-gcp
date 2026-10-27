# AI Engineering Policy

The normative source of truth is under `policies/ai/`: `ai-engineering-principles.md`, `model-governance.md`, `prompt-governance.md`, and `evaluation-principles.md`. Their stable IDs are future automation targets.

Agent-specific controls are defined in `policies/ai/agent-governance.md`. The repository framework is documented in `docs/agents-and-skills.md` and uses the shared finding format in `docs/agent-output.md`.

## Approved use
Use only organization-approved AI tools, models, endpoints, and data-processing locations. Record the tool/model and purpose for material AI-assisted changes.

## Data handling
Do not send confidential, personal, regulated, customer, production, credential, or proprietary data to an AI system unless explicitly approved for that classification and purpose. Sanitize prompts and outputs.

## Model and prompt changes
Version model identifiers, configuration, prompts, retrieval sources, evaluation datasets, guardrails, and safety settings. Material changes require review and an ADR when they change risk, behavior, cost, or data flow.

## Evaluation and controls
- Define intended use, unacceptable use, quality targets, and failure modes.
- Maintain representative, permissioned evaluation data without exposing sensitive data.
- Measure quality, latency, cost, refusal behavior, hallucination risk, and guardrail violations as applicable.
- Use input validation, output validation, grounding, rate limits, abuse controls, and human escalation for consequential decisions.
- Do not present unverified model output as fact or allow a model to make irreversible decisions without an approved control.

## Code assistance
AI-generated code must be reviewed, tested, dependency-scanned, secret-scanned, and checked for license or provenance concerns. AI agents are advisory unless a finding has been converted into a deterministic policy.
