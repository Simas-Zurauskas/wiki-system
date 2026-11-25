#!/usr/bin/env bash
# Unattended map refresh: prepare, run Claude Code only when needed, conclude.
# Never commits or pushes. Always leaves <work>/status.json; exits 1 only when the run failed.
#
# Required env: WIKI_MAP (map's AGENTS dir), WIKI_ROOT (workspace root), WIKI_WORK (scratch dir
# outside every repo), ANTHROPIC_API_KEY (only when the model runs).
# Optional env: WIKI_FULL=true, WIKI_MODEL, WIKI_MAX_TURNS, WIKI_MAX_BUDGET_USD,
# WIKI_CLAUDE_VERSION (installs that CLI version when `claude` is missing).
set -uo pipefail

SKILL="$(cd "$(dirname "$0")/.." && pwd)"
MAP="$(cd "$WIKI_MAP" && pwd)"
ROOT="$(cd "$WIKI_ROOT" && pwd)"
mkdir -p "$WIKI_WORK"
WORK="$(cd "$WIKI_WORK" && pwd)"
MODEL="${WIKI_MODEL:-claude-sonnet-5-5}"
TURNS="${WIKI_MAX_TURNS:-150}"
BUDGET="${WIKI_MAX_BUDGET_USD:-2}"
CI_PY=(python3 -B "$SKILL/scripts/ci.py")

full=()
[ "${WIKI_FULL:-false}" = "true" ] && full=(--full)
rm -f "$WORK/result.json" "$WORK/claude.json" "$WORK/claude-repair.json" "$WORK/claude.stderr" "$WORK/status.json"

if ! "${CI_PY[@]}" prepare "$MAP" --root "$ROOT" --work "$WORK" ${full[@]+"${full[@]}"}; then
  exit 1  # prepare wrote status.json with the reason
fi

decision="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["decision"])' "$WORK/prepare.json")"
if [ "$decision" = "update" ]; then
  if ! command -v claude >/dev/null 2>&1; then
    if [ -z "${WIKI_CLAUDE_VERSION:-}" ]; then
      echo "claude is not installed and WIKI_CLAUDE_VERSION is unset" > "$WORK/claude.stderr"
    else
      npm install -g --silent "@anthropic-ai/claude-code@${WIKI_CLAUDE_VERSION}" >/dev/null 2>&1
    fi
  fi
  prompt="You are running unattended in CI. Read ${SKILL}/ci.md and follow it exactly.
Skill directory: ${SKILL}
Workspace root (your working directory): ${ROOT}
Map directory: ${MAP}
Work directory: ${WORK} (read brief.md there; write result.json there)"
  # A scrubbed environment and an empty home: no user settings, inherited session or other
  # secret reaches the model, so the permission rules below are the whole policy.
  # Paths in permission rules: a leading // is absolute.
  CLEAN_HOME="$(mktemp -d)"
  CLAUDE_BIN="$(command -v claude)"
  run_claude() {  # $1 prompt, $2 budget, $3 output file
    (cd "$ROOT" && env -i HOME="$CLEAN_HOME" PATH="$PATH" LANG="${LANG:-C.UTF-8}" TMPDIR="${TMPDIR:-/tmp}" \
      ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" "$CLAUDE_BIN" -p "$1" \
      --bare --model "$MODEL" --max-turns "$TURNS" --max-budget-usd "$2" \
      --output-format json --no-session-persistence --permission-mode dontAsk \
      --add-dir "$SKILL" --add-dir "$WORK" \
      --tools "Read,Glob,Grep,Edit,Write,Bash" \
      --allowedTools "Read" "Glob" "Grep" \
        "Edit(/${MAP}/**)" "Write(/${MAP}/**)" "Edit(/${WORK}/result.json)" "Write(/${WORK}/result.json)" \
        "Bash(python3 -B ${SKILL}/scripts/check.py *)" "Bash(ls *)" "Bash(grep *)" \
        "Bash(git -C * diff *)" "Bash(git -C * log *)" "Bash(git -C * show *)" \
        "Bash(git -C * ls-files *)" "Bash(git -C * status *)" \
      --disallowedTools "Agent" "WebFetch" "WebSearch" \
      > "$3" 2>> "$WORK/claude.stderr")
    echo "claude exit=$?"
  }
  run_claude "$prompt" "$BUDGET" "$WORK/claude.json"

  # One repair pass: structure errors after the edits get a short, targeted follow-up run.
  if [ -f "$WORK/result.json" ] && ! python3 -B "$SKILL/scripts/check.py" "$MAP" --root "$ROOT" --structure-only > "$WORK/check-after.txt" 2>&1; then
    echo "structure check failed after the model run; one repair pass"
    errors="$(grep '^ERROR' "$WORK/check-after.txt" | head -20)"
    repair="You are running unattended in CI and already updated the map in ${MAP} following ${SKILL}/ci.md.
The structure check now fails with:
${errors}
Fix only these errors inside the map (cite paths with their repo folder, for example aos-app/src/x.ts),
then run: python3 -B ${SKILL}/scripts/check.py ${MAP} --root ${ROOT} --structure-only
until it passes. Keep ${WORK}/result.json, updating its pages and limitations if needed. Same rules as ci.md."
    run_claude "$repair" "$(python3 -c 'import sys; print(round(float(sys.argv[1]) / 2, 2))' "$BUDGET")" "$WORK/claude-repair.json"
  fi
  rm -rf "$CLEAN_HOME"
fi

"${CI_PY[@]}" conclude "$MAP" --root "$ROOT" --work "$WORK"
