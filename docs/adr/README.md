# Architecture Decision Records

Use `template.md` for decisions affecting boundaries, dependencies, data, security, infrastructure, models, or operations.

Name files `ADR-NNNN-title.md`. When the Architecture Baseline Guard reports `ARCHITECTURE_CHANGE`, the ADR must set `Baseline impact: change` and list the affected `Baseline boundaries`; changing `docs/architecture/baseline.yaml` also requires `Baseline update: yes` (`ARCH-BL-002`). Normal feature work needs no ADR. The architecture owner approves the ADR.
