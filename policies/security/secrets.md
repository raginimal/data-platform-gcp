# Secrets Principles

Owner: security owner. Scope: credentials, tokens, keys, certificates, connection strings, and sensitive configuration.

### SEC-SEC-001 No secrets in Git
- **MUST NOT:** commit secrets, credentials, private keys, tokens, passwords, or production connection strings to source control, issues, logs, images, or artifacts.
- **MUST:** use approved secret management and external references.

### SEC-SEC-002 Secret access
- **MUST:** grant secret access by least privilege, purpose, environment, and service identity.
- **SHOULD:** use short-lived credentials and workload identity or OIDC where supported.

### SEC-SEC-003 Rotation and response
- **MUST:** define ownership, rotation, revocation, and compromise response for every material secret.
- **MUST:** revoke and rotate exposed credentials immediately according to incident procedures.

### SEC-SEC-004 Safe handling
- **MUST:** prevent secrets from appearing in logs, prompts, test fixtures, container layers, crash dumps, or error messages.
- **SHOULD:** use redaction and automated scanning at commit and CI boundaries.

## Exceptions
There is no exception for knowingly committing live credentials. Temporary test credentials require isolation, an owner, limited scope, and human approval.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| SEC-SEC-001 | Secret scanning and forbidden-file checks | Security CI |
| SEC-SEC-002 | Identity and permission policy checks | Access governance |
| SEC-SEC-003 | Rotation metadata and expiry checks | Secret governance |
| SEC-SEC-004 | Log and artifact secret pattern scanning | Security CI |
