#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

read_value() {
  local prompt="$1" current="$2" value
  read -r -p "$prompt [$current]: " value
  printf '%s' "${value:-$current}"
}

project_name="$(read_value 'Project name' 'CHANGE_ME')"
team="$(read_value 'Team' 'CHANGE_ME')"
owner="$(read_value 'Owner' 'CHANGE_ME')"
language="$(read_value 'Language' 'CHANGE_ME')"
cloud="$(read_value 'Cloud' 'vendor-neutral')"
project_type="$(read_value 'Project type' 'ai-or-data-project')"
repository_organization="$(read_value 'Repository organization' 'CHANGE_ME')"
environments="$(read_value 'Environments (comma-separated)' 'dev,test,prod')"
ai_capabilities="$(read_value 'AI capabilities (comma-separated)' 'none')"

python3 - "$project_name" "$team" "$owner" "$language" "$cloud" "$project_type" "$repository_organization" "$environments" "$ai_capabilities" <<'PY'
from pathlib import Path
import sys

path = Path("PROJECT.yaml")
text = path.read_text()
keys = ["project_name", "team", "owner", "language", "cloud", "project_type", "repository_organization"]
for key, value in zip(keys, sys.argv[1:]):
    text = text.replace(f'{key}: "CHANGE_ME"', f'{key}: "{value}"')
    text = text.replace(f'{key}: "vendor-neutral"', f'{key}: "{value}"')
    text = text.replace(f'{key}: "ai-or-data-project"', f'{key}: "{value}"')
  environments = [item.strip() for item in sys.argv[8].split(",") if item.strip()]
  capabilities = {item.strip().lower() for item in sys.argv[9].split(",") if item.strip()}
  text = text.replace("  - dev\n  - test\n  - prod", "\n".join(f"  - {item}" for item in environments))
  for capability in ("models", "prompts", "rag", "evaluations", "guardrails"):
    text = text.replace(f"  {capability}: false", f"  {capability}: {'true' if capability in capabilities else 'false'}")
path.write_text(text)
PY

printf 'Bootstrap configuration written to PROJECT.yaml. Review it before committing.\n'
