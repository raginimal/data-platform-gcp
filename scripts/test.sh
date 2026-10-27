#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/python.sh"

if test -d tests && find tests -type f -not -name README.md -print -quit | grep -q .; then
  if find tests -type f -name 'test_*.py' -print -quit | grep -q .; then
    run_python -m unittest discover -s tests -v
    exit 0
  fi
  echo "Project tests detected; configure the stack overlay test command in scripts/test.sh."
  exit 1
fi

echo "No application tests configured in the technology-neutral core."
