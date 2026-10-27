# Architecture Principles

Owner: architecture owner or technical lead. Scope: system structure, boundaries, interfaces, resilience, and operations.

### ARCH-001 Separation of concerns
- **MUST:** separate domain logic, interfaces, infrastructure, configuration, policy, and delivery concerns.
- **SHOULD:** keep modules cohesive and expose narrow interfaces.
- **Automation:** inspect dependency direction and forbidden cross-layer imports.

### ARCH-002 Explicit boundaries
- **MUST:** define ownership, inputs, outputs, trust boundaries, and failure behavior for each service or major module.
- **SHOULD:** prefer loose coupling and independently testable components.
- **Human decision:** approve new services, data stores, or boundary changes.

### ARCH-003 API and contract compatibility
- **MUST:** version externally consumed APIs and data contracts.
- **MUST:** define compatibility and deprecation behavior before a breaking change.
- **SHOULD:** validate schemas at trust boundaries.

### ARCH-004 Resilience and scalability
- **MUST:** document availability, failure, timeout, retry, idempotency, and recovery expectations for production boundaries.
- **SHOULD:** design capacity and scaling assumptions explicitly.

### ARCH-005 Observability
- **MUST:** provide health signals, structured logs, relevant metrics, and runbook ownership for production services.
- **SHOULD:** add traces where they explain distributed behavior.

### ARCH-006 Infrastructure as code
- **MUST:** represent production infrastructure as reviewed, reproducible code.
- **MUST NOT:** introduce unmanaged production resources without an approved transition plan.

### ARCH-007 Architecture decisions
- **MUST:** create an ADR for a new architectural component, external platform, system boundary, significant data change, AI platform, or operational-risk decision.
- **Human decision:** architecture owner approves the decision and exceptions.

## Exceptions
Use the standard exception record and link an ADR when the exception changes architecture, security, data, or operational risk.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| ARCH-001 | Dependency-direction rules | Architecture CI |
| ARCH-002 | Service-contract presence check | Governance CI |
| ARCH-003 | API/schema compatibility check | Contract CI |
| ARCH-005 | Observability and runbook checks | Architecture policy check |
| ARCH-006 | IaC presence and unmanaged-resource scan | Infrastructure CI |
| ARCH-007 | ADR trigger and link check | PR governance |
