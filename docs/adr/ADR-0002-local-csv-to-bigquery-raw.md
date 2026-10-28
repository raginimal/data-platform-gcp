# ADR-0002: Load synthetic CSV samples into BigQuery raw

- Status: proposed
- Date: 2026-10-28
- Owners: data-platform
- Baseline impact: impact
- Baseline boundaries: BL-DATA
- Baseline update: no
- Approver: architecture owner (human)

## Context

The architecture proposal describes Cloud Storage landing followed by a BigQuery staging load, but leaves the trigger, names, and schemas TBD. The requested development change is to ingest sample sales and customer CSV files into a BigQuery raw dataset. The repository has no sample files, ingestion code, or BigQuery dependency.

## Decision

For a development/demo-only path, provide synthetic CSV fixtures and a Python CLI that validates both files locally and loads them into an existing BigQuery dataset (default `raw`). Use explicit schemas, Application Default Credentials, and `WRITE_EMPTY` so an existing populated table is not overwritten or duplicated by a rerun. This does not configure GCP resources or execute a cloud load. The production/approved architecture remains subject to human review; the proposed Cloud Storage landing flow is not replaced.

## Alternatives considered

- Follow the proposed Cloud Storage landing and staging flow: deferred because the bucket, dataset, schemas, and GCP project are not configured.
- Autodetect schemas: rejected because the persisted data contract requires explicit, validated schemas.
- Append or truncate destination tables: rejected for this sample loader because retries could duplicate data or overwrite existing data.

## Consequences

- Local validation catches malformed headers, missing values, invalid dates and amounts, duplicate IDs, and sales rows without a matching customer before any cloud request.
- The target dataset must already exist. A failed second table load can leave the first table loaded; reruns fail safely when that table is populated.
- The target dataset must have a default table expiration configured; the CLI refuses to load otherwise.
- The sample fixtures contain no names, email addresses, or other direct personal data. Do not substitute production customer data without data-owner and privacy/security approval.
- The Google Cloud BigQuery Python client is an external dependency, constrained to major version 3 and documented in `requirements.txt`.

## Impact and risks

This selects a demo ingestion path and dataset contract within the proposed GCP platform; the architecture owner must review before treating it as approved or production-ready. Verify IAM, billing, project, and location before an actual load. The data owner must configure the raw dataset's default table expiration. The loader uses ADC and stores no credentials.

## Automated controls

- Unit tests cover CSV structure and declared data-quality checks.
- BigQuery load jobs use explicit required schemas, reject bad rows, and require an empty destination.
- Run `python -m unittest tests.unit.test_sample_ingestion -v` and `python -m src.data_platform.ingest_samples --dry-run` before any cloud load.

## Review and expiry

Review before production use or when the Cloud Storage landing/staging design, data classification, schema, retention, or access model is decided. The data owner must set a retention/expiry policy before the sample dataset is retained beyond short-lived development validation.
