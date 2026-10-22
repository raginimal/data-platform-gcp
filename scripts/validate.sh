#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

required_files=(README.md AGENTS.md CONTRIBUTING.md ARCHITECTURE.md SECURITY.md AI_POLICY.md DATA_POLICY.md PROJECT.yaml plumbline.toml .plumbline/plumbline.py .plumbline/guard.py)
for file in "${required_files[@]}"; do
  test -f "$file" || { echo "Missing required file: $file" >&2; exit 1; }
done

required_dirs=(.github docs src tests ai infrastructure config policies)
for directory in "${required_dirs[@]}"; do
  test -d "$directory" || { echo "Missing required directory: $directory" >&2; exit 1; }
done


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
  --exclude=existing-project.md \
  --exclude=README.md \
  .; then
  echo "FAILED RP-001: unresolved placeholder found outside PROJECT.yaml." >&2
  exit 1
fi


if grep -RInE '(AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9_]{20,})' --exclude-dir=.git --exclude-dir=.plumbline .; then
  echo "Possible secret pattern found" >&2
  exit 1
fi

echo "Repository validation passed."
