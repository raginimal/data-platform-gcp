# Deployment Model

## Environment progression

```text
approved commit -> immutable artifact -> DEV -> validation -> TEST/UAT -> approval -> PROD
```

- **DEV:** isolated integration environment for early validation. Promotion may be automatic after artifact verification.
- **TEST/UAT:** representative validation environment with separate access and data boundaries. Promotion requires successful DEV validation.
- **PROD:** restricted environment. Promotion uses the same verified artifact and requires explicit human approval through the selected platform.

Environment configuration, secrets, identities, and data access are external to the artifact. Provider-specific deployment commands belong in a stack overlay. The core deployment hook reports `NOT CONFIGURED` until an adapter is selected.

## Automation Candidates

| Candidate | Principle ID | Component | Mode | Human approval | Phase |
|---|---|---|---|---|---|
| Environment ordering | DEVOPS-CD-003 | CD workflow | Deterministic | PROD approver | 5 |
| Environment isolation | DEVOPS-ENV-001 | Platform/IaC check | Deterministic | Platform owner | 5 |
| Production protection | DEVOPS-ENV-003 | GitHub environment | Deterministic | Production approver | 5 |
