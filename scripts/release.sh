#!/usr/bin/env bash
# Release version N: set VERSION, pin the update workflow to action tag vN, commit, tag vN,
# move the `stable` tag and push. Update CHANGELOG.md first. Usage: scripts/release.sh 38
set -euo pipefail
N="${1:?usage: scripts/release.sh <version number>}"
cd "$(dirname "$0")/.."
grep -q "^## v$N " CHANGELOG.md || { echo "CHANGELOG.md has no '## v$N' entry"; exit 1; }
python3 -B -m unittest discover -s tests >/dev/null 2>&1 || { echo "tests fail; not releasing"; exit 1; }
printf '%s\n' "$N" > VERSION
python3 - "$N" <<'PY'
import re, sys
p = ".github/workflows/update.yml"
s = open(p).read()
new, n = re.subn(r"(uses: Simas-Zurauskas/wiki-system)@v\d+", rf"\1@v{sys.argv[1]}", s)
assert n == 1, "expected exactly one action pin in update.yml"
open(p, "w").write(new)
PY
git add -A
git commit -q -m "v$N"
git tag -a "v$N" -m "wiki-system v$N"
git tag -f -a stable -m "wiki-system stable: v$N" >/dev/null
git push -q origin HEAD
git push -q origin "v$N"
git push -q -f origin stable
echo "released v$N; stable -> $(git rev-parse --short HEAD)"
