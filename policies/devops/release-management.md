# Release Management Principles

Owner: release owner. Scope: versioning, release notes, artifacts, and hotfixes.

### DEVOPS-REL-001 Version strategy
- **MUST:** identify every releasable artifact with a unique version or immutable digest.
- **SHOULD:** use semantic versioning when the project exposes a compatible public API or library.
- **MAY:** use date, build, or platform-native versions when semantic versioning is inappropriate, with the strategy documented.

### DEVOPS-REL-002 Release evidence
- **MUST:** record commit, artifact, checks, approvers, deployment environments, and release notes.
- **SHOULD:** update `CHANGELOG.md` for user-visible changes.

### DEVOPS-REL-003 Rollback and hotfixes
- **MUST:** define rollback, recovery, and hotfix ownership.
- **MUST:** validate a hotfix with the same applicable security and quality controls as normal changes.

### DEVOPS-REL-004 Release ownership
- **MUST:** name an accountable release owner and operational contact.

## Exceptions
A release exception requires a human approver, risk assessment, mitigation, and review date.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| DEVOPS-REL-001 | Version/digest uniqueness check | Release CI |
| DEVOPS-REL-002 | Release metadata and changelog check | Release governance |
| DEVOPS-REL-003 | Rollback-plan field check | Deployment gate |
