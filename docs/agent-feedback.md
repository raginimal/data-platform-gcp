# Agent Feedback Contract

Phase 6 prepares the shape for later learning without implementing a feedback store.

A human disposition may record:

- Finding ID
- Decision: accepted, rejected, false-positive, resolved
- Reviewer role
- Reason and evidence
- Related policy, ADR, issue, or CI rule
- Date and follow-up owner

Accepted recurring findings may become policy or deterministic checks. Rejected or false-positive findings should improve skill guidance. Agents cannot self-approve or self-close governance findings.
