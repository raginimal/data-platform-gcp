#!/usr/bin/env bash
set -euo pipefail

if command -v pre-commit >/dev/null 2>&1 && test -f .pre-commit-config.yaml; then
  pre-commit run --all-files
else
  echo "pre-commit is not installed; no stack-specific lint configured."
fi
