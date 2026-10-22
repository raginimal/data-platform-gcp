# Continuous Integration Principles

Owner: platform owner. Scope: changes entering protected branches.

### DEVOPS-CI-001 Build gate
- **MUST:** resolve dependencies reproducibly and validate compilation, packaging, or equivalent project build behavior.
- **SHOULD:** produce a traceable artifact identified by commit and version.

### DEVOPS-CI-002 Quality gate
- **MUST:** run applicable formatting, linting, unit tests, integration tests, and static analysis.
- **MUST:** enforce the project coverage threshold without lowering it to pass a change.

### DEVOPS-CI-003 Security gate
- **MUST:** run secret scanning, SAST, dependency scanning, and applicable container and IaC scans.
- **MUST:** block merge for deterministic critical findings unless an approved, time-bound exception exists.

### DEVOPS-CI-004 Architecture and governance gate
- **MUST:** validate required files, policy presence, ownership, architecture rules, data contracts, dependency rules, and AI policy compliance.

### DEVOPS-CI-005 Reproducibility and evidence
- **MUST:** retain enough logs and metadata to identify commit, dependencies, checks, artifact, and result.
- **SHOULD:** fail fast on mandatory gates and make optional overlay checks explicit.

## Exceptions
A missing tool or stack-specific check is `NOT CONFIGURED`, not silently treated as passed. A human owner must approve risk and deadline for an exception.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| DEVOPS-CI-001 | Build and artifact check | Build CI |
| DEVOPS-CI-002 | Test, coverage, lint, and format checks | Quality CI |
| DEVOPS-CI-003 | Security scanners | Security CI |
| DEVOPS-CI-004 | Repository and policy validator | Governance CI |
| DEVOPS-CI-005 | Evidence and status checks | CI governance |
