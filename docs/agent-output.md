# Agent Output Contract

Agents and skills should emit structured findings using this shape:

```yaml
finding_id: AGENT-FINDING-0001
agent_id: ARCH-AGENT-001
agent_version: 1.0.0
skill_id: ARCH-SK-001
skill_version: 1.0.0
severity: MEDIUM
confidence: HIGH
classification: confirmed-violation
policy_id: ARCH-001
file: path/to/file
line: 1
evidence: Describe the observed evidence.
finding: State the issue clearly.
why_it_matters: Explain the engineering or risk impact.
recommendation: Suggest a focused remediation.
human_action_required: Describe the decision or approval required.
disposition: open
```

## Allowed values

- Severity: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`
- Confidence: `HIGH`, `MEDIUM`, `LOW`
- Classification: `confirmed-violation`, `likely-issue`, `recommendation`, `informational`
- Disposition: `open`, `accepted`, `rejected`, `false-positive`, `resolved`

A finding must not call uncertain reasoning a confirmed violation. Every non-informational finding should reference a policy ID or state why no policy applies. Human disposition remains authoritative.
