# Contribution Guide

## Before coding

Start from an issue or approved work item. Identify affected policy IDs, risk level, owner, reviewers, data or AI impact, and rollback needs before implementation.

## Commit standard

Use Conventional Commits where the selected stack permits it: `type(scope): imperative summary`. Recommended types are `feat`, `fix`, `docs`, `test`, `refactor`, `build`, `ci`, and `chore`.

Commits MUST be meaningful, focused, free of secrets and generated output, and traceable to the work item. Do not mix unrelated changes. Squash merge is the default; do not rewrite shared branches or force-push unless the repository maintainer has approved it.

## Local validation

Run the narrowest useful check while developing, then the complete baseline before opening a PR:

```text
bash scripts/check.sh
```

If a command fails, fix the issue or document why it is not applicable. Do not hide failures, lower thresholds, or treat an unavailable required check as passed. Stack overlays may add commands but must preserve the core checks.

## Pull request and merge

Complete the PR template, classify risk, link evidence, request required reviewers, and disclose AI assistance. Resolve requested changes and keep the branch current. Do not merge until required checks and human approvals are complete.

## After merge

The release owner follows deployment, monitoring, rollback, and post-deployment validation guidance. Recurring review or operational issues are recorded through the learning loop.

## Automation Candidates

| Candidate | Principle ID | Future component | Mode | Trigger | Human approval | Phase |
|---|---|---|---|---|---|---|
| Commit format | DEVOPS-PR-001 | Commit policy check | Deterministic | Commit/PR | No | 4 |
| Local-check evidence | DEVOPS-CI-005 | PR evidence check | Deterministic | PR opened | Reviewer | 4 |
| AI assistance disclosure | AI-005 | PR governance | Deterministic | AI-assisted change | Reviewer | 4 |
