# /foundation

Use this skill to apply the AI Delivery Foundation to new and existing repositories. The foundation owns policy,
risk, architecture-baseline, and human-approval decisions. Plumbline owns deterministic source checks and the
agent safety guard.

## Commands

| Command | Mode | Purpose |
|---|---|---|
| `/foundation assess [path]` | Read-only | Inventory a repository and report missing foundation controls. |
| `/foundation init [path]` | Human-reviewed change | Configure a new project from the foundation template. |
| `/foundation adopt [path]` | Human-reviewed change | Bring an existing repository under the foundation without overwriting its conventions. |
| `/foundation scaffold <path>` | Dry-run by default | Plan or add the foundation files to an existing repository. |
| `/foundation check [path]` | Deterministic | Run the foundation validators and Plumbline gate. |
| `/foundation policy [paths...]` | Read-only | Identify policies relevant to changed paths. |
| `/foundation baseline [path]` | Read-only or validation | Inspect or validate the architecture baseline. |
| `/foundation protect` | Read-only | Show the GitHub protections administrators must configure. |
| `/foundation report [path]` | Read-only | Summarize adoption status and enforcement evidence. |

## Existing repository: adopt

1. Run `/foundation assess <path>` and review the inventory.
2. Create a branch in the target repository.
3. Preserve existing CI, hooks, policies, architecture, and ownership files unless the owner approves a merge.
4. Add missing foundation files and the Plumbline gate/guard on the branch.
5. Populate `PROJECT.yaml`, owners, architecture baseline, and ADRs from project facts only.
6. Run `/foundation check <path>` and record existing debt rather than weakening controls.
7. Open a pull request and stop for human review.

For file transfer, use the scaffold helper. Quote Windows paths containing spaces:

```text
python skills/foundation/foundation.py scaffold "C:/path/to/existing project" --mode minimal
python skills/foundation/foundation.py scaffold "C:/path/to/existing project" --mode minimal --apply
```

`minimal` adds the governance and enforcement core, including `src/` and `tests/` placeholders required by
repository validation. Use `--mode full` to add the policies, docs, agents, skills, scripts, and workflows as
well. Scaffolding never overwrites an existing file; review the dry run first.

## New repository: init

1. Create the repository from the foundation template.
2. Populate `PROJECT.yaml`, owners, stack overlay, environments, and AI capabilities.
3. Define the architecture baseline and required ADR decisions.
4. Configure Plumbline, CI, CODEOWNERS, branch protection, and human production approval.
5. Run `/foundation check` before the first feature branch.

Agents may prepare these changes, but they cannot approve exceptions, approve or merge pull requests, configure
protected-branch bypasses, or decide architecture ownership.

## Deterministic entry point

Run the helper directly when an agent command is unavailable:

```text
python skills/foundation/foundation.py assess .
python skills/foundation/foundation.py check .
python skills/foundation/foundation.py policy src/foo.py ai/prompts/example.md
```
