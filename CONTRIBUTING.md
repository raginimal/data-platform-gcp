# Contributing

Read [docs/developer-workflow.md](docs/developer-workflow.md), [.github/BRANCHING.md](.github/BRANCHING.md), and [.github/definition-of-done.md](.github/definition-of-done.md) before starting. Use [docs/governance/approval-matrix.md](docs/governance/approval-matrix.md) and [docs/governance/risk-classification.md](docs/governance/risk-classification.md) to select reviewers.

## Golden path

```text
Issue -> feature branch -> development -> local validation -> commit -> push
-> Pull Request -> CI -> review -> merge -> build -> deploy
```

## Branches
Use `feature/<issue>-<name>`, `bugfix/<issue>-<name>`, or `hotfix/<issue>-<name>`. `main` is protected: no direct pushes, squash merge is preferred, and the branch must be up to date.

## Local commands

```bash
bash scripts/setup.sh          # configure a new project from PROJECT.yaml
bash scripts/lint.sh           # formatting and lint hooks
bash scripts/test.sh           # unit and available integration tests
bash scripts/security.sh       # deterministic security checks and optional scanners
bash scripts/validate.sh       # repository, policy, and structure checks
bash scripts/plumbline-check.sh --all # AI-quality gate for the whole foundation
bash scripts/check.sh          # baseline validation before commit
bash scripts/build-artifact.sh # produce a versioned local artifact
```

Run `bash scripts/check.sh` before committing. Add stack-overlay commands through the project configuration rather than replacing the core checks.

Use `bash scripts/check.sh` while developing. If a check fails, resolve it or record why it is not applicable; never hide a required failure. Commit conventions, PR evidence, and post-merge responsibilities are described in [docs/contribution-guide.md](docs/contribution-guide.md).

For each change, consult the relevant `policies/` document and disclose affected principle IDs in the pull request when applicable. Automated checks may block deterministic violations; architecture, security, data, AI, production, and exception decisions remain human decisions.

## Pull requests
Describe what changed and why. Complete testing, architecture, security, data, AI/model, infrastructure, breaking-change, and AI-assistance sections. Link the issue, identify migrations and rollback needs, and request the appropriate CODEOWNER review.

## Delivery
CI must pass before merge. The pipeline builds one immutable artifact, promotes it through DEV and TEST/UAT, and requires explicit human approval for production. Deployments must be traceable to a commit and have a documented rollback path.

Exceptions use [docs/governance/exceptions.md](docs/governance/exceptions.md) and [docs/adr/exception-template.md](docs/adr/exception-template.md). AI review may advise but cannot approve exceptions, risk acceptance, production deployment, or merge.
