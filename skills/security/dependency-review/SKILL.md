# Security Dependency Review Skill

- Skill ID: `SEC-SK-003`
- Version: `1.0.0`
- Owner: security owner placeholder
- Applicable policies: `ARCH-DEP-003`, `ARCH-DEP-004`, `SEC-004`

## Purpose
Interpret dependency vulnerability, provenance, support, and license evidence.

## When to run
Run when dependency manifests or lockfiles change, or when scanner results identify a dependency finding.

## Inputs
Dependency manifests, lockfiles, scanner results, severity policy, and exception records.

## Analysis procedure
Confirm the affected dependency, evidence, reachability where available, remediation version, exploitability, and expiry of any accepted risk.

## Expected output
Separate confirmed scanner findings from recommendations and reference the dependency/security policy ID.

## Human review
Security and architecture owners approve high-risk vulnerability or licensing exceptions.
