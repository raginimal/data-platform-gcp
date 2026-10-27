# IAM Review Skill

- Skill ID: `SEC-SK-002`
- Version: `1.0.0`
- Owner: security/platform owner placeholder
- Applicable policies: `SEC-IAM-001` through `SEC-IAM-004`, `DEVOPS-ENV-003`

## Purpose
Review identity ownership, least privilege, trust boundaries, deployment permissions, environment access, and workflow token scopes.

## When to run
Run for IAM, workflow permissions, environment, cloud identity, secret access, network trust, or deployment changes.

## Inputs
Changed configuration, policy documents, identity definitions, environment rules, and review evidence.

## Analysis procedure
Check purpose, owner, role scope, separation of human/runtime/deployment identities, expiry, auditability, and production restrictions.

## Expected output
Use the shared finding contract and escalate high-risk access changes.

## Human review
Security and platform owners approve privileged access and emergency access.
