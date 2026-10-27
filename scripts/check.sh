#!/usr/bin/env bash
set -euo pipefail

bash scripts/lint.sh
bash scripts/test.sh
bash scripts/security.sh
bash scripts/validate.sh
bash scripts/plumbline-check.sh --all

echo "Baseline checks passed."
