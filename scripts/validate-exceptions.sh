#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

exception_dir="docs/exceptions"
if ! test -d "$exception_dir"; then
  echo "PASS: no exception records are configured."
  exit 0
fi

status=0
while IFS= read -r file; do
  for field in 'Exception ID:' 'Principle ID:' 'Reason' 'Mitigation' 'Approver:' 'Expires or review date:'; do
    grep -qF "$field" "$file" || { echo "FAILED exception metadata: $file missing $field" >&2; status=1; }
  done
done < <(find "$exception_dir" -type f -name '*.md' -print)

if test "$status" -ne 0; then exit "$status"; fi
echo "PASS: exception metadata is complete. Human approval remains mandatory."
