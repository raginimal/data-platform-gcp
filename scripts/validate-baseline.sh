#!/usr/bin/env bash
# Architecture Baseline Guard (ARCH-BL-001..003). Classifies changed files; never judges the change.
set -euo pipefail

root_dir="${BASELINE_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$root_dir"

baseline="${BASELINE_FILE:-docs/architecture/baseline.yaml}"
changed_file="${CHANGED_FILES_FILE:-}"

fail() { echo "FAILED $1: $2" >&2; exit 1; }

test -f "$baseline" || fail ARCH-BL-001 "missing architecture baseline: $baseline"

top_value() {
  awk -v k="$1" 'index($0, k ":") == 1 { v = $0; sub(/^[^:]*:[ \t]*/, "", v); gsub(/"/, "", v); print v; exit }' "$baseline"
}

# One boundary per line: id|area|baseline|change_summary|impact_paths|change_paths|agents
records() {
  awk '
    function flush() { if (id != "") print id "|" area "|" base "|" summ "|" imp "|" chg "|" ag; id = "" }
    /^boundaries:/ { inb = 1; next }
    !inb { next }
    /^  - id:/ { flush(); v = $0; sub(/^  - id:[ \t]*/, "", v); gsub(/"/, "", v); id = v; area = base = summ = imp = chg = ag = ""; next }
    /^    [a-z_]+:/ {
      k = $0; sub(/^    /, "", k); v = k; sub(/:.*/, "", k); sub(/^[^:]*:[ \t]*/, "", v)
      gsub(/"/, "", v)
      if (k ~ /_paths$/ || k == "agents") { gsub(/^\[|\]$/, "", v); gsub(/[ \t]*,[ \t]*/, ",", v) }
      if (k == "area") area = v; else if (k == "baseline") base = v; else if (k == "change_summary") summ = v
      else if (k == "impact_paths") imp = v; else if (k == "change_paths") chg = v; else if (k == "agents") ag = v
    }
    END { flush() }
  ' "$baseline"
}

matches_any() {
  local file="$1" list="$2" pattern
  local -a patterns
  IFS=',' read -r -a patterns <<< "$list"
  for pattern in "${patterns[@]}"; do
    # shellcheck disable=SC2053
    if test -n "$pattern" && [[ "$file" == $pattern ]]; then return 0; fi
  done
  return 1
}

agent_name() {
  case "$1" in
    architecture) echo "Architecture Agent" ;;
    security-devops) echo "Security & DevOps Agent" ;;
    ai-engineering) echo "AI Engineering Agent" ;;
    code-quality) echo "Code Quality Agent" ;;
  esac
}

# --- Structure validation (ARCH-BL-001) ---
status="$(top_value status)"
for key in version status approved_by approved_date approving_adr exempt_paths; do
  test -n "$(grep -E "^$key:" "$baseline" || true)" || fail ARCH-BL-001 "baseline is missing required key: $key"
done
case "$status" in
  draft|approved) ;;
  *) fail ARCH-BL-001 "baseline status must be draft or approved, found: $status" ;;
esac
if test "$status" = "approved"; then
  for key in approved_by approved_date approving_adr; do
    test "$(top_value "$key")" != "pending" || fail ARCH-BL-001 "approved baseline must set $key (human approval required)"
  done
fi

mapfile -t boundaries < <(records)
test "${#boundaries[@]}" -gt 0 || fail ARCH-BL-001 "baseline defines no boundaries"
seen_ids=","
for record in "${boundaries[@]}"; do
  IFS='|' read -r id area base summ imp chg agents <<< "$record"
  test -n "$id" && test -n "$area" && test -n "$base" && test -n "$agents" || fail ARCH-BL-001 "boundary '$id' needs id, area, baseline, and agents"
  case "$seen_ids" in *",$id,"*) fail ARCH-BL-001 "duplicate baseline boundary id: $id" ;; esac
  seen_ids="$seen_ids$id,"
  IFS=',' read -r -a agent_list <<< "$agents"
  for agent in "${agent_list[@]}"; do
    test -n "$(agent_name "$agent")" || fail ARCH-BL-001 "boundary $id names unknown agent: $agent"
  done
done
test "$(grep -cE '^    flexible: ' "$baseline")" -eq "${#boundaries[@]}" || fail ARCH-BL-001 "every boundary must state what remains flexible"
echo "PASS ARCH-BL-001: architecture baseline is valid ($status, ${#boundaries[@]} boundaries)."

if test -z "$changed_file" || ! test -f "$changed_file"; then
  echo "INFO: no changed-file list supplied; baseline impact detection runs in PR context."
  exit 0
fi

# --- Change detection (ARCH-BL-003) ---
exempt="$(top_value exempt_paths | sed -e 's/^\[//' -e 's/\]$//' -e 's/[[:space:]]*,[[:space:]]*/,/g')"
files=()
baseline_changed=0
while IFS= read -r file || test -n "$file"; do
  file="${file%$'\r'}"
  test -n "$file" || continue
  if test "$file" = "$baseline"; then baseline_changed=1; continue; fi
  matches_any "$file" "$exempt" && continue
  files+=("$file")
