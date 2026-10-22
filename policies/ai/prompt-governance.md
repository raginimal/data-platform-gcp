# Prompt Governance Principles

Owner: AI product or prompt owner. Scope: system prompts, templates, retrieval instructions, tool instructions, and prompt configuration.

### AI-PRM-001 Version control
- **MUST:** version prompts and record owner, purpose, model assumptions, input/output contract, grounding sources, guardrails, and change reason.
- **MUST NOT:** place secrets, credentials, unnecessary PII, or confidential data directly in prompts.

### AI-PRM-002 Prompt security
- **MUST:** address prompt injection, instruction conflict, data exfiltration, unsafe tool use, and untrusted retrieved content.
- **SHOULD:** separate trusted instructions from untrusted user and retrieved content.

### AI-PRM-003 Change review
- **MUST:** evaluate material prompt changes for quality, safety, grounding, latency, cost, and regression.
- **MUST:** obtain human review for prompts that affect decisions, tools, sensitive data, or safety behavior.

### AI-PRM-004 Observability
- **MUST:** define safe prompt/output telemetry and redaction; do not log sensitive payloads by default.

## Exceptions
A prompt exception requires AI owner and appropriate security/data/risk approval, mitigation, test evidence, and expiry.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| AI-PRM-001 | Prompt metadata and secret scan | AI governance CI |
| AI-PRM-002 | Injection/tool-boundary test suite | AI security CI |
| AI-PRM-003 | Prompt diff and evaluation gate | AI review |
| AI-PRM-004 | Telemetry/redaction configuration check | AI operations |
