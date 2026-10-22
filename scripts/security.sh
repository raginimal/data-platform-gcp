#!/usr/bin/env bash
set -euo pipefail

bash scripts/security-check.sh

echo "Core security checks completed; configure dependency, SAST, container, and IaC scanners in the stack overlay."
