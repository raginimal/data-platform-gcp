#!/usr/bin/env bash
set -euo pipefail

bash scripts/verify-artifact.sh
if test "${ROLLBACK_APPROVED:-false}" != "true"; then
  echo "FAILED DEVOPS-CD-005: rollback requires explicit human approval." >&2
  exit 1
fi
if test -z "${ROLLBACK_ARTIFACT:-}"; then
  echo "FAILED DEVOPS-CD-005: set ROLLBACK_ARTIFACT to a previously verified artifact." >&2
  exit 1
fi
test -f "$ROLLBACK_ARTIFACT" || { echo "FAILED DEVOPS-CD-005: rollback artifact does not exist: $ROLLBACK_ARTIFACT" >&2; exit 1; }
if test -z "${ROLLBACK_DIGEST:-}"; then
  echo "FAILED DEVOPS-CD-005: set ROLLBACK_DIGEST for the selected artifact." >&2
  exit 1
fi
rollback_digest="$(sha256sum "$ROLLBACK_ARTIFACT" | awk '{print $1}')"
if test "$rollback_digest" != "$ROLLBACK_DIGEST"; then
  echo "FAILED DEVOPS-CD-005: rollback artifact digest does not match ROLLBACK_DIGEST." >&2
  exit 1
fi

if test -z "${ROLLBACK_ADAPTER:-}"; then
  echo "NOT CONFIGURED DEVOPS-CD-005: no stack-overlay rollback adapter is configured."
  exit 0
fi
command -v "$ROLLBACK_ADAPTER" >/dev/null 2>&1 || { echo "FAILED DEVOPS-CD-005: rollback adapter is unavailable: $ROLLBACK_ADAPTER" >&2; exit 1; }
"$ROLLBACK_ADAPTER"
echo "Rollback adapter completed; retain incident and deployment evidence."
