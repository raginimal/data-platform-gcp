# Approval Matrix

The author may propose risk and reviewers, but the accountable owner confirms the final classification. Required approvals are cumulative.

| Change | Minimum review | Human approval |
|---|---|---|
| Documentation, tests, non-functional change | CODEOWNER | CODEOWNER |
| Application logic or dependency | CODEOWNER, relevant specialist | CODEOWNER |
| API, service boundary, architecture, or major dependency | CODEOWNER, architecture owner | Architecture owner |
| Baseline impact (`BASELINE_IMPACT`) | CODEOWNER, owners of the matched boundaries | Owners per the matching rows in this matrix |
| Architecture change (`ARCHITECTURE_CHANGE`) or baseline edit | CODEOWNER, ADR, architecture owner, affected specialists | Architecture owner |
| Infrastructure, Terraform, environment, or deployment | CODEOWNER, platform owner | Platform owner |
| IAM, trust boundary, cryptography, secrets, or security control | CODEOWNER, security owner | Security owner |
| Data contract, PII, retention, classification, or migration | CODEOWNER, data owner | Data owner and security/privacy when applicable |
| Model, prompt, RAG, evaluation, guardrail, or AI dataset | CODEOWNER, AI owner | AI owner and security/data owner when applicable |
| Production configuration or release | Relevant owner and release owner | Explicit production approver |
| Policy or exception change | Policy owner | Authorized policy owner |
| HIGH or CRITICAL change | All affected specialists | Accountable risk owner plus required approvers |

## Human boundary

Automated checks and AI review can provide evidence and recommendations. They cannot approve exceptions, accept risk, approve production, or replace required human review.

## Unavailability and escalation

Use the documented backup owner. If no qualified backup exists, pause the change or escalate to the repository maintainer and accountable owner. Emergency changes follow `docs/break-glass-procedure.md`.

## Automation Candidates

| Candidate | Principle ID | Future component | Mode | Trigger | Human approval | Phase |
|---|---|---|---|---|---|---|
| Reviewer routing | DEVOPS-PR-002, SEC-003, AI-002 | Approval policy | Deterministic/AI-assisted | PR diff | Required matrix approvers | 4/6 |
| Approval completeness | RP-002 | Governance check | Deterministic | Merge attempt | No bypass | 4 |
| Production approval | DEVOPS-CD-003 | Environment protection | Deterministic | Deployment | Production approver | 5 |
