#!/usr/bin/env bash
# Scenario tests for the Architecture Baseline Guard (ARCH-BL-001..003).
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
guard="$root_dir/scripts/validate-baseline.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

failures=0

run_guard() { # root, files... ; prints output, returns guard exit code
  local root="$1"; shift
  printf '%s\n' "$@" > "$work/changed.txt"
  BASELINE_ROOT="$root" CHANGED_FILES_FILE="$work/changed.txt" bash "$guard" 2>&1
}

expect_class() { # name, expected, files...
  local name="$1" expected="$2"; shift 2
  local out
  out="$(run_guard "$root_dir" "$@")" || { echo "FAIL $name: guard exited non-zero"; echo "$out"; failures=$((failures + 1)); return; }
  if grep -qx "CLASSIFICATION: $expected" <<< "$out"; then echo "PASS $name: $expected"
  else echo "FAIL $name: expected $expected"; echo "$out"; failures=$((failures + 1)); fi
}

expect_exit() { # name, expected_exit, root, files...
  local name="$1" expected="$2" root="$3"; shift 3
  local code=0
  run_guard "$root" "$@" > /dev/null || code=$?
  if test "$code" -eq "$expected"; then echo "PASS $name: exit $code"
  else echo "FAIL $name: expected exit $expected, got $code"; failures=$((failures + 1)); fi
}

expect_class "scenario 1 normal feature" NO_BASELINE_IMPACT src/customer_summary.py
expect_class "scenario 2 new database" ARCHITECTURE_CHANGE infrastructure/database/new_database.tf
expect_class "scenario 3 AI model change" BASELINE_IMPACT ai/models/model.yaml
expect_class "scenario 4 IAM change" BASELINE_IMPACT infrastructure/iam/
expect_class "scenario 5 prompt only" NO_BASELINE_IMPACT ai/prompts/customer-summary.md
expect_class "scenario 5b protected prompt contract" BASELINE_IMPACT ai/prompts/summary-contract.md
expect_class "scenario 6 deployment architecture" ARCHITECTURE_CHANGE infrastructure/
expect_class "exempt folder README" NO_BASELINE_IMPACT infrastructure/modules/README.md
expect_class "highest class wins" ARCHITECTURE_CHANGE ai/models/model.yaml infrastructure/database/db.tf

# Enforcement uses a fixture whose baseline is approved.
fixture="$work/fixture"
mkdir -p "$fixture/docs/architecture" "$fixture/docs/adr"
sed -e 's/^status: draft/status: approved/' \
    -e 's/^approved_by: "pending"/approved_by: "architecture owner"/' \
    -e 's/^approved_date: "pending"/approved_date: "2026-01-01"/' \
    -e 's/^approving_adr: "pending"/approving_adr: "ADR-0001"/' \
    "$root_dir/docs/architecture/baseline.yaml" > "$fixture/docs/architecture/baseline.yaml"

expect_exit "approved: architecture change without ADR fails" 1 "$fixture" infrastructure/database/db.tf
expect_exit "approved: baseline impact does not fail" 0 "$fixture" ai/models/model.yaml
expect_exit "draft: architecture change only warns" 0 "$root_dir" infrastructure/database/db.tf

printf '%s\n' '# ADR-0002' '' '- Baseline impact: change' '- Baseline boundaries: BL-DATA' > "$fixture/docs/adr/ADR-0002-new-store.md"
expect_exit "approved: architecture change with ADR passes" 0 "$fixture" infrastructure/database/db.tf docs/adr/ADR-0002-new-store.md

printf '%s\n' '# ADR-0003' '' '- Baseline impact: change' '- Baseline boundaries: none' > "$fixture/docs/adr/ADR-0003-bad.md"
expect_exit "ADR change without boundaries fails" 1 "$fixture" docs/adr/ADR-0003-bad.md

expect_exit "approved: baseline edit without baseline-update ADR fails" 1 "$fixture" docs/architecture/baseline.yaml docs/adr/ADR-0002-new-store.md
printf '%s\n' '# ADR-0004' '' '- Baseline impact: change' '- Baseline boundaries: BL-DATA' '- Baseline update: yes' > "$fixture/docs/adr/ADR-0004-baseline.md"
expect_exit "approved: baseline edit with baseline-update ADR passes" 0 "$fixture" docs/architecture/baseline.yaml docs/adr/ADR-0004-baseline.md

if test "$failures" -ne 0; then
  echo "FAILED ARCH-BL-003: $failures baseline guard scenario(s) failed." >&2
  exit 1
fi
echo "PASS ARCH-BL-003: baseline guard scenarios passed."
