# Architecture Baseline

Owner: architecture owner. Scope: the approved architecture boundaries recorded in `docs/architecture/baseline.yaml` and how changes to them are detected and approved.

The baseline locks architecture and engineering boundaries, not every developer decision. Prompts, models, context, skills, and agents are not versioned individually; they matter only when a change crosses a baseline boundary.

### ARCH-BL-001 Approved baseline
- **MUST:** keep an architecture baseline at `docs/architecture/baseline.yaml` covering application pattern, major components, technology and platform, data, AI integration and model boundary, security and IAM, deployment, environments, CI/CD, and repository boundaries.
- **MUST NOT:** record routine implementation detail in the baseline.
- **SHOULD:** state for each boundary what is approved and what remains flexible.
- **Human decision:** the architecture owner approves the baseline and sets its status to `approved`.

### ARCH-BL-002 Baseline change control
- **MUST:** include an ADR with `Baseline impact: change` for a change classified `ARCHITECTURE_CHANGE`.
- **MUST:** include an ADR with `Baseline update: yes` when `baseline.yaml` changes.
- **MUST:** fail deterministically when the baseline is `approved` and a required ADR is missing or malformed.
- **Human decision:** the architecture owner approves the ADR and every baseline change.

### ARCH-BL-003 Baseline impact detection
- **MUST:** classify each pull request as `NO_BASELINE_IMPACT`, `BASELINE_IMPACT`, or `ARCHITECTURE_CHANGE` from changed paths and report the boundaries, agents, and approvals involved.
- **MUST NOT:** let the deterministic check decide whether an architectural change is acceptable.
- **SHOULD:** treat `BASELINE_IMPACT` as a routing signal that needs review, not a failure.

### ARCH-BL-004 Advisory baseline analysis
- **MAY:** use agents to assess architectural, security, and AI impact of a change against the baseline and recommend whether architecture review is required.
- **MUST NOT:** let agents approve an architecture change, modify the baseline, bypass CI or an ADR, merge, or approve production.
- **Human decision:** humans own every architecture decision (see `AI-AGT-005`).

## Exceptions
Use the standard exception record and link the ADR when an exception changes a baseline boundary.

## Automation Candidates

| Principle | Automation | Future component |
|---|---|---|
| ARCH-BL-001 | Baseline structure validation | `scripts/validate-baseline.sh` |
| ARCH-BL-002 | ADR metadata and presence check | `scripts/validate-baseline.sh` |
| ARCH-BL-003 | Changed-path classification | `scripts/validate-baseline.sh` |
| ARCH-BL-004 | Baseline impact review skill | `ARCH-SK-001` |
