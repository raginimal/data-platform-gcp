# AI Engineering Principles

Owner: AI engineering owner with product, security, data, and risk stakeholders. Scope: models, prompts, RAG, tools, evaluations, guardrails, and AI-assisted code.

### AI-001 Approved use
- **MUST:** use approved tools, models, providers, data-processing locations, and deployment patterns.
- **MUST:** document intended use, prohibited use, owner, risk, and human oversight for material AI capability.

### AI-002 Human oversight
- **MUST:** define escalation and human review for consequential, uncertain, unsafe, or irreversible outcomes.
- **MUST NOT:** allow AI output or an AI reviewer to approve its own exception or bypass deterministic controls.

### AI-003 Risk and reliability
- **MUST:** identify hallucination, prompt injection, data leakage, misuse, bias, availability, cost, and model-drift risks relevant to the use case.
- **SHOULD:** use grounding, validation, refusal, rate limits, monitoring, and safe failure behavior.

### AI-004 Change control
- **MUST:** version and review material model, prompt, retrieval, tool, evaluation, and guardrail changes.
- **MUST:** run appropriate regression evaluations before release.

### AI-005 AI-generated code
- **MUST:** review, test, scan, and license-check AI-generated code exactly as human-written code.

## Exceptions
AI policy exceptions require accountable product/AI and security or risk approval, documented mitigation, evaluation evidence, owner, and expiry.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| AI-001 | Approved model/tool registry check | AI governance |
| AI-002 | Human-oversight metadata check | AI policy check |
| AI-003 | Risk and guardrail checklist | AI review |
| AI-004 | Evaluation and version-diff gate | AI CI |
| AI-005 | AI-assistance disclosure and standard scanners | PR/security CI |
