# Agents and Skills Framework

```text
POLICY -> SKILL -> AGENT -> WORKFLOW -> HUMAN
```

- **Policy:** defines what must be true.
- **Skill:** defines how one focused analysis is performed.
- **Agent:** selects applicable skills and consolidates findings.
- **Workflow:** supplies changed files, policy context, and review context.
- **Human:** makes accountable decisions for risk, exceptions, production, and required approvals.

## Routing

The initial change-aware routing contract is in `config/ai/agent-routing.yaml`. It is a configurable default, not a complete project classifier. Agents should select only relevant skills after reviewing changed paths, declared impact, policy IDs, and available evidence.

## Deterministic boundary

Formatting, linting, tests, secret scanning, SAST, IaC validation, dependency checks, policy validation, artifact verification, and deployment protections remain deterministic. Agents provide reasoning, context, trade-off analysis, and recommendations around those results.

The vendored Plumbline gate adds deterministic checks for AI-generated stubs, debug leftovers, undeclared imports,
swallowed exceptions, missing tests, oversized changes, and changes spanning too many modules. Run it locally with
`bash scripts/plumbline-check.sh --all`; the quality workflow runs the same gate against pull-request changes.
The vendored implementation is excluded from its own content scan because it contains detector patterns by design.
The foundation's YAML architecture baseline and policy validators remain authoritative. Plumbline's source-level
architecture rules are disabled until the foundation defines a compatible machine-checkable module map in
`ARCHITECTURE.md`.

The vendored `scripts/plumbline-guard.sh` is an agent PreToolUse guard, not a GitHub branch-protection replacement.
Register it with the host agent's shell-tool hook to block merge, approval, force-push, hook-bypass, and protected
branch commands. Repository administrators must still configure protected branches, CODEOWNERS, and required checks.

## Human boundary

Agents cannot approve findings, exceptions, risk acceptance, production, IAM, merges, or deployments. Human reviewers remain accountable for defined decisions in the approval matrix.

## Architecture baseline impact

The Baseline Guard (`bash scripts/validate-baseline.sh`) reports which baseline boundaries a change touches and which agents they name. Architecture changes go to the Architecture Agent (`ARCH-SK-001` baseline impact review); IAM, infrastructure, and deployment boundaries add the Security & DevOps Agent; AI integration and model boundaries add the AI Engineering Agent plus the Architecture Agent. Agents recommend only: they cannot approve an architecture change, modify the baseline, waive an ADR, or bypass CI.

## Versioning

Every agent and skill has an ID, version, owner placeholder, applicable policies, and reviewable repository history. Changes to a skill or agent are governance changes because they can affect engineering review outcomes.
