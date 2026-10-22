# Administrator Setup

This checklist is manual repository administration. Committed files can describe the desired state but cannot fully configure GitHub settings.

## Repository protection

- [ ] Protect `main`; prohibit direct pushes and force pushes.
- [ ] Require pull requests, current branches, required status checks, and CODEOWNER approval.
- [ ] Require conversation resolution and prevent bypass except for documented emergency administration.
- [ ] Enable squash merge and merge queue where appropriate; disable unintended merge methods.
- [ ] Configure stale-branch cleanup and audit ownership quarterly.

## Environments and delivery

- [ ] Configure DEV, TEST/UAT, and PROD environments.
- [ ] Restrict production deployment to approved human reviewers.
- [ ] Require the PROD environment to approve deployment only from protected release tags or branches.
- [ ] Configure separate environment reviewers and deployment permissions for DEV, TEST/UAT, and PROD.
- [ ] Configure environment secrets externally and use OIDC/workload identity where supported.
- [ ] Retain deployment logs and artifact/commit traceability.
- [ ] Retain artifact manifests and digests according to release policy.

## Access and security

- [ ] Assign least-privilege repository roles and admin backups.
- [ ] Configure secret scanning, dependency alerts, and approved security integrations.
- [ ] Review Actions permissions and workflow token scopes.
- [ ] Configure audit-log access and retention according to organizational requirements.

## Ownership

- [ ] Replace CODEOWNERS placeholders with approved team or role handles.
- [ ] Confirm coverage for source, infrastructure, security, data, AI, policies, and documentation.
- [ ] Confirm backup owners and escalation routes.

## Governance

- [ ] Publish the selected stack overlay and project configuration.
- [ ] Identify architecture, security, data, AI, platform, release, and production approvers.
- [ ] Review open exceptions and ownership at least quarterly.

## Automation Candidates

| Candidate | Principle ID | Future component | Mode | Trigger | Human approval | Phase |
|---|---|---|---|---|---|---|
| Branch protection audit | DEVOPS-BR-001 | Repository governance check | Deterministic | Setup/quarterly | Repository admin | 4 |
| Environment approval audit | DEVOPS-CD-003 | Deployment governance | Deterministic | Setup/deployment | Production approver | 5 |
| Actions permission audit | SEC-IAM-003 | Security check | Deterministic | Workflow change | Security owner | 4 |
