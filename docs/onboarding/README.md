# Onboarding

- [New project setup](#new-project)
- [Existing project adoption](existing-project.md)

## New Project

Use this guide to create a new project from the AI Delivery Foundation. The foundation supplies governance,
architecture, policies, CI, and human-approval controls; the project supplies its language, runtime, cloud, data,
AI, and deployment overlays.

## 1. Create the repository

Create the project from this repository as a template, or copy its contents into a new repository. Do not retain the
foundation repository's Git history:

```powershell
git clone <foundation-repository-url> my-project
Set-Location my-project
Remove-Item -Recurse -Force .git
git init
```

The `/foundation init .` skill command can prepare the setup plan. It does not approve architecture, ownership, or
repository protection decisions.

## 2. Configure the project

Run the interactive setup script when Bash is available:

```bash
bash scripts/setup.sh
```

On Windows without Bash, edit [PROJECT.yaml](../../PROJECT.yaml) and replace every `CHANGE_ME` value. Set the
project name, team, owner, language, cloud, project type, repository organization, environments, and AI capabilities.

## 3. Configure ownership and policies

Replace the placeholders in [.github/CODEOWNERS](../../.github/CODEOWNERS), `AGENTS.md`, `ARCHITECTURE.md`, and
policy owner fields. Read [CONTRIBUTING.md](../../CONTRIBUTING.md), [SECURITY.md](../../SECURITY.md),
[AI_POLICY.md](../../AI_POLICY.md), and [DATA_POLICY.md](../../DATA_POLICY.md).

## 4. Select the project overlay

Add the project-specific build, lint, test, dependency, SAST, IaC, container, model, and deployment commands. Keep
these in the overlay; do not weaken the core policy or validation scripts.

## 5. Define and approve architecture

Complete [ARCHITECTURE.md](../../ARCHITECTURE.md), [baseline.yaml](../architecture/baseline.yaml), and any required
ADRs. Define modules, ownership, interfaces, data boundaries, environments, AI capabilities, and deployment shape.
The architecture owner must approve the baseline before it is marked `approved`.

## 6. Add project implementation

Use the standard locations:

```text
src/              application source
tests/            unit, integration, and end-to-end tests
ai/               models, prompts, evaluations, and guardrails
infrastructure/   infrastructure as code
config/           non-secret configuration
```

Keep secrets, credentials, production data, and environment-specific secret values outside Git.

## 7. Enable enforcement

The foundation includes the Plumbline gate and guard:

```text
.plumbline/plumbline.py
.plumbline/guard.py
plumbline.toml
```

Register the guard with the selected agent's PreToolUse hook. Configure CI to require the policy, quality, security,
and build checks. Configure GitHub branch protection separately; repository files cannot apply those settings alone.

## 8. Validate before the first feature

On Windows:

```powershell
python -m unittest discover -s tests -v
python skills/foundation/foundation.py assess .
python skills/foundation/foundation.py check .
python .plumbline\plumbline.py --all --format markdown
powershell -File scripts\validate.ps1
git diff --check
```

With Bash available, run the complete local gate:

```bash
bash scripts/check.sh
```

## 9. Open the foundation PR

Create a bootstrap branch, complete the [pull request template](../../.github/pull_request_template.md), and record
the testing, security, AI, architecture, risk, and ownership evidence. A human reviews and merges this PR before
feature development begins.

## 10. Configure repository protection

An administrator must protect `main`, require pull requests and current branches, require CI and CODEOWNER approval,
prohibit force pushes, and configure human approval for production. Use
[administrator-setup.md](../administrator-setup.md) as the checklist.
