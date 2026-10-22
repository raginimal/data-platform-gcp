# Ownership Model

Ownership is accountable responsibility, not a claim that one person performs every task. Use team or role placeholders until a project populates them.

## Boundaries

| Area | Accountable owner | Typical review |
|---|---|---|
| Source and application | Project engineering owner | CODEOWNER |
| Architecture and APIs | Architecture owner | Architecture reviewer |
| Infrastructure and environments | Platform/DevOps owner | Platform reviewer |
| Security and IAM | Security owner | Security reviewer |
| Data and contracts | Data owner | Data reviewer |
| AI models, prompts, evaluations, guardrails | AI owner | AI reviewer |
| Documentation and onboarding | Repository maintainer | CODEOWNER |

`CODEOWNERS` should use team or role handles such as `@platform-owner`, not invented individual users. Project setup replaces placeholders with approved groups.

## CODEOWNERS maintenance

- Add coverage when a new protected area, service, data asset, or AI asset is introduced.
- Remove or transfer ownership during team changes, offboarding, or service handoff.
- Require approval from the current owner and repository maintainer for ownership changes.
- Review coverage at least quarterly and after reorganizations or incidents.
- Keep a backup owner or escalation route for every critical area.
- Record contested ownership in an ADR or governance issue; do not silently merge with missing ownership.

## Responsibility

CODEOWNERS review the quality and impact of changes in their area. They do not replace security, data, architecture, or production approvers when the approval matrix requires those roles.

## Automation Candidates

| Candidate | Principle ID | Future component | Mode | Trigger | Human approval | Phase |
|---|---|---|---|---|---|---|
| Ownership coverage | RP-002 | CODEOWNERS audit | Deterministic | PR and quarterly review | Maintainer | 4 |
| Placeholder detection | RP-002 | Setup/governance check | Deterministic | Bootstrap/PR | Repository owner | 4 |
| Ownership freshness | RP-002 | Scheduled report | Deterministic | Quarterly | Maintainer | 4 |
