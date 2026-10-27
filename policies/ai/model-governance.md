# Model Governance Principles

Owner: AI/model owner. Scope: foundation models, fine-tuned models, classifiers, embeddings, and model-serving configuration.

### AI-MOD-001 Model registry
- **MUST:** record model identifier, version, provider, owner, purpose, permitted data, risk classification, limits, and evaluation suite.
- **MUST:** use only approved model versions in controlled environments.

### AI-MOD-002 Model change
- **MUST:** assess behavior, safety, privacy, performance, latency, availability, and cost impact before a material model change.
- **MUST:** retain the prior version and rollback path where production use requires continuity.

### AI-MOD-003 Provider and data boundary
- **MUST:** review provider terms, data processing, residency, retention, training use, access, and contractual controls before adoption.

### AI-MOD-004 Monitoring
- **MUST:** monitor model errors, latency, usage, cost, evaluation results, safety events, and drift signals appropriate to risk.

## Exceptions
A model exception requires AI owner, security/privacy/risk review, documented evidence, mitigation, human approver, and expiry.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| AI-MOD-001 | Registry and approved-version check | AI governance CI |
| AI-MOD-002 | Evaluation evidence and rollback check | AI release gate |
| AI-MOD-003 | Provider/data-boundary checklist | Architecture/security review |
| AI-MOD-004 | Required telemetry metadata | AI operations check |
