# AI Engineering Project Foundation

## Purpose
This repository is a reusable, technology-neutral golden path for AI and Data/AI projects. It contains engineering, security, governance, CI/CD, infrastructure, and AI review standards. It is not an application.

## Before changing files
1. Read `README.md`, `CONTRIBUTING.md`, and the policy relevant to the change.
2. Inspect nearby implementation and tests before proposing a new pattern.
3. Check `PROJECT.yaml` for project-specific configuration.
4. For architectural changes, read `ARCHITECTURE.md` and add or update an ADR. Check `docs/architecture/baseline.yaml`; never edit it without explicit human approval.
5. Read the relevant source-of-truth documents under `policies/` and reference their stable principle IDs in the change.
6. Run `bash scripts/check.sh` before committing. The Makefile is optional and is not required on developer machines.

For workflow and governance decisions, read `docs/developer-workflow.md`, `docs/governance/risk-classification.md`, `docs/governance/approval-matrix.md`, and `docs/governance/exceptions.md`.

For AI-assisted engineering reviews, read `docs/agents-and-skills.md`, `docs/agent-output.md`, `policies/ai/agent-governance.md`, and the applicable agent and skill contracts. Agents are advisory and read-only by default.

## Engineering standards
- Keep changes small, reviewable, reversible, and traceable to an issue.
- Prefer simple, explicit designs over speculative abstractions.
- Keep the core cloud and language neutral; put provider-specific behavior in an overlay.
- Do not add dependencies without documenting purpose, ownership, license, risk, and update strategy.
- Configuration belongs outside code where environments differ; secrets never belong in Git.

## Coding and testing
- Follow the selected stack overlay and existing project conventions.
- Add or update tests for behavior changes.
- Unit tests are required for deterministic logic; integration and end-to-end tests are required when boundaries or workflows change.
- Do not reduce coverage thresholds to make a change pass.
- Run `bash scripts/check.sh`, and report unavailable optional tools rather than silently skipping required checks.

## Security and data
- Read `SECURITY.md` and `DATA_POLICY.md` before handling credentials, personal data, infrastructure, or external inputs.
- Never commit secrets, tokens, credentials, production data, or unapproved generated data.
- Use least privilege, approved secret management, encryption, and auditable identities.
- Treat all external input as untrusted and validate it at trust boundaries.

## AI usage
- Read `AI_POLICY.md` before changing models, prompts, RAG, evaluations, or guardrails.
- AI-generated code is untrusted until reviewed, tested, and scanned like human-authored code.
- AI review is advisory and never bypasses deterministic security, governance, or human approval controls.
- AI assistants must not approve exceptions, risk acceptance, production releases, or their own generated changes.
- AI assistants may identify applicable policies, suggest reviewers, summarize evidence, and flag risk; humans remain accountable for approval and exceptions.
- Do not send confidential, personal, regulated, or production data to unapproved AI tools.

## Pull requests and delivery
- Use `feature/*`, `bugfix/*`, or `hotfix/*` branches; never push directly to `main`.
- Complete every relevant section of the PR template.
- CI, CODEOWNER approval, and branch protection are mandatory merge controls.
- Build immutable artifacts once and promote the same artifact through environments.
- Production deployment requires explicit human approval and a documented rollback path.

## Prohibited behaviours
- Do not bypass checks, disable security scanning, or weaken policy to make CI pass.
- Do not auto-merge based only on an AI recommendation.
- Do not introduce hidden network calls, telemetry, remote code execution, or unreviewed model behavior.
- Do not modify unrelated files or vendor-specific core architecture without an ADR.
