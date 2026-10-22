# Identity and Access Principles

Owner: security and platform owners. Scope: human, service, CI/CD, data, and production identities.

### SEC-IAM-001 Least privilege
- **MUST:** grant only the permissions required for an identified purpose and time period.
- **SHOULD:** use role-based access and deny-by-default policies.

### SEC-IAM-002 Identity ownership
- **MUST:** assign an owner, purpose, environment, and review cadence to each non-public identity.
- **MUST:** remove or disable unused identities and access.

### SEC-IAM-003 Service and deployment identities
- **MUST:** separate human, runtime, and deployment identities.
- **SHOULD:** use short-lived credentials, OIDC, workload identity, and protected environments.
- **MUST NOT:** embed long-lived credentials in code, images, or workflows.

### SEC-IAM-004 Access review
- **MUST:** review privileged and production access periodically and after role changes.
- **MUST:** retain approval and audit evidence.

## Exceptions
Emergency access requires a named human approver, bounded duration, logging, and post-use review.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| SEC-IAM-001 | Permission and role policy scan | Security CI |
| SEC-IAM-002 | Owner and expiry metadata check | Access governance |
| SEC-IAM-003 | Workflow permission and credential scan | CI security |
| SEC-IAM-004 | Periodic access review report | Security operations |
