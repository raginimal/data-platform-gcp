#!/usr/bin/env bash
set -euo pipefail

body_file="${PR_BODY_FILE:-}"
if test -z "$body_file" && test -n "${GITHUB_EVENT_PATH:-}" && command -v jq >/dev/null 2>&1; then
  body_file="$(mktemp)"
  trap 'rm -f "$body_file"' EXIT
  jq -r '.pull_request.body // empty' "$GITHUB_EVENT_PATH" > "$body_file"
fi

if test -z "$body_file" || ! test -f "$body_file"; then
  echo "INFO: no PR body supplied; PR validation is available in GitHub pull-request context."
  exit 0
fi

required_sections=('## Change' '## Risk and applicability' '## Testing' '## Governance and exceptions')
for section in "${required_sections[@]}"; do
  grep -qF "$section" "$body_file" || { echo "FAILED DEVOPS-PR-001: missing PR section: $section" >&2; exit 1; }
done

grep -qE 'Risk: \[ \] (Low|Medium|High|Critical)' "$body_file" || { echo "FAILED DEVOPS-PR-004: declare a risk classification." >&2; exit 1; }
grep -qF 'Applicable policy IDs:' "$body_file" || { echo "FAILED DEVOPS-PR-004: declare applicable policy IDs." >&2; exit 1; }
grep -qF 'Architecture baseline:' "$body_file" || { echo "FAILED ARCH-BL-003: declare the architecture baseline impact (no impact, baseline impact, or architecture change)." >&2; exit 1; }

section_has_applicable() {
  local heading="$1"
  awk -v heading="$heading" '
    $0 == heading { in_section=1; next }
    in_section && /^## / { in_section=0 }
    in_section { print }
  ' "$body_file" | grep -qF -- '- [x] Applicable'
}

changed_file="${CHANGED_FILES_FILE:-}"
if test -n "$changed_file" && test -f "$changed_file"; then
  if grep -Eq '(^|/)ai/' "$changed_file" && ! section_has_applicable '## AI-specific impact'; then
    echo "FAILED AI-004: AI files changed; mark AI-specific impact as applicable and provide evidence." >&2
    exit 1
  fi
  if grep -Eq '(^|/)infrastructure/|(^|/)config/(dev|test|prod)/' "$changed_file" && ! section_has_applicable '## Engineering impact'; then
    echo "FAILED DEVOPS-ENV-002: infrastructure or environment files changed; disclose configuration impact." >&2
    exit 1
  fi
  if grep -Eq '(^|/)policies/(data|security)/|data-contract|schema' "$changed_file" && ! section_has_applicable '### Data'; then
    echo "FAILED DATA-001: data or policy files changed; disclose data impact." >&2
    exit 1
  fi
fi

echo "PASS DEVOPS-PR-001: required PR governance sections are present."
echo "PASS DEVOPS-PR-004: risk and policy declarations are present."
