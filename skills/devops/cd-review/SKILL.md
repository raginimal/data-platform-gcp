# CD Review Skill

- Skill ID: `DEVOPS-SK-002`
- Version: `1.0.0`
- Owner: release/platform owner placeholder
- Applicable policies: `DEVOPS-CD-001` through `DEVOPS-CD-005`, `DEVOPS-ENV-003`

## Purpose
Review build-once promotion, artifact verification, environment ordering, approval gates, traceability, and rollback hooks.

## When to run
Run for CD workflows, release configuration, environment protection, promotion logic, or rollback changes.

## Inputs
Workflow diff, artifact manifest, environment configuration, approval matrix, and rollback evidence.

## Analysis procedure
Verify the same artifact is promoted, digests are checked, PROD requires human approval, identities are separated, and rollback is possible.

## Expected output
Reference `DEVOPS-CD-*` and distinguish executable behavior from unconfigured platform adapters.

## Human review
Release and production owners approve deployment and rollback decisions.
