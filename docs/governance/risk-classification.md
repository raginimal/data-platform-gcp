# Risk Classification

The author proposes a risk level; the CODEOWNER or accountable specialist confirms it. Use the highest applicable level.

## LOW

Documentation, tests, formatting, comments, or non-functional changes with no production, security, data, API, infrastructure, or AI behavior impact. Requires normal CODEOWNER review and applicable local checks.

## MEDIUM

Application logic, dependencies, configuration, non-breaking APIs, internal data behavior, or operational changes. Requires tests, impact disclosure, CODEOWNER review, and relevant specialist review when indicated.

## HIGH

Production infrastructure, IAM, security controls, data contracts or migrations, public APIs, model/prompt/guardrail changes, major cost or availability impact, or breaking changes. Requires affected specialist approval, documented rollback or mitigation, targeted validation, and explicit human risk ownership.

## CRITICAL

Changes that could cause material security or privacy harm, irreversible data loss, unsafe consequential AI behavior, broad production outage, or bypass of mandatory controls. Requires accountable risk owner, security or risk approval, architecture/platform approval where applicable, tested recovery, and explicit production approval. Do not merge until all required approvals are recorded.

## Reclassification

Raise the level when scope changes, new evidence appears, a reviewer identifies unanticipated impact, or an exception is requested. Risk acceptance is not an automatic waiver; use the exception process.

## Automation Candidates

| Candidate | Principle ID | Future component | Mode | Trigger | Human approval | Phase |
|---|---|---|---|---|---|---|
| Risk label suggestion | DEVOPS-PR-004 | PR risk classifier | AI-assisted | PR opened | Reviewer confirms | 6 |
| High-risk path detection | SEC-003, AI-002 | Policy rules | Deterministic | PR diff | Specialist | 4 |
| Approval escalation | DEVOPS-PR-002 | Review router | Deterministic | HIGH/CRITICAL label | Risk owner | 4 |
