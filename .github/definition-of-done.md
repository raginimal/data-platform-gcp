# Definition of Done

A change is done when the applicable items below are complete. Mark items not applicable with a reason in the PR.

## Code

- [ ] Implementation is complete and follows the architecture and selected stack overlay.
- [ ] Interfaces, configuration, and dependencies are documented where changed.
- [ ] No secrets, generated artifacts, temporary files, or unrelated changes are included.

## Testing

- [ ] Unit tests are added or updated for deterministic behavior.
- [ ] Integration and end-to-end tests are added when boundaries or workflows change.
- [ ] `bash scripts/check.sh` or the documented equivalent was run; failures are resolved or explained.

## Security and data

- [ ] Secrets, identity, dependency, infrastructure, and trust-boundary impact was considered.
- [ ] Data classification, contracts, retention, PII, and test-data requirements were considered where applicable.

## AI

- [ ] Model, prompt, RAG, evaluation, guardrail, and dataset changes were reviewed where applicable.
- [ ] Required evaluation evidence, human oversight, and cost impact are documented.
- [ ] AI-generated code received the same tests, scans, and review as human-written code.

## Documentation and review

- [ ] Relevant README, architecture, ADR, runbook, changelog, or policy documentation is updated.
- [ ] Required CODEOWNER and specialist reviews are complete.
- [ ] Required automated checks pass, or an approved exception is linked.

## Delivery

- [ ] Deployment impact, monitoring, rollback, and post-deployment validation are understood where applicable.
- [ ] The change is traceable to a work item and has no unresolved blocking feedback.

## Automation Candidates

| Candidate | Principle ID | Future component | Mode | Trigger | Human approval | Phase |
|---|---|---|---|---|---|---|
| Checklist completeness | DEVOPS-PR-003 | PR governance check | Deterministic | PR opened | Reviewer | 4 |
| Test evidence | DEVOPS-CI-002 | Quality gate | Deterministic | PR validation | No | 4 |
| AI impact fields | AI-004, AI-005 | AI policy check | Deterministic/AI-assisted | AI asset or code change | AI owner | 4/6 |
