# Review Model

## Reviewer roles

- **Author:** owns correctness, evidence, disclosure, and responding to feedback.
- **CODEOWNER:** verifies maintainability, policy alignment, tests, and impact for owned paths.
- **Specialist reviewer:** reviews architecture, security, data, platform, or AI concerns when the approval matrix requires it.
- **Community reviewer:** provides useful feedback but cannot replace required ownership or specialist approval.
- **AI reviewer:** identifies risks and suggests questions; it cannot approve, merge, accept risk, or override a deterministic control.
- **Release approver:** confirms deployment, rollback, environment, and production conditions.

## Evidence standard

Evidence must be reproducible and specific: command and result, test report, scan result, ADR, data contract, evaluation report, deployment record, or approved exception. Statements without evidence are questions, not proof.

## Review checklist

Reviewers should confirm scope, architecture, dependencies, security, data, AI, tests, observability, deployment, rollback, documentation, risk, and required approvals. Request changes when evidence is missing, a requirement is violated, or risk is not owned.

## Decision and disagreement

Approve only when the change and evidence meet the Definition of Done. Use request-changes for blocking concerns and comment for non-blocking suggestions. When reviewers disagree, pause merge, document the competing risks, and escalate to the accountable owner or maintainer. A maintainer cannot override a required security, data, AI, or production approval without the authorized approver.

Reviewers should respond within the project-agreed service level, normally two business days. Escalate stalled reviews to the repository maintainer; emergency changes use the break-glass procedure.

## Automation Candidates

| Candidate | Principle ID | Future component | Mode | Trigger | Human approval | Phase |
|---|---|---|---|---|---|---|
| Review checklist | DEVOPS-PR-001 | PR guidance/check | Deterministic | PR opened | Reviewer | 4 |
| Specialist routing | DEVOPS-PR-002 | Review router | Deterministic/AI-assisted | PR diff | Specialist | 4/6 |
| Review evidence | DEVOPS-PR-003 | Evidence validator | Deterministic | PR update | Reviewer | 4 |
