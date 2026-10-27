#!/usr/bin/env bash
set -euo pipefail

changed_file="${CHANGED_FILES_FILE:-}"
if test -z "$changed_file" || ! test -f "$changed_file"; then
  echo "INFO: no changed-file list supplied; risk path detection is available in PR context."
  exit 0
fi

risk="LOW"
if grep -Eiq '(^|/)(infrastructure|config/(prod|test)|policies/security|ai/(models|guardrails)|.*(iam|secret|data-contract|prompt|model))' "$changed_file"; then
  risk="HIGH"
elif grep -Eiq '(^|/)(src|config|dependencies|package-lock|poetry.lock|requirements|pom.xml|build.gradle)' "$changed_file"; then
  risk="MEDIUM"
fi

echo "Detected minimum change risk: $risk"
echo "INFO DEVOPS-PR-004: author and accountable reviewer must confirm the final risk classification."
