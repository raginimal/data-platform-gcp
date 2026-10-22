# Artifact Promotion

## Artifact identity

An artifact is identified by its repository, commit SHA, release version or tag, artifact name, SHA-256 digest, build timestamp, and workflow run. The manifest and digest are published with the artifact.

## Rules

- Build the artifact exactly once.
- Upload the artifact, manifest, and digest as one release bundle.
- Download and verify the same bundle before every environment stage.
- Do not rebuild for DEV, TEST/UAT, or PROD.
- Retain artifacts according to the selected platform and release policy.
- Record promotion environment, result, identity, approver, and deployment reference.

The core produces a repository-template archive because no application stack exists yet. A stack overlay may replace the archive build with its application artifact while preserving the manifest and digest contract.

## Automation Candidates

| Candidate | Principle ID | Component | Mode | Human approval | Phase |
|---|---|---|---|---|---|
| Manifest generation | DEVOPS-CD-004 | Artifact script | Deterministic | No | 5 |
| Digest verification | DEVOPS-CD-001 | Promotion hook | Deterministic | No | 5 |
| Artifact retention | DEVOPS-REL-002 | Artifact platform | Deterministic | Release owner | 5 |
