# Architecture Review Skill

- Skill ID: `ARCH-SK-001`
- Version: `1.1.0`
- Owner: architecture owner placeholder
- Applicable policies: `ARCH-001` through `ARCH-007`, `ARCH-BL-001` through `ARCH-BL-004`

## Purpose
Assess boundaries, cohesion, coupling, resilience, observability, APIs, and architecture consistency. Includes Architecture Baseline Impact Review: judge whether a change flagged by the Architecture Baseline Guard conforms to, adapts, or deviates from the approved baseline.

## When to run
Run for service, module, API, infrastructure-boundary, observability, or architecture-document changes. Also run when `bash scripts/validate-baseline.sh` reports `BASELINE_IMPACT` or `ARCHITECTURE_CHANGE`.

## Inputs
Changed files, PR context, architecture docs, ADRs, service contracts, and relevant policy documents. For baseline review also: `docs/architecture/baseline.yaml` and the guard output (matched boundaries, classification, routed agents).

## Analysis procedure
1. Identify changed boundaries and affected owners.
2. Compare dependencies and interfaces with documented architecture.
3. Check compatibility, failure behavior, observability, and ADR triggers.
4. Report evidence and uncertainty; recommend a deterministic check where possible.

### Baseline impact review
1. Read the matched boundaries; treat the guard classification as a routing signal, not a verdict.
2. Compare the change with each boundary's approved `baseline` and `flexible` statements.
3. Decide whether the change conforms (inside what is flexible), adapts (touches the boundary without altering the decision), or deviates (alters the approved decision).
4. Recommend whether architecture review and an ADR are required, and name the affected specialist owners, including where Security & DevOps or AI Engineering input is needed.
5. State uncertainty. Do not edit the baseline, approve the change, or waive the ADR.

## Expected output
Use `docs/agent-output.md` with an `ARCH-*` policy ID (`ARCH-BL-*` for baseline findings). Set `human_action_required` to the architecture owner for any deviation.

## Severity and false positives
Use the shared severity/confidence model. Do not call a design preference a violation without a policy requirement or evidence.

| Baseline finding | Severity |
|---|---|
| Deviation from an approved boundary without an ADR | HIGH |
| Deviation with an ADR awaiting approval | MEDIUM |
| Boundary touched, decision unchanged | LOW |
| Change inside a flexible area | INFO |

## Human review
Architecture owners decide material boundary, API, data, cost, and operational trade-offs. They approve every ADR and every baseline change.

## Examples
- New datastore under `infrastructure/database/`: `ARCHITECTURE_CHANGE`; likely deviation from the approved data platform; recommend an ADR and data-owner review.
- `ai/models/` version bump inside the approved model family: `BASELINE_IMPACT`; adapts, does not deviate; route to the AI owner.
- Prompt wording change: no baseline impact; leave to `AI-SK-002`.
