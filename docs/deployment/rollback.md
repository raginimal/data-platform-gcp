# Rollback Strategy

Rollback selects the previous known-good immutable artifact and redeploys it through the selected stack overlay.

## Trigger

Rollback is considered when health validation, security validation, data integrity, availability, or critical business behavior fails. The incident lead or authorized production owner decides whether to rollback.

## Procedure

1. Declare the incident or change record and capture the current artifact and deployment evidence.
2. Select the previous verified artifact by manifest and digest; provide it as `ROLLBACK_ARTIFACT` with its expected `ROLLBACK_DIGEST`.
3. Confirm configuration and data compatibility; do not assume application rollback reverses migrations.
4. Obtain required human emergency approval.
5. Run the stack-overlay rollback hook.
6. Validate health, security, data integrity, and user impact.
7. Record result, approver, timestamps, artifact digest, and follow-up actions.

Rollback does not automatically reverse irreversible data changes. Data migrations require a forward-fix or separately approved recovery plan.

## Automation Candidates

| Candidate | Principle ID | Component | Mode | Human approval | Phase |
|---|---|---|---|---|---|
| Previous digest selection | DEVOPS-CD-005 | Release metadata | Deterministic | Incident lead | 5 |
| Health-gated rollback | DEVOPS-CD-005 | Deployment platform | Deterministic | Production owner | 5 |
| Recovery decision | DEVOPS-CD-005 | Incident process | Human | Required | 5 |
