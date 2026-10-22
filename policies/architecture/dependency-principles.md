# Dependency Principles

Owner: technical lead and security owner. Scope: runtime, build, infrastructure, data, and AI dependencies.

### ARCH-DEP-001 Justification
- **MUST:** record purpose, owner, license, source, version policy, and update strategy for every material dependency.
- **SHOULD:** prefer maintained, supported dependencies with an active security process.

### ARCH-DEP-002 Capability reuse
- **MUST:** assess existing approved capabilities before adding a duplicate library, service, platform, or model.
- **SHOULD:** remove unused and duplicate dependencies.

### ARCH-DEP-003 Version and provenance
- **MUST:** constrain or pin dependencies sufficiently for reproducible builds and verify provenance where supported.
- **SHOULD:** update dependencies through small, reviewable changes.

### ARCH-DEP-004 Vulnerability and licensing risk
- **MUST:** scan dependencies for known vulnerabilities and license restrictions before release.
- **MUST:** document and human-approve accepted high-risk exceptions with an expiry.

### ARCH-DEP-005 Boundary risk
- **MUST:** review dependencies that cross trust, data, network, or cloud boundaries before adoption.

## Exceptions
The dependency owner records the exception, risk, mitigation, approver, and review date. AI recommendations do not approve dependencies.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| ARCH-DEP-001 | Dependency manifest metadata check | Dependency policy check |
| ARCH-DEP-002 | Duplicate capability review prompt | Architecture review |
| ARCH-DEP-003 | Lockfile and provenance check | Build CI |
| ARCH-DEP-004 | Vulnerability and license scan | Security CI |
