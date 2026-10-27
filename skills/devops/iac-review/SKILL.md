# IaC Review Skill

- Skill ID: `DEVOPS-SK-003`
- Version: `1.0.0`
- Owner: platform owner placeholder
- Applicable policies: `ARCH-006`, `DEVOPS-ENV-001` through `DEVOPS-ENV-004`, `SEC-004`

## Purpose
Review reusable modules, isolated state, plan/apply separation, drift, secrets, least privilege, and environment composition.

## When to run
Run when Terraform or other infrastructure definitions, modules, state configuration, or environment composition changes.

## Inputs
IaC diff, plans, module documentation, state configuration, scanner results, and environment policies.

## Analysis procedure
Check provider-overlay separation, module boundaries, state protection, plan evidence, production approval, secrets, and drift controls.

## Expected output
Reference the applicable architecture, environment, and security policies. Do not invent provider-specific findings without evidence.

## Human review

Platform and infrastructure owners approve plans, state changes, production apply, and IaC exceptions.
