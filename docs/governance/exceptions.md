# Exception Management

Use an exception only when a MUST requirement cannot be met, the reason is specific, and compensating controls reduce the risk. Exceptions are not a permanent alternative to implementation.

## Required record

Use `docs/adr/exception-template.md` and include exception ID, principle ID, reason, scope, risk, mitigation, owner, approver, created date, expiry or review date, evidence, and status.

## Approval routing

- Repository or branching exception: repository maintainer.
- Architecture or dependency exception: architecture owner.
- Security, secret, IAM, or vulnerability exception: security owner.
- Data, PII, retention, or contract exception: data owner and security/privacy owner when applicable.
- AI model, prompt, evaluation, guardrail, or dataset exception: AI owner plus affected security/data owner.
- Production or release exception: release owner and explicit production approver.
- HIGH or CRITICAL exception: accountable risk owner plus all affected specialist approvers.

## Process

1. Author opens an exception record before merge or deployment.
2. Owner documents why compliance is not currently feasible.
3. Reviewers assess risk, scope, mitigation, and residual exposure.
4. Authorized humans approve or reject the exception.
5. The PR links the record and states the expiry or review date.
6. The owner reviews open exceptions at least monthly and closes, renews, or replaces them before expiry.
7. Expired exceptions are treated as non-compliance until renewed by an authorized human.

If an approver disagrees or is unavailable, escalate to the accountable risk owner. AI recommendations may inform the decision but cannot approve it.

## Automation Candidates

| Candidate | Principle ID | Future component | Mode | Trigger | Human approval | Phase |
|---|---|---|---|---|---|---|
| Required exception fields | All policy exception clauses | Exception validator | Deterministic | PR/deployment | Approver | 4 |
| Expiry reporting | RP-005 | Governance report | Deterministic | Monthly | Owner | 4 |
| Risk summary | DEVOPS-PR-004 | Review assistant | AI-assisted | Exception opened | Human approver | 6 |
