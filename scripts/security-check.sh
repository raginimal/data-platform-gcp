#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

# These patterns are high-confidence indicators only; organization scanners may be added by an overlay.
patterns=(
  'AKIA[0-9A-Z]{16}'
  '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'
  'gh[pousr]_[A-Za-z0-9_]{20,}'
  'xox[baprs]-[0-9A-Za-z-]{20,}'
  'AIza[0-9A-Za-z_-]{30,}'
)
for pattern in "${patterns[@]}"; do
  if grep -RInE --exclude-dir=.git --exclude-dir=.plumbline --exclude='security-check.sh' -e "$pattern" .; then
    echo "FAILED SEC-SEC-001: a high-confidence credential pattern was detected." >&2
    echo "Remove the credential, rotate it if exposed, and follow the incident process." >&2
    exit 1
  fi
done

if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect --no-banner --source .
else
  echo "INFO: built-in high-confidence secret checks passed; external scanner not installed."
fi

echo "PASS SEC-SEC-001: no high-confidence committed secret pattern detected."
