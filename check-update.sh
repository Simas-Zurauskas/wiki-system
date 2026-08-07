#!/usr/bin/env bash
# wiki-system self-update check — fully mechanical; the orchestrator runs it
# and relays its output verbatim. Prints a pre-formatted banner ONLY when the
# local skill clone is behind its origin; otherwise prints nothing. Never
# fails (always exits 0), never prompts, never blocks or delays a run:
# network fetch is TTL-cached (once per 24h), non-interactive, and
# short-circuited on any error — offline runs compare against the last
# fetched state.
set -u

SELF_DIR="$(cd "$(dirname "$0")" && pwd)" || exit 0
cd "$SELF_DIR" || exit 0

# Only meaningful for a git clone with an origin remote.
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
git remote get-url origin >/dev/null 2>&1 || exit 0

# Remote default branch: origin/HEAD when set, else master (the canonical
# wiki-system branch).
branch="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')"
[ -n "$branch" ] || branch=master

# Fetch at most once per TTL. The stamp lives inside .git/ so it never
# dirties the working tree; it is touched only on a SUCCESSFUL fetch, so a
# failed fetch is retried on the next invocation.
GITDIR="$(git rev-parse --git-dir)"
STAMP="$GITDIR/update-check-stamp"
TTL_SECONDS=$((24 * 3600))

needs_fetch=1
if [ -f "$STAMP" ]; then
  now="$(date +%s)"
  mtime="$(stat -f %m "$STAMP" 2>/dev/null || stat -c %Y "$STAMP" 2>/dev/null || echo 0)"
  if [ $((now - mtime)) -lt "$TTL_SECONDS" ]; then
    needs_fetch=0
  fi
fi

if [ "$needs_fetch" = 1 ]; then
  # Non-interactive and bounded: no credential/passphrase prompts, and slow
  # HTTP transfers abort after 10s below 1KB/s.
  if GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=5" \
     git -c http.lowSpeedLimit=1024 -c http.lowSpeedTime=10 \
     fetch --quiet origin "$branch" >/dev/null 2>&1; then
    touch "$STAMP"
  fi
fi

# Compare against the last-known remote state (works even when this run's
# fetch was skipped by the TTL or failed).
git rev-parse --verify --quiet "origin/$branch" >/dev/null 2>&1 || exit 0

behind="$(git rev-list --count "HEAD..origin/$branch" 2>/dev/null)" || exit 0
[ -n "$behind" ] && [ "$behind" -gt 0 ] 2>/dev/null || exit 0

ahead="$(git rev-list --count "origin/$branch..HEAD" 2>/dev/null || echo 0)"
dirty=""
[ -n "$(git status --porcelain 2>/dev/null)" ] && dirty=1

local_sha="$(git rev-parse --short HEAD 2>/dev/null)"
remote_sha="$(git rev-parse --short "origin/$branch" 2>/dev/null)"
local_ver="$(tr -d '[:space:]' <VERSION 2>/dev/null)"
remote_ver="$(git show "origin/$branch:VERSION" 2>/dev/null | tr -d '[:space:]')"

echo "⚠ wiki-system skill update available: local v${local_ver:-?} (${local_sha:-?}) → origin/${branch} v${remote_ver:-?} (${remote_sha:-?}), ${behind} commit(s) behind."
if [ -n "$dirty" ] && [ "$ahead" -gt 0 ]; then
  echo "  This clone has uncommitted changes AND ${ahead} unpushed commit(s) — reconcile manually: cd $SELF_DIR && git status"
elif [ -n "$dirty" ]; then
  echo "  This clone has uncommitted changes — reconcile manually: cd $SELF_DIR && git status"
elif [ "$ahead" -gt 0 ]; then
  echo "  This clone has ${ahead} unpushed commit(s) — reconcile manually: cd $SELF_DIR && git status"
else
  echo "  Update now: git -C $SELF_DIR pull --ff-only origin $branch"
fi
echo "  What changed: git -C $SELF_DIR log --oneline HEAD..origin/$branch  (details: CHANGELOG.md on origin/$branch)"
exit 0
