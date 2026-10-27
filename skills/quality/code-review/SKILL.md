# Code Review Skill

- Skill ID: `QUAL-SK-001`
- Version: `1.0.0`
- Owner: engineering owner placeholder
- Applicable policies: `DEVOPS-PR-001`, `DEVOPS-PR-003`, `ARCH-001`, `SEC-003`

## Purpose
Review changed code for clarity, maintainability, error handling, observability, duplication, and appropriate scope.

## When to run
Run for source-code changes after deterministic formatting, lint, and test results are available.

## Inputs
Changed code, tests, project conventions, scanner results, and applicable policy IDs.

## Analysis procedure
Focus on changed behavior, evidence, failure paths, boundary validation, logging safety, and maintainability. Do not replace deterministic tests or lint.

## Expected output
Use the shared finding contract and classify suggestions separately from policy violations.

## Human review

Code owners decide whether maintainability recommendations require changes; deterministic lint, formatting, and test results remain authoritative.