done < "$changed_file"

overall="NO_BASELINE_IMPACT"
raise() { if test "$1" = "ARCHITECTURE_CHANGE" || test "$overall" = "NO_BASELINE_IMPACT"; then overall="$1"; fi; }
required_agents=","

print_block() { # component baseline change class files agents
  echo
  echo "ARCHITECTURE BASELINE IMPACT"
  echo
  echo "Component:"; echo "  $1"
  echo "Baseline:"; echo "  $2"
  echo "Change:"; echo "  $3"
  echo "Changed files:"
  printf '  - %s\n' $5
  echo "Classification:"; echo "  $4"
  echo "Required:"
  local agent
  IFS=',' read -r -a agent_list <<< "$6"
  for agent in "${agent_list[@]}"; do echo "  - $(agent_name "$agent") review"; done
  if test "$4" = "ARCHITECTURE_CHANGE"; then echo "  - ADR (docs/adr/template.md, Baseline impact: change)"; fi
  echo "  - Human approval (architecture owner and affected owners, docs/governance/approval-matrix.md)"
}

for record in "${boundaries[@]}"; do
  IFS='|' read -r id area base summ imp chg agents <<< "$record"
  class="NO_BASELINE_IMPACT"
  hits=()
  for file in "${files[@]+"${files[@]}"}"; do
    if matches_any "$file" "$chg"; then class="ARCHITECTURE_CHANGE"; hits+=("$file")
    elif matches_any "$file" "$imp"; then
      if test "$class" = "NO_BASELINE_IMPACT"; then class="BASELINE_IMPACT"; fi
      hits+=("$file")
    fi
  done
  test "$class" != "NO_BASELINE_IMPACT" || continue
  raise "$class"
  required_agents="$required_agents$agents,"
  change_text="Change touches an approved boundary"
  if test "$class" = "ARCHITECTURE_CHANGE"; then change_text="$summ"; fi
  print_block "$area" "$base" "$change_text" "$class" "${hits[*]}" "$agents"
done

if test "$baseline_changed" -eq 1; then
  raise ARCHITECTURE_CHANGE
  print_block "Architecture Baseline" "Approved architecture baseline ($baseline)" "Baseline file modified" ARCHITECTURE_CHANGE "$baseline" "architecture"
fi

echo
echo "CLASSIFICATION: $overall"

# --- ADR enforcement (ARCH-BL-002) ---
adr_files=()
while IFS= read -r file || test -n "$file"; do
  file="${file%$'\r'}"
  case "$file" in docs/adr/ADR-*.md) test -f "$file" && adr_files+=("$file") ;; esac
done < "$changed_file"

has_adr_field() { # field regex
  local adr
  for adr in "${adr_files[@]+"${adr_files[@]}"}"; do
    grep -qE "^- $1[[:space:]]*\$" "$adr" && return 0
  done
  return 1
}

for adr in "${adr_files[@]+"${adr_files[@]}"}"; do
  value="$(grep -E '^- Baseline impact:' "$adr" | head -n1 | sed 's/^- Baseline impact:[[:space:]]*//' || true)"
  test -n "$value" || continue
  case "$value" in none|impact|change) ;; *) fail ARCH-BL-002 "$adr: Baseline impact must be none, impact, or change (found: $value)" ;; esac
  if test "$value" = "change"; then
    boundaries_value="$(grep -E '^- Baseline boundaries:' "$adr" | head -n1 | sed 's/^- Baseline boundaries:[[:space:]]*//' || true)"
    test -n "$boundaries_value" && test "$boundaries_value" != "none" || fail ARCH-BL-002 "$adr: Baseline impact: change must list Baseline boundaries."
  fi
done

if test "$overall" = "ARCHITECTURE_CHANGE"; then
  missing=""
  has_adr_field 'Baseline impact:[[:space:]]*change' || missing="an ADR with 'Baseline impact: change'"
  if test "$baseline_changed" -eq 1 && ! has_adr_field 'Baseline update:[[:space:]]*yes'; then
    missing="${missing:+$missing and }an ADR with 'Baseline update: yes'"
  fi
  if test -n "$missing"; then
    if test "$status" = "approved"; then
      echo "FAILED ARCH-BL-002: architecture change requires $missing." >&2
      echo "Why: approved architecture boundaries change only through a recorded, human-approved decision." >&2
      echo "Fix: add the ADR under docs/adr/ using docs/adr/template.md and request architecture owner approval." >&2
      echo "Exception: possible only through docs/governance/exceptions.md." >&2
      exit 1
    fi
    echo "WARNING ARCH-BL-002: architecture change needs $missing; enforced once the baseline status is approved."
  else
    echo "PASS ARCH-BL-002: required ADR metadata is present; human approval is still required."
  fi
fi
exit 0
