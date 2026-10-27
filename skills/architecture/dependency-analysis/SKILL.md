# Dependency Analysis Skill

- Skill ID: `ARCH-SK-002`
- Version: `1.0.0`
- Owner: architecture owner placeholder
- Applicable policies: `ARCH-DEP-001` through `ARCH-DEP-005`

## Purpose
Review new, changed, duplicate, unsupported, vulnerable, or license-sensitive dependencies.

## When to run
Run when dependency manifests, lockfiles, package configuration, external platforms, or model providers change.

## Inputs
Dependency diff, manifests, lockfiles, ownership metadata, vulnerability results, license data, and ADRs.

## Analysis procedure
Check purpose, owner, provenance, version strategy, duplicate capabilities, support, license, vulnerability, and trust-boundary implications.

## Expected output
Reference the dependency evidence and applicable `ARCH-DEP-*` policy ID in the shared finding contract.

## False positives and human review
Do not infer vulnerability or license violations without evidence. Architecture, security, and legal owners decide material exceptions.

## Human review

Architecture and security owners approve material dependency, vulnerability, licensing, and boundary-risk decisions.
