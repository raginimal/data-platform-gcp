# Data Contract Principles

Owner: data producer and consumer owners. Scope: datasets, events, APIs, features, retrieval sources, and model interfaces.

### DATA-CON-001 Contract required
- **MUST:** define a versioned data contract for shared, persisted, externally consumed, decision-supporting, or model-consumed data.
- **MUST:** identify producer, consumers, owner, purpose, classification, schema, quality, retention, and access.

### DATA-CON-002 Schema and compatibility
- **MUST:** define schema evolution, compatibility, validation, and deprecation behavior.
- **MUST:** review breaking changes with affected consumers before release.

### DATA-CON-003 Quality and failure
- **MUST:** define required fields, valid ranges or semantics, freshness, completeness, and failure behavior where relevant.
- **SHOULD:** publish quality evidence and lineage.

### DATA-CON-004 Privacy and security
- **MUST:** include classification, PII handling, access controls, encryption, and retention in the contract.

## Exceptions
A contract exception requires producer, consumer, data-owner, and appropriate security/privacy approval with mitigation and expiry.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| DATA-CON-001 | Contract presence and metadata check | Data governance CI |
| DATA-CON-002 | Schema compatibility tests | Contract CI |
| DATA-CON-003 | Quality threshold checks | Data CI |
| DATA-CON-004 | Classification/access field validation | Security/data CI |
