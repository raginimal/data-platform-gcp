# Data Classification Principles

Owner: data owner. Scope: project data, prompts, model inputs and outputs, logs, fixtures, and artifacts.

### DATA-CLS-001 Classification
- **MUST:** classify assets as Public, Internal, Confidential, or Restricted/Sensitive before material processing.
- **MUST:** record owner, permitted purpose, access roles, retention, and handling controls.

### DATA-CLS-002 Sensitive handling
- **MUST:** identify PII, regulated data, credentials, customer data, and confidential information before use.
- **MUST:** apply approved storage, transfer, encryption, access, masking, deletion, and incident controls.

### DATA-CLS-003 Access and disclosure
- **MUST:** restrict access to the minimum roles and purposes required.
- **MUST NOT:** disclose restricted data to unapproved tools, model providers, environments, or personnel.

### DATA-CLS-004 Change review
- **MUST:** reassess classification when purpose, source, joining, model use, storage, or exposure changes.

## Exceptions
A classification exception requires data-owner and security/privacy approval, mitigation, review date, and documented impact.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| DATA-CLS-001 | Required classification metadata | Data policy check |
| DATA-CLS-002 | PII and sensitive-data detection | Security/data CI |
| DATA-CLS-003 | Access and destination policy checks | Data governance |
| DATA-CLS-004 | Change-impact review trigger | PR governance |
