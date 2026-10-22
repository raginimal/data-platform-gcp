# Engineering Learning Loop

```text
Repeated PR issue or incident
  -> engineering decision
  -> ADR
  -> repository policy
  -> deterministic automated check
  -> future PR protected
```

Review recurring comments, security findings, incidents, operational alerts, and AI failures during retrospectives. Assign an owner and due date. Convert repeatable rules into `policies/` and validation scripts; keep context and exceptions in an ADR. Revisit controls when they create false positives or no longer represent the decision.

The repository maintainer owns a monthly open-exception and recurring-finding review. A quarterly governance review checks CODEOWNERS coverage, stale exceptions, reviewer availability, branch protection, and whether repeated issues have become policy or deterministic checks.
