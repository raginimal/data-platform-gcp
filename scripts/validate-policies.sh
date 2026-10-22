#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

policy_files=(policies/repository/repository-principles.md policies/architecture/architecture-principles.md policies/architecture/dependency-principles.md policies/architecture/architecture-baseline.md policies/devops/branching.md policies/devops/pull-request.md policies/devops/ci-principles.md policies/devops/cd-principles.md policies/devops/release-management.md policies/devops/environment-management.md policies/security/security-principles.md policies/security/secrets.md policies/security/identity-access.md policies/data/data-principles.md policies/data/data-classification.md policies/data/data-contracts.md policies/ai/ai-engineering-principles.md policies/ai/model-governance.md policies/ai/prompt-governance.md policies/ai/evaluation-principles.md policies/ai/agent-governance.md)

for file in "${policy_files[@]}"; do
  test -f "$file" || { echo "FAILED RP-005: missing policy document: $file" >&2; exit 1; }
  grep -q '## Automation Candidates' "$file" || { echo "FAILED RP-005: missing automation mapping: $file" >&2; exit 1; }
  grep -Eq '\*\*(MUST|SHOULD|MAY):' "$file" || { echo "FAILED RP-005: missing normative vocabulary: $file" >&2; exit 1; }
done

ids_file="$(mktemp)"
trap 'rm -f "$ids_file"' EXIT
grep -RhoE '^### [A-Z]+(-[A-Z]+)?-[0-9]+' policies --include='*.md' | sed 's/^### //' | sort > "$ids_file"
if test -z "$(cat "$ids_file")"; then
  echo "FAILED RP-005: no policy IDs found." >&2
  exit 1
fi
duplicates="$(uniq -d "$ids_file")"
if test -n "$duplicates"; then
  echo "FAILED RP-005: duplicate policy IDs:" >&2
  echo "$duplicates" >&2
  exit 1
fi

policy_reference_pattern='\b(RP|ARCH(-BL|-DEP)?|DEVOPS-(BR|PR|CI|CD|REL|ENV)|SEC(-SEC|-IAM)?|DATA(-CLS|-CON)?|AI(-MOD|-PRM|-EVAL|-AGT)?)-[0-9]+\b'
bad_references=0
while IFS= read -r reference; do
  if ! grep -Rqs "^### $reference\b" policies --include='*.md'; then
    echo "FAILED RP-005: policy reference has no definition: $reference" >&2
    bad_references=1
  fi
done < <(grep -RhoE "$policy_reference_pattern" docs README.md CONTRIBUTING.md AGENTS.md .github --include='*.md' | sort -u)
if test "$bad_references" -ne 0; then exit 1; fi

echo "PASS RP-005: policy documents, IDs, mappings, and references are valid."
