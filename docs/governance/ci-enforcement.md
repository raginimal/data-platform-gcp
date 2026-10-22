# CI Enforcement Model

Phase 4 translates policy IDs into deterministic checks. The core remains technology-neutral and reports conditional stack checks as `NOT CONFIGURED` when no relevant project assets exist.

## Check classes

- **Required:** repository structure, policy integrity, high-confidence secret scanning, governance metadata, and architecture baseline validation. The Baseline Guard classifies changes (`ARCH-BL-003`) and fails only on a missing or malformed ADR when the baseline is approved (`ARCH-BL-002`); whether a change is acceptable stays a human decision.
- **Conditional:** language linting/tests, coverage, dependency scanning, SAST, Terraform, and container checks when relevant assets exist.
- **Advisory:** future AI-assisted review; it cannot approve or override a deterministic result.

## Failure messages

Every blocking check should report the policy ID, failure reason, why it matters, remediation, and whether a human exception is possible. Committed secrets cannot be excepted; other policy exceptions require the Phase 3 exception process.

## Local and CI parity

CI invokes the same Makefile and scripts exposed to developers. Stack overlays extend the commands through project configuration rather than replacing the core checks.

## Human boundary

CI can validate, scan, fail, report, and enforce deterministic rules. It cannot approve exceptions, accept risk, approve production, or replace required human reviewers.
