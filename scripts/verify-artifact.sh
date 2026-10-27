#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/python.sh"

artifact_path="${ARTIFACT_PATH:-}"
if test -z "$artifact_path"; then
  artifact_path="$(find dist -maxdepth 1 -type f -name 'project-template-*.tar.gz' -print -quit)"
fi
test -n "$artifact_path" && test -f "$artifact_path" || { echo "FAILED DEVOPS-CD-002: artifact not found." >&2; exit 1; }
test -f dist/artifact-manifest.json || { echo "FAILED DEVOPS-CD-004: artifact manifest not found." >&2; exit 1; }
test -f dist/artifact.sha256 || { echo "FAILED DEVOPS-CD-002: artifact digest not found." >&2; exit 1; }

digest="$(sha256sum "$artifact_path" | awk '{print $1}')"
expected_digest="$(awk '{print $1}' dist/artifact.sha256)"
expected_name="$(awk '{print $2}' dist/artifact.sha256)"
manifest_digest="$(run_python -c 'import json; print(json.load(open("dist/artifact-manifest.json"))["sha256"])')"
if test "$(basename "$artifact_path")" != "$expected_name"; then
  echo "FAILED DEVOPS-CD-002: artifact filename does not match digest record." >&2
  exit 1
fi
if test "$digest" != "$expected_digest"; then
  echo "FAILED DEVOPS-CD-002: artifact digest does not match digest record." >&2
  exit 1
fi
if test "$digest" != "$manifest_digest"; then
  echo "FAILED DEVOPS-CD-001: artifact digest does not match manifest." >&2
  exit 1
fi

echo "PASS DEVOPS-CD-001/002/004: verified $artifact_path ($digest)."
