# Security Principles

Owner: security owner. Scope: code, data, infrastructure, identities, dependencies, and operations.

### SEC-001 Secure by default
- **MUST:** treat external input, dependencies, model output, and infrastructure configuration as untrusted until validated.
- **MUST:** apply secure defaults and document security-sensitive assumptions.

### SEC-002 Defense in depth
- **MUST:** combine preventive, detective, and corrective controls for material trust boundaries.
- **SHOULD:** minimize blast radius and fail safely.

### SEC-003 Secure development
- **MUST:** apply input validation, output validation, authorization, safe error handling, and secure logging.
- **MUST:** perform security review for identity, sensitive data, public exposure, cryptography, or production infrastructure changes.

### SEC-004 Vulnerability management
- **MUST:** scan code, dependencies, containers where applicable, and infrastructure as code.
- **MUST:** triage findings by severity, exploitability, exposure, and business impact.

### SEC-005 Auditability and incidents
- **MUST:** retain auditable security and deployment evidence without exposing secrets or unnecessary sensitive data.
- **MUST:** define incident ownership, escalation, containment, recovery, and learning.

## Exceptions
Security exceptions require documented risk acceptance by an authorized human security owner, mitigation, compensating controls, and expiry or review date.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| SEC-001 | SAST and unsafe-input patterns | Security CI |
| SEC-003 | Secure-code and logging rules | SAST/policy checks |
| SEC-004 | Vulnerability and IaC scanners | Security CI |
| SEC-005 | Audit and incident metadata checks | Governance review |
