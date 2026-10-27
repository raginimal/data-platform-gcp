# Break-Glass Procedure

Break-glass is for an active incident or imminent material harm where following the normal workflow would increase impact. It is not a convenience path for late planning.

## Procedure

1. Declare the incident or emergency change and record affected service, impact, and reason.
2. Name the incident lead, implementer, reviewer, and emergency approver.
3. Record which protection or requirement is temporarily bypassed and the shortest required duration.
4. Apply the smallest reversible change, with logging and peer review where possible.
5. Validate health, security, data integrity, and user impact immediately after deployment.
6. Roll back or remediate if validation fails.
7. Restore normal branch protections and access.
8. Complete a post-incident review, update the exception record, and convert recurring issues into policies, tests, or ADRs.

## Approval

At least one authorized human emergency approver must approve the action. Production approval remains human. AI may summarize evidence or suggest mitigations but cannot invoke, approve, or close break-glass.

## Evidence

Record incident ID, principle IDs, approvers, bypassed controls, timestamps, artifacts, commands, monitoring evidence, validation, rollback result, and follow-up owner. Any temporary exception requires an expiry or review date.

## Automation Candidates

| Candidate | Principle ID | Future component | Mode | Trigger | Human approval | Phase |
|---|---|---|---|---|---|---|
| Bypass evidence | DEVOPS-BR-004, DEVOPS-CD-005 | Incident/deployment record | Deterministic | Emergency change | Emergency approver | 5 |
| Post-change validation | DEVOPS-CD-005 | Deployment health gate | Deterministic | Break-glass deployment | Incident lead | 5 |
| Recurrence detection | Learning loop | Review assistant | AI-assisted | Incident review | Human owner | 6 |
