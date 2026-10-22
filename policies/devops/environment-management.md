# Environment Management Principles

Owner: platform owner. Scope: DEV, TEST/UAT, and PROD environments.

### DEVOPS-ENV-001 Separation
- **MUST:** logically separate DEV, TEST/UAT, and PROD identities, configuration, data access, and deployment controls.
- **MUST NOT:** use production credentials or unrestricted production data in development or testing.

### DEVOPS-ENV-002 Configuration
- **MUST:** keep environment configuration separate from application code and secrets outside Git.
- **SHOULD:** use reproducible, reviewed configuration and infrastructure definitions.

### DEVOPS-ENV-003 Production access
- **MUST:** restrict production access by role, purpose, approval, and audit trail.
- **SHOULD:** use short-lived access and break-glass controls.

### DEVOPS-ENV-004 Environment parity
- **SHOULD:** keep runtime and infrastructure behavior sufficiently consistent to make validation meaningful.
- **MUST:** document intentional differences.

## Exceptions
Exceptions require an environment owner, risk and data assessment, human approval, mitigation, and expiry.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| DEVOPS-ENV-001 | Credential, account, and data-boundary checks | Environment policy |
| DEVOPS-ENV-002 | Secret-path and config separation check | Governance CI |
| DEVOPS-ENV-003 | Role and approval audit | Access governance |
| DEVOPS-ENV-004 | Configuration drift and parity report | Platform CI |
