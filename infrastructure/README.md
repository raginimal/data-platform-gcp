# Infrastructure as Code

Infrastructure is composed from reviewed modules into isolated DEV, TEST/UAT, and PROD environments.

## Core contract

- Provider-specific resources belong in a selected stack overlay.
- Modules expose documented inputs and outputs and have an owner.
- Environment roots compose modules without sharing mutable state or credentials.
- Remote state must use approved storage, locking, encryption, access control, and retention.
- Plans are reviewed before apply; production apply requires explicit human approval.
- Secrets and state credentials remain outside Git and outside artifacts.
- Drift is detected and reviewed; unmanaged production resources require an approved transition plan.

See `docs/infrastructure/iac-model.md` and the environment directories for the project contract.
