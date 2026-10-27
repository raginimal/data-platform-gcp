# Environment Strategy

## Boundaries

Each environment has separate configuration, deployment permissions, runtime identity, secret references, data access, and audit trail.

- DEV may use synthetic or approved non-production data.
- TEST/UAT uses controlled representative data and release validation.
- PROD uses restricted data, identities, secrets, and access.

Configuration is reviewed and external to the immutable artifact. Secrets are never stored in Git or artifact archives. Intentional parity differences must be documented.

## GitHub controls

Configure `dev`, `test`, and `prod` environments. PROD requires approved reviewers, restricted deployment branches/tags, protected secrets, and retained deployment evidence. OIDC or workload identity is preferred over long-lived credentials.

## Automation Candidates

| Candidate | Principle ID | Component | Mode | Human approval | Phase |
|---|---|---|---|---|---|
| Config separation | DEVOPS-ENV-002 | Repository/IaC check | Deterministic | No | 5 |
| Access separation | DEVOPS-ENV-001 | Platform policy | Deterministic | Platform owner | 5 |
| PROD reviewers | DEVOPS-ENV-003 | GitHub environment | Deterministic | Production approver | 5 |
