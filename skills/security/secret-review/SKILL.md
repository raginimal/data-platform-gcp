# Secret Review Skill

- Skill ID: `SEC-SK-001`
- Version: `1.0.0`
- Owner: security owner placeholder
- Applicable policies: `SEC-SEC-001` through `SEC-SEC-004`

## Purpose
Identify likely credentials, keys, tokens, secret-bearing configuration, and unsafe logging or artifact exposure.

## When to run
Run for all changed files, especially configuration, workflows, scripts, images, prompts, and tests.

## Inputs
Git diff, repository files, scanner evidence, ignore rules, and secret-management guidance.

## Analysis procedure
Prefer deterministic scanner results, classify confidence, identify exposure and rotation needs, and provide remediation. Treat a confirmed credential as a blocking security finding.

## Expected output
Reference `SEC-SEC-001` and include evidence, location, severity, confidence, and rotation action.

## Human review
Live secret handling and incident response require security-owner action. Knowingly committed live secrets are not eligible for exception.
