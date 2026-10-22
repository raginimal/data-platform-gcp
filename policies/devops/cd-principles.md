# Continuous Delivery Principles

Owner: release and platform owners. Scope: promotion from source to production.

### DEVOPS-CD-001 Build once
- **MUST:** build the artifact once and promote the same artifact through DEV, TEST/UAT, and PROD.
- **MUST NOT:** rebuild production from a mutable branch or different source state.

### DEVOPS-CD-002 Immutable versioned artifacts
- **MUST:** deploy an immutable, versioned artifact traceable to a commit.
- **SHOULD:** sign or attest artifacts where platform capability exists.

### DEVOPS-CD-003 Environment progression
- **MUST:** validate in DEV before TEST/UAT and validate TEST/UAT before PROD.
- **MUST:** require appropriate human approval before production.

### DEVOPS-CD-004 Traceability
- **MUST:** retain repository, commit, artifact, pipeline, environment, result, identity, and approver evidence for each deployment.

### DEVOPS-CD-005 Rollback
- **MUST:** document and test rollback or recovery for every production service.

## Exceptions
A production emergency may use a documented hotfix path with incident ownership, human approval, post-release validation, and retrospective review.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| DEVOPS-CD-001 | Artifact digest comparison across environments | CD gate |
| DEVOPS-CD-002 | Artifact version and provenance check | Release pipeline |
| DEVOPS-CD-003 | Environment dependency and approval check | Deployment policy |
| DEVOPS-CD-004 | Deployment evidence record | Release governance |
| DEVOPS-CD-005 | Rollback metadata and rehearsal check | Operations gate |
