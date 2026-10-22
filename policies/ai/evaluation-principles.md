# AI Evaluation Principles

Owner: AI evaluation owner. Scope: model, prompt, retrieval, tool, guardrail, and workflow behavior.

### AI-EVAL-001 Evaluation plan
- **MUST:** define intended behavior, unacceptable behavior, evaluation data provenance, metrics, thresholds, and decision owner before production use.
- **MUST:** protect evaluation data according to its classification.

### AI-EVAL-002 Regression testing
- **MUST:** evaluate material AI behavior changes against an agreed baseline before release.
- **SHOULD:** include representative, adversarial, edge, refusal, grounding, and tool-use cases where relevant.

### AI-EVAL-003 Release thresholds
- **MUST:** define what happens when quality, safety, privacy, latency, or cost thresholds fail.
- **MUST NOT:** declare success based only on anecdotal examples or an AI-generated assessment.

### AI-EVAL-004 Human review
- **MUST:** use qualified human review for consequential outcomes, ambiguous results, and evaluation-set limitations.
- **SHOULD:** track evaluator agreement and known blind spots.

### AI-EVAL-005 Continuous learning
- **SHOULD:** monitor production signals and convert recurring failures into evaluation cases, guardrails, policies, or ADRs.

## Exceptions
An evaluation exception requires risk owner approval, explicit limitation, compensating validation, release restriction, and expiry.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| AI-EVAL-001 | Evaluation metadata and dataset permission check | AI governance CI |
| AI-EVAL-002 | Regression suite execution | AI quality CI |
| AI-EVAL-003 | Threshold and release gate | AI release pipeline |
| AI-EVAL-004 | Human review evidence check | Governance CI |
| AI-EVAL-005 | Failure-to-test tracking | Learning-loop tooling |
