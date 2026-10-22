# Branching Guide

This guide operationalizes `DEVOPS-BR-001` through `DEVOPS-BR-004`.

## Model

- `main` is the protected, releasable branch.
- `feature/<issue>-<short-name>` is for new capability.
- `bugfix/<issue>-<short-name>` is for corrective changes.
- `hotfix/<incident>-<short-name>` is for urgent production recovery.
- Release branches are not part of the default model; add one only with an ADR and release-owner approval.

## Rules

- Direct commits, force pushes, and bypass merges to `main` are prohibited.
- Branches should be short-lived and focused on one work item.
- Rebase or update a branch before merge when required checks depend on current `main`.
- Squash merge is the default for focused changes.
- Delete merged branches. Stale branches should be reviewed and removed by their owner.
- A hotfix must reference an incident or change record and follow the break-glass procedure where protections are temporarily bypassed.

## Responsibility

The developer owns branch creation, keeping it current, and local validation. Repository administrators configure protection. CODEOWNERS and required reviewers approve the change; no AI review can replace that approval.

## Automation Candidates

| Candidate | Principle ID | Future component | Mode | Trigger | Human approval | Phase |
|---|---|---|---|---|---|---|
| Branch naming | DEVOPS-BR-002 | Branch policy check | Deterministic | Branch creation/PR | No | 4 |
| Protected `main` | DEVOPS-BR-001 | GitHub repository policy | Deterministic | Repository setup | Admin configuration | 4 |
| Stale branch report | DEVOPS-BR-004 | Repository maintenance | Deterministic | Scheduled review | Branch owner | 4 |
