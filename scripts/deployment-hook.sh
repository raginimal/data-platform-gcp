#!/usr/bin/env bash
set -euo pipefail

bash scripts/verify-artifact.sh

if test -z "${DEPLOYMENT_ADAPTER:-}"; then
  echo "NOT CONFIGURED DEVOPS-CD-003: no stack-overlay deployment adapter is configured."
  echo "Artifact verification passed; no deployment was performed."
  exit 0
fi
command -v "$DEPLOYMENT_ADAPTER" >/dev/null 2>&1 || { echo "FAILED DEVOPS-CD-003: deployment adapter is unavailable: $DEPLOYMENT_ADAPTER" >&2; exit 1; }
"$DEPLOYMENT_ADAPTER"
echo "Deployment adapter completed; retain platform deployment evidence."
