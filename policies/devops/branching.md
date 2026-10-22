# Branching Principles

Owner: repository maintainers. Scope: source-control workflow.

### DEVOPS-BR-001 Protected branches
- **MUST:** protect `main`; direct pushes, force pushes, and bypass merges MUST NOT be permitted for normal development.
- **MUST:** require a pull request, required checks, and CODEOWNER or designated human approval.
- **SHOULD:** use a merge queue where repository scale warrants it.

### DEVOPS-BR-002 Branch names
- **MUST:** use `feature/*`, `bugfix/*`, or `hotfix/*` branches for changes.
- **SHOULD:** include an issue identifier and concise purpose.

### DEVOPS-BR-003 Merge strategy
- **SHOULD:** use squash merges for focused, reviewable history.
- **MUST:** keep the branch up to date with protected `main` before merge where required checks depend on current state.

### DEVOPS-BR-004 Branch lifecycle
- **SHOULD:** keep branches short-lived and delete merged branches.
- **MAY:** retain a hotfix branch only while incident recovery requires it.

## Exceptions
A break-glass hotfix requires a named human approver, incident or change record, post-change review, and expiry of any temporary bypass.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| DEVOPS-BR-001 | Branch protection and push-rule validation | GitHub repository policy |
| DEVOPS-BR-002 | Branch-name check | PR governance |
| DEVOPS-BR-004 | Stale-branch reporting | Repository maintenance |
