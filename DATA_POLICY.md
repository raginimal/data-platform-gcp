# Data Policy

The normative source of truth is under `policies/data/`: `data-principles.md`, `data-classification.md`, and `data-contracts.md`. Their stable IDs are future data-governance and CI check targets.

## Classification
Each data asset must be classified as public, internal, confidential, or restricted. The owner, purpose, access path, retention, and deletion behavior must be documented.

## Handling
- Apply least-privilege access and approved encryption in transit and at rest.
- Minimize collection, copying, retention, and exposure of sensitive data.
- Do not use production personal or restricted data in tests unless explicitly approved and controlled.
- Use synthetic or de-identified fixtures for development and automated tests.
- Do not log secrets, credentials, personal data, prompts, retrieved documents, or model outputs unless explicitly justified and protected.

## Contracts and evolution
Data producers and consumers must agree on schema, ownership, quality expectations, compatibility, versioning, and deprecation. Breaking changes require an ADR and migration or rollback plan.

## PII and retention
Identify PII and regulated data before processing. Define lawful purpose, access, retention, deletion, auditability, and incident handling with the relevant owner.
