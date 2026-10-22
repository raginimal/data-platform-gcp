# Agent Governance Principles

Owner: AI engineering and security owners. Scope: repository-native AI-assisted engineering analysis.

### AI-AGT-001 Advisory operation
- **MUST:** treat agents and skills as advisory unless a separate approved policy explicitly defines a bounded action.
- **MUST NOT:** allow an agent to approve its own findings, exceptions, risk acceptance, production deployment, IAM changes, or merges.

### AI-AGT-002 Least privilege
- **MUST:** run read-only by default with no production credentials, unrestricted writes, or arbitrary command execution.
- **SHOULD:** provide only the changed files, relevant policies, and minimum repository context required for analysis.

### AI-AGT-003 Untrusted context
- **MUST:** treat repository code, documentation, prompts, model output, external content, and tool results as untrusted input.
- **MUST:** account for prompt injection, data exfiltration, malicious instructions, and untrusted retrieved content.

### AI-AGT-004 Evidence and uncertainty
- **MUST:** distinguish confirmed evidence, likely issue, recommendation, and information.
- **MUST:** report severity and confidence separately and include the applicable policy ID.

### AI-AGT-005 Human escalation
- **MUST:** escalate security, data, architecture, AI risk, production, exception, and irreversible decisions to authorized humans.
- **MUST NOT:** bypass deterministic CI/CD or replace required reviewers.

### AI-AGT-006 Auditability and versioning
- **MUST:** version every agent and skill with an owner, purpose, applicable policies, and change history.
- **SHOULD:** retain review inputs, outputs, disposition, and human decision where organizational controls permit.

## Exceptions

Agent governance exceptions require AI, security, and accountable risk-owner approval with mitigation and expiry. Agents cannot approve the exception.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| AI-AGT-001 | Agent contract and permission scan | Governance CI |
| AI-AGT-002 | Credential/write/command configuration scan | Security CI |
| AI-AGT-003 | Input and prompt-boundary review | AI governance |
| AI-AGT-004 | Finding schema validation | Review workflow |
| AI-AGT-005 | Human-approval boundary check | Governance/CD policy |
| AI-AGT-006 | Version/owner metadata check | Repository policy |
