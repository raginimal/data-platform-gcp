# Architecture Principles

This document defines the core contract. Project-specific decisions belong in `docs/architecture/` and `docs/adr/`.

## GCP Data Platform Demo (Proposal)

**Status:** Demo proposal only; not an approved production design. Unknowns are marked TBD.

### Overview

Land demo data in Cloud Storage, load it into BigQuery, and run simple SQL analytics in BigQuery. The cloud and data platform are specified by the demo request; production suitability, data classification, and operational requirements remain TBD.

### Components and data flow

1. A Cloud Storage landing bucket receives demo files. Bucket name, location, file format, and retention are TBD.
2. A BigQuery load job loads files into a staging dataset, then into analytics tables as needed. Load trigger, schema validation, dataset names, and transformation approach are TBD.
3. An analyst queries BigQuery tables with SQL for simple analytics. Any dashboard or other consumer is TBD.

### IAM and secrets

- Use separate human, data-loading, and deployment identities; grant least-privilege access to the bucket and BigQuery datasets. Exact principals and roles are TBD.
- For local development, use approved user authentication; for CI deployment, prefer short-lived OIDC/workload identity credentials. The identity provider and setup are TBD.
- Do not store credentials in Git, source files, or logs. No application secret is currently identified; if one is needed, use an approved secret manager (GCP Secret Manager is a demo option, subject to review).
- Confirm data classification, encryption requirements, audit needs, retention, and deletion before using anything other than synthetic or approved demo data.

### Development environment

Use an isolated GCP development project and separate bucket/dataset for the demo; project ID, region, billing limits, and enabled APIs are TBD. Use synthetic or approved non-production data. Test and production environments are out of scope until their requirements are confirmed.

### Deployment approach

Demo proposal: provision bucket, datasets, IAM, and required APIs through reviewed infrastructure as code; tool and CI workflow are TBD. Deploy to development first, validate a sample load and query, and require human review before any expansion to other environments. Rollback and cleanup procedures are TBD.

### Applicable principles

This proposal follows ARCH-001, ARCH-002, ARCH-006, ARCH-007, SEC-IAM-001, SEC-IAM-003, SEC-SEC-001, and DATA-001 through DATA-005. See [ADR-0001](docs/adr/ADR-0001-gcp-demo-data-platform.md); neither this proposal nor the ADR changes or approves the architecture baseline.

The detailed source of truth is under `policies/architecture/`: `architecture-principles.md` and `dependency-principles.md`. Their stable IDs are intended for future automated enforcement.

| Principle | Requirement | Automated check | Human decision |
|---|---|---|---|
| Clear boundaries | Separate domains, infrastructure, policy, and delivery concerns. | Repository structure validation; dependency checks. | Approve boundary changes in review. |
| Explicit dependencies | Dependencies are declared, justified, pinned or constrained, and scanned. | Dependency and license checks. | Approve exceptions and major upgrades. |
| Secure interfaces | APIs validate input, authenticate callers, authorize actions, and avoid leaking sensitive data. | SAST and policy checks. | Review trust-boundary changes. |
| Data ownership | Each dataset has an owner, classification, contract, retention, and access path. | Data-policy and contract checks where configured. | Approve classification and retention. |
| Cloud neutrality | Core rules do not depend on one cloud vendor. | Forbidden-provider checks in core paths. | Approve stack overlays. |
| Observable systems | Services expose health, logs, metrics, traces where applicable, and actionable alerts. | Required observability documentation. | Set service-level objectives. |
| Reproducible delivery | Build once, identify artifacts by commit, and promote the same artifact. | CI/CD workflow checks. | Approve release and rollback policy. |

## Allowed patterns
- Modular monoliths or services with explicit ownership.
- Versioned APIs and data contracts.
- Infrastructure represented as reviewed code.
- Synchronous calls for bounded work and asynchronous messaging for durable workflows.
- Provider-specific implementations behind stack-overlay boundaries.

## Prohibited patterns
- Shared mutable databases across unrelated domains without an approved contract.
- Secrets or environment-specific credentials in source control.
- Unbounded synchronous chains, hidden network calls, or undocumented data copies.
- Vendor-specific code in core policy and governance paths.
- Architecture changes without an ADR when they affect boundaries, data, security, cost, or operations.

## Architecture baseline
The approved architecture boundaries are recorded in `docs/architecture/baseline.yaml` (`ARCH-BL-001` to `ARCH-BL-004`). The baseline locks boundaries, not developer decisions. `bash scripts/validate-baseline.sh` classifies each PR as `NO_BASELINE_IMPACT`, `BASELINE_IMPACT`, or `ARCHITECTURE_CHANGE`. An `ARCHITECTURE_CHANGE` requires an ADR with `Baseline impact: change`; agents advise, CI enforces the deterministic rule, and the architecture owner decides.

## ADR triggers
Create an ADR for a new service, external dependency, data store, public API, model/provider, RAG source, guardrail change, infrastructure pattern, security exception, or breaking change.