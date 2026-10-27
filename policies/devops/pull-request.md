# Pull Request Principles

Owner: repository maintainers and CODEOWNERS. Scope: changes proposed for protected branches.

Practical review roles, risk classification, and approval routing are defined in `docs/governance/review-model.md`, `docs/governance/risk-classification.md`, and `docs/governance/approval-matrix.md`.

### DEVOPS-PR-001 Reviewable change
- **MUST:** explain what changed, why, testing, risk, rollback, and affected architecture, security, data, AI, and infrastructure concerns.
- **SHOULD:** keep a PR focused and small enough for effective review.

### DEVOPS-PR-002 Required review
- **MUST:** use the PR template and obtain required CODEOWNER or designated human approvals.
- **MUST:** pass required build, quality, security, architecture, and governance checks.
- **MUST NOT:** merge based only on an AI recommendation.

### DEVOPS-PR-003 Evidence
- **MUST:** include tests or an explicit explanation when tests are not applicable.
- **MUST:** include an ADR or exception record when a change triggers one.
- **SHOULD:** link the issue and relevant deployment or migration plan.

### DEVOPS-PR-004 Impact disclosure
- **MUST:** disclose breaking changes, data classification, AI/model changes, infrastructure changes, and production rollback considerations.

## Exceptions
A reviewer may approve a documented exception only when risk, mitigation, owner, approver, and expiry are recorded. AI review is advisory.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| DEVOPS-PR-001 | Required template and issue link | PR governance |
| DEVOPS-PR-002 | Required checks and CODEOWNER status | GitHub branch policy |
| DEVOPS-PR-003 | Test and ADR/exception field validation | Governance CI |
| DEVOPS-PR-004 | Impact checklist completeness | PR policy check |
