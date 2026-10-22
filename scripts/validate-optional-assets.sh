#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

manifests=0
for pattern in package.json package-lock.json yarn.lock pnpm-lock.yaml pyproject.toml requirements.txt poetry.lock Pipfile pom.xml build.gradle build.gradle.kts; do
  if find . -path './.git' -prune -o -type f -name "$pattern" -print -quit | grep -q .; then
    manifests=1
    break
  fi
done
if test "$manifests" -eq 0; then
  echo "NOT CONFIGURED: no supported application dependency manifest detected."
else
  echo "Application dependency manifests detected; configure the selected stack overlay scanner."
  if test -z "${DEPENDENCY_SCANNER:-}"; then
    echo "FAILED ARCH-DEP-004: dependency scanner is required when manifests exist." >&2
    exit 1
  fi
  command -v "$DEPENDENCY_SCANNER" >/dev/null 2>&1 || { echo "FAILED ARCH-DEP-004: configured dependency scanner is unavailable: $DEPENDENCY_SCANNER" >&2; exit 1; }
  "$DEPENDENCY_SCANNER"
fi

if find . -path './.git' -prune -o -type f -name 'Dockerfile*' -print -quit | grep -q .; then
  echo "Container definition detected; configure the selected container scanner."
  if test -z "${CONTAINER_SCANNER:-}"; then
    echo "FAILED SEC-004: container scanner is required when a Dockerfile exists." >&2
    exit 1
  fi
  command -v "$CONTAINER_SCANNER" >/dev/null 2>&1 || { echo "FAILED SEC-004: configured container scanner is unavailable: $CONTAINER_SCANNER" >&2; exit 1; }
  "$CONTAINER_SCANNER"
else
  echo "NOT CONFIGURED: no container definition detected."
fi

if find infrastructure -type f -name '*.tf' -print -quit | grep -q .; then
  echo "Terraform detected; configure the selected IaC scanner."
  if test -z "${IAC_SCANNER:-}"; then
    echo "FAILED SEC-004: IaC scanner is required when Terraform exists." >&2
    exit 1
  fi
  command -v "$IAC_SCANNER" >/dev/null 2>&1 || { echo "FAILED SEC-004: configured IaC scanner is unavailable: $IAC_SCANNER" >&2; exit 1; }
  "$IAC_SCANNER"
else
  echo "NOT CONFIGURED: no Terraform files detected."
fi
