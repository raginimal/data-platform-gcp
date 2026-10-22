# ADR-0001: GCP Demo Data Platform

- Status: approved
- Date: 2026-10-23
- Owners: TBD
- Baseline impact: impact
- Baseline boundaries: BL-APP, BL-TECH, BL-DATA, BL-SEC, BL-DEPLOY, BL-ENV
- Baseline update: no
- Approver: architecture owner (human); TBD

## Context

A demo needs a minimal path to land files, load them into BigQuery, and query them for simple analytics. Production requirements and ownership are not yet known.

## Decision

Demo proposal only, not an approved production decision: use Cloud Storage as the landing area and BigQuery for staging, analytics tables, and SQL queries. Use a development-only GCP environment, separate least-privilege identities, and reviewed infrastructure as code. Refer to [ARCHITECTURE.md](../../ARCHITECTURE.md) for the proposed flow and TBD details.

## Alternatives considered

- Other storage and analytics platforms: outside the requested GCP demo scope.
- Automated ingestion and dashboarding: deferred; trigger, orchestration, and consumer are TBD.

## Consequences

The proposal provides a small batch analytics path. File format, schema, validation, transformation, load trigger, location, resource names, and cost limits remain TBD.

## Impact and risks

Data classification, retention, deletion, access review, billing controls, and recovery requirements must be confirmed before implementation beyond synthetic or approved demo data. The architecture baseline remains unchanged and in draft.

## Automated controls

Review infrastructure as code and CI identity permissions before deployment. Validate least-privilege IAM, secret handling, and data controls using the project checks.

## Review and expiry

Review with the architecture, data, and security owners before implementation. Owners and review date are TBD. This proposal does not authorize production use.
