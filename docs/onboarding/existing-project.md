# Onboarding: Existing Project Adoption

Use this runbook to bring an existing repository under the AI Delivery Foundation without replacing its application,
architecture, CI, ownership, or deployment decisions. Adoption is an incremental pull request, not a repository clone.

## 1. Keep the repositories separate

Clone the foundation beside the existing project, never inside it:

```powershell
Set-Location "C:\Users\<user>\workspace"
git clone <foundation-repository-url> ai-delivery-foundation
```

If the foundation is already available locally, use that path as the source repository.

## 2. Assess the existing repository

Run the assessment with the complete target path quoted. Quoting is required when a Windows directory contains spaces:

```powershell
python "C:\Users\<user>\workspace\ai-delivery-foundation\skills\foundation\foundation.py" assess "C:\path\to\existing project"
```

Review the missing files, missing directories, and unresolved project configuration before copying anything.

## 3. Create an adoption branch

Run this inside the existing project:

```powershell
Set-Location "C:\path\to\existing project"
git switch -c chore/adopt-ai-delivery-foundation
```

Do not modify the existing project's default branch directly.

## 4. Preview the foundation files

Start with the minimum governance and enforcement set:

```powershell
python "C:\Users\<user>\workspace\ai-delivery-foundation\skills\foundation\foundation.py" scaffold "C:\path\to\existing project" --mode minimal
```

Use the full set only after reviewing the project's existing conventions:

```powershell
python "C:\Users\<user>\workspace\ai-delivery-foundation\skills\foundation\foundation.py" scaffold "C:\path\to\existing project" --mode full
```

The command is a dry run by default:

- `PLAN` means the file is missing and can be added.
- `SKIP` means the target already has that path.
- Existing files are never overwritten.

## 5. Review conflicts before applying

Compare these files manually before applying the scaffold:

```text
AGENTS.md
ARCHITECTURE.md
CONTRIBUTING.md
PROJECT.yaml
plumbline.toml
.github/CODEOWNERS
.github/pull_request_template.md
.github/workflows/
scripts/
```

Merge the foundation requirements into existing files. Preserve project-specific build commands, test commands,
deployment workflows, security scanners, architecture documents, CODEOWNERS, and fitness functions unless their owners
approve a replacement.

## 6. Apply the selected files

Apply only the minimum set first:

```powershell
python "C:\Users\<user>\workspace\ai-delivery-foundation\skills\foundation\foundation.py" scaffold "C:\path\to\existing project" --mode minimal --apply
```

Apply the full set only when the adoption PR is intended to include the complete foundation documentation and policy
library:

```powershell
python "C:\Users\<user>\workspace\ai-delivery-foundation\skills\foundation\foundation.py" scaffold "C:\path\to\existing project" --mode full --apply
```

Scaffolding copies missing files only. It does not merge content inside files that already exist.

## 7. Configure the target project

Replace `CHANGE_ME` values and identify real owners in:

- `PROJECT.yaml`
- `AGENTS.md`
- `ARCHITECTURE.md`
- `docs/architecture/baseline.yaml`
- `.github/CODEOWNERS`
- `plumbline.toml`

Add project-specific overlays for language, runtime, cloud, data platform, AI capabilities, build, tests, deployment,
dependency scanning, SAST, IaC, and container validation.

## 8. Register the agent guard

Register the target project's `scripts/plumbline-guard.sh` with the selected agent's PreToolUse or shell-tool hook.
This guard blocks agent attempts to merge or approve pull requests, force-push, bypass hooks, or commit directly to a
protected branch. It does not replace GitHub branch protection.

## 9. Validate the adoption

From the existing project:

```powershell
python skills\foundation\foundation.py assess .
python skills\foundation\foundation.py check .
python .plumbline\plumbline.py --all --format markdown
powershell -File scripts\validate.ps1
python -m unittest discover -s tests -v
git diff --check
```

With Bash available:

```bash
bash scripts/check.sh
```

Do not weaken a rule to make adoption green. Fix critical secrets and security findings immediately. Record legitimate
existing debt through an ADR or approved exception and assign a remediation owner.

## 10. Open the adoption pull request

Complete the project PR template and document:

- Files added and files merged manually
- Existing controls preserved
- Plumbline and foundation checks run
- Existing findings and remediation owners
- Architecture baseline status
- Applicable policy IDs
- Required CODEOWNER and specialist reviewers

The adoption PR must receive human review before merge.

## 11. Configure repository protection

After adoption, an administrator must configure protected `main`, required pull requests, required CI checks,
CODEOWNER approval, current-branch requirements, no force pushes, and human production approval. Use
[administrator-setup.md](../administrator-setup.md) for the checklist.

## Completion criteria

Adoption is complete when:

- Project owners approve the adoption PR.
- `PROJECT.yaml` and ownership placeholders are configured.
- The architecture baseline has an owner and status.
- Foundation and Plumbline checks run in CI.
- Existing project checks still run.
- Required branch protections and human approvals are enabled.
