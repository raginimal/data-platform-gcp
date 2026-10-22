# Security Baseline

Security controls are mandatory from repository creation. Project overlays may strengthen them, never weaken them without a documented and approved exception.

Detailed controls and stable IDs are defined in `policies/security/security-principles.md`, `policies/security/secrets.md`, and `policies/security/identity-access.md`. Exceptions use `docs/adr/exception-template.md` and require authorized human security approval.

## Requirements
- Store secrets in an approved secret manager; use OIDC/workload identity where supported.
- Use least-privilege GitHub, cloud, runtime, and deployment identities.
- Never commit secrets, tokens, private keys, credentials, production data, or `.env` files.
- Encrypt data in transit and at rest using platform-approved controls.
- Run secret scanning, SAST, dependency vulnerability scanning, and IaC scanning in CI.
- Scan containers when container assets exist.
- Pin or constrain dependencies and review transitive risk, licenses, and provenance.
- Emit auditable security and deployment logs without logging secrets or sensitive payloads.
- Triage vulnerabilities by severity, exploitability, exposure, and business impact; document accepted risk.
- Require security review for identity, trust boundary, sensitive data, internet exposure, cryptography, or production infrastructure changes.

## Blocking policy
Deterministic secret, critical vulnerability, prohibited permission, or failed infrastructure security checks block merge unless an approved exception is recorded. AI findings are advisory and cannot replace these controls.

## Incident response
Every project must identify an owner, escalation path, runbook location, containment approach, evidence-retention requirement, and post-incident learning process.
