# Repository Principles

Owner: repository maintainers. Scope: every project created from this template.

Operational ownership and administrator setup are described in `docs/governance/ownership.md` and `docs/administrator-setup.md`.

## Normative rules

### RP-001 Repository identity and documentation
- **MUST:** contain `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, the applicable policy documents, and a project configuration file.
- **SHOULD:** keep onboarding, architecture, runbook, and ADR guidance current.
- **MAY:** add project-specific documentation under `docs/`.
- **Human decision:** repository maintainers approve documentation exceptions.

### RP-002 Ownership and review
- **MUST:** contain root and GitHub `CODEOWNERS` coverage for protected paths.
- **MUST:** protect `main` and require pull-request review and required checks.
- **SHOULD:** assign an accountable owner for every policy, service, data asset, and AI asset.
- **Human decision:** CODEOWNER and repository administrators approve ownership changes.

### RP-003 Source control and artifacts
- **MUST:** keep source, configuration contracts, policies, infrastructure, tests, and AI assets in version control.
- **MUST NOT:** commit secrets, credentials, production data, temporary files, generated build output, unmanaged binaries, or local environment files.
- **SHOULD:** use versioned releases and maintain `CHANGELOG.md` for user-visible changes.
- **MAY:** commit small reviewed fixtures and static assets where ownership and licensing are clear.

### RP-004 Configuration and environments
- **MUST:** separate environment configuration from application code and keep secrets outside Git.
- **MUST:** define supported environments and their owners in project configuration.
- **SHOULD:** make configuration changes auditable and reproducible.

### RP-005 Dependencies and decisions
- **MUST:** document the purpose, owner, license, risk, and update strategy for material dependencies.
- **MUST:** record material architecture and platform decisions in an ADR.
- **SHOULD:** remove duplicate or unused capabilities.

## Exceptions
An exception must record an exception ID, affected principle ID, reason, risk, mitigation, owner, human approver, and expiry or review date. AI review cannot approve an exception.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| RP-001 | Required-file check | Repository policy check |
| RP-002 | CODEOWNERS and branch-rule validation | GitHub repository policy |
| RP-003 | Secret, artifact, binary, and ignore-pattern scans | Security and governance CI |
| RP-004 | Configuration and secret-path checks | Governance CI |
| RP-005 | Dependency metadata and ADR-trigger checks | Architecture policy check |
