# Test Review Skill

- Skill ID: `QUAL-SK-002`
- Version: `1.0.0`
- Owner: engineering owner placeholder
- Applicable policies: `DEVOPS-CI-002`, `DEVOPS-PR-003`, `AI-EVAL-002`

## Purpose
Review whether tests cover changed behavior, boundaries, failures, regressions, and AI evaluation requirements where applicable.

## When to run
Run for source, test, API, data, infrastructure, or AI behavior changes after tests execute.

## Inputs
Changed code, test diff, test results, coverage when configured, contracts, and risk classification.

## Analysis procedure
Identify untested behavior and weak assertions without inventing a coverage threshold. Report missing tests as recommendations unless a policy or configured gate requires them.

## Expected output
Reference the applicable quality or AI evaluation policy and state the evidence and confidence.

## Human review

Code owners and AI evaluation owners decide whether test gaps block a change or require an approved exception.
