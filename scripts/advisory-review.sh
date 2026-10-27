#!/usr/bin/env bash
# Advisory only: routes changed files to review agents using config/ai/agent-routing.yaml. Always exits 0.
set -uo pipefail

ROUTING="config/ai/agent-routing.yaml"
BASE_REF="${1:-${GITHUB_BASE_REF:-main}}"
OUT="${GITHUB_STEP_SUMMARY:-/dev/stdout}"

if git rev-parse --verify -q "origin/${BASE_REF}" >/dev/null; then
  changed=$(git diff --name-only "origin/${BASE_REF}...HEAD")
else
  changed=$(git diff --name-only HEAD~1 2>/dev/null || true)
fi

declare -A agent_files
declare -A file_agents
unknown_agent=$(awk '/^unknown_changes:/ {print $2}' "$ROUTING")

# Flatten rules into "pattern|agent1,agent2" lines.
rules=$(awk '
  /^  - match:/ { if (pats != "") print pats "|" ags; pats=""; ags=""; mode="m"; next }
  /^    agents:/ { mode="a"; next }
  /^[a-z_]+:/ { mode="" }
  mode=="m" && /^      - / { sub(/^      - /, ""); pats = pats (pats==""?"":",") $0 }
  mode=="a" && /^      - / { sub(/^      - /, ""); ags = ags (ags==""?"":",") $0 }
  END { if (pats != "") print pats "|" ags }
' "$ROUTING")

while IFS= read -r f; do
  [ -z "$f" ] && continue
  matched=""
  while IFS='|' read -r pats ags; do
    IFS=',' read -ra plist <<<"$pats"
    for p in "${plist[@]}"; do
      glob="${p//\*\*/*}"
      # shellcheck disable=SC2254
      case "$f" in $glob) matched="${matched},${ags}"; break ;; esac
    done
  done <<<"$rules"
  [ -z "$matched" ] && matched=",${unknown_agent}"
  for a in $(echo "${matched#,}" | tr ',' '\n' | sort -u); do
    agent_files[$a]+="${f}"$'\n'
    file_agents[$f]+="${a} "
  done
done <<<"$changed"

{
  echo "## Gate 5 - Advisory AI review"
  echo
  echo "Mode: advisory, read-only. This job never fails the build; deterministic checks and human approvals remain authoritative."
  echo
  if [ -z "$changed" ]; then
    echo "No changed files detected."
  else
    echo "### Suggested reviewers"
    echo
    echo "| Agent | Files | Instructions |"
    echo "|---|---|---|"
    for a in $(printf '%s\n' "${!agent_files[@]}" | sort); do
      n=$(printf '%s' "${agent_files[$a]}" | grep -c .)
      echo "| \`$a\` | $n | \`agents/$a/AGENT.md\` |"
    done
    echo
    echo "### File to agent mapping"
    echo
    echo "| File | Agents |"
    echo "|---|---|"
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      echo "| \`$f\` | ${file_agents[$f]} |"
    done <<<"$changed"
    echo
    echo "### Next steps"
    echo
    echo "- Run the listed agents in the editor and record findings using \`docs/agent-output.md\`."
    echo "- Attach findings (or a note that none apply) to the PR; human reviewers decide disposition."
  fi
} >>"$OUT"

exit 0
