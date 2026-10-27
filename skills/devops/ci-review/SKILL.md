# CI Review Skill

- Skill ID: `DEVOPS-SK-001`
- Version: `1.0.0`
- Owner: platform owner placeholder
- Applicable policies: `DEVOPS-CI-001` through `DEVOPS-CI-005`

## Purpose
Review CI workflow triggers, permissions, gates, reproducibility, evidence, and separation of required versus conditional checks.

## When to run
Run for `.github/workflows/`, Makefile, scripts, build configuration, or CI policy changes.

## Inputs
Workflow diff, scripts, policy IDs, runner permissions, artifact evidence, and stack overlay configuration.

## Analysis procedure
Check least privilege, duplicate checks, deterministic gates, conditional asset handling, failure messages, and evidence retention.

## Expected output
Reference `DEVOPS-CI-*` and identify the required human decision for exceptions.

## Human review

Platform owners approve required gate changes, workflow permissions, and exceptions. AI recommendations cannot replace deterministic CI checks.
