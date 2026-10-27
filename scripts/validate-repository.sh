#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

required_files=(README.md AGENTS.md CONTRIBUTING.md ARCHITECTURE.md SECURITY.md AI_POLICY.md DATA_POLICY.md PROJECT.yaml Makefile plumbline.toml .plumbline/plumbline.py .plumbline/guard.py .github/CODEOWNERS .github/pull_request_template.md docs/architecture/baseline.yaml)
required_dirs=(.github docs src tests ai infrastructure config policies scripts)

for file in "${required_files[@]}"; do
  test -f "$file" || { echo "FAILED RP-001: missing required file: $file" >&2; exit 1; }
done
for directory in "${required_dirs[@]}"; do
  test -d "$directory" || { echo "FAILED RP-001: missing required directory: $directory" >&2; exit 1; }
done

if test -f CODEOWNERS; then
  echo "FAILED RP-002: duplicate root CODEOWNERS found; use .github/CODEOWNERS." >&2
  exit 1
fi

if grep -RInE \
  'CHANGE_ME|YOUR_|REPLACE_ME' \
  --exclude-dir=.git \
  --exclude=PROJECT.yaml \
  --exclude=CODEOWNERS \
  --exclude=setup.sh \
  --exclude=validate.sh \
  --exclude=validate-repository.sh \
  --exclude=foundation.py \
  --exclude='*.template.yaml' \
  --exclude=devops-developer-guide.html \
  --exclude=README.md \
  --exclude=existing-project.md \
  .; then
  echo "FAILED RP-001: unresolved placeholder found outside approved templates." >&2
  exit 1
fi

echo "PASS RP-001: required repository structure is present."
echo "PASS RP-002: .github/CODEOWNERS is the only authoritative CODEOWNERS file."
