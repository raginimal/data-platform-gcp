# Data Principles

Owner: data owner and privacy/security owners. Scope: collection, processing, storage, transfer, access, use, and deletion.

### DATA-001 Purpose and minimization
- **MUST:** define a legitimate purpose, owner, classification, access path, and retention for material data assets.
- **MUST:** collect, copy, expose, and retain only the data needed for the purpose.

### DATA-002 Protection
- **MUST:** apply least-privilege access and approved encryption in transit and at rest.
- **MUST:** prevent sensitive data from unapproved logs, prompts, test fixtures, and telemetry.

### DATA-003 Quality and lineage
- **SHOULD:** define data quality, lineage, provenance, and operational ownership where data affects decisions or production behavior.
- **MUST:** document material transformations and consumers.

### DATA-004 Retention and deletion
- **MUST:** define retention, deletion, legal hold, backup, and recovery behavior appropriate to classification.

### DATA-005 Test data
- **MUST NOT:** use production personal or restricted data in development or automated tests without explicit approval and controls.
- **SHOULD:** use synthetic, masked, or de-identified fixtures.

## Exceptions
Data exceptions require privacy/security review, owner, purpose, risk, mitigation, human approval, and expiry.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| DATA-001 | Required data metadata check | Governance CI |
| DATA-002 | Access, encryption, and log checks | Security/data CI |
| DATA-004 | Retention and deletion metadata check | Data governance |
| DATA-005 | Production-data and PII fixture scan | Security CI |
