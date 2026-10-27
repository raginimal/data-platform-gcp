# Infrastructure as Code Model

## Layout

```text
infrastructure/
├── modules/                 reusable reviewed modules
├── terraform/               selected overlay roots
└── environments/
    ├── dev/                 isolated DEV composition
    ├── test/                isolated TEST/UAT composition
    └── prod/                protected PROD composition
```

## Rules

Modules document inputs, outputs, ownership, security, monitoring, and lifecycle. Environment roots compose modules and keep state isolated. Remote state must be encrypted, locked, access-controlled, retained, and external to Git.

Plan and apply are separate operations. Plans are reviewed; production apply requires explicit approval. State credentials and secrets are supplied by the platform, not source control. Drift detection is scheduled where the selected platform supports it.

The core contains no provider resources. A stack overlay supplies Terraform providers, backend configuration, variables, plans, applies, and IaC security scanners.

## Automation Candidates

| Candidate | Principle ID | Component | Mode | Human approval | Phase |
|---|---|---|---|---|---|
| Format and validate | ARCH-006 | Infrastructure CI | Deterministic | No | 4/5 |
| Plan review | ARCH-006 | IaC workflow | Deterministic | Platform owner | 5 |
| State and drift checks | DEVOPS-ENV-004 | IaC platform | Deterministic | Platform owner | 5 |
