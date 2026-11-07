#!/usr/bin/env python3
"""Map source changes to owned areas and referencing pages. Exit 2 requires full fallback."""

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import subprocess
import sys

from common import SKIP_DIRS, evidence_paths, references, referenced, relevant_evidence, load_state, match_any, validate_state, workspace_root
from snapshot import decode_paths, excluded, file_fingerprint, git, source_snapshot

INDEX_HINTS = {
    "package.json", "README.md", "AGENTS.md", "CLAUDE.md", "wrangler.jsonc",
    "app.config.ts", "app.json", "pyproject.toml", "Dockerfile", "Makefile",
}


def diff_paths(data):
    fields = data.split(b"\0")
    paths, i = set(), 0
    while i < len(fields) and fields[i]:
        status = os.fsdecode(fields[i])
        count = 2 if status.startswith(("R", "C")) else 1
        if i + count >= len(fields):
            raise ValueError("malformed git name-status output")
        paths.update(os.fsdecode(p) for p in fields[i + 1:i + count + 1])
        i += count + 1
    return paths


def changes(agents, root, state):
    areas = state["areas"]
    explicit = evidence_paths(state, agents, root)
    touched, referenced_pages = defaultdict(set), defaultdict(set)
    repo_reports, fallbacks = {}, {}
    discovered = []
    if "." not in state["repos"]:
        excluded_repos = set(state.get("excluded_repos", []))
        discovered = sorted(p.name for p in root.iterdir()
                            if p.is_dir() and (p / ".git").exists()
                            and not p.name.startswith(".") and p.name not in SKIP_DIRS
                            and p.resolve() not in (agents.resolve(), *agents.resolve().parents)
                            and p.name not in state["repos"] and p.name not in excluded_repos)
    unavailable = []
    changed, unmapped, hints = set(), set(), set()
    ok_globs = [u["glob"] for u in state.get("unmapped_ok", [])]
    pages = state["managed_pages"]
    page_refs = {p: references(agents / p, root) for p in pages}
    for repo, info in state["repos"].items():
        repo_dir = root / repo
        sha = info.get("sha")
        if not (repo_dir / ".git").exists():
            unavailable.append(repo)
            fallbacks[repo] = "repo unavailable or not a git checkout"
            continue
        try:
            if not sha:
                raise ValueError("no baseline SHA")
            git(repo_dir, "cat-file", "-e", f"{sha}^{{commit}}")
            if info.get("dirty") and "dirty_files" not in info:
                raise ValueError("legacy dirty baseline lacks dirty_files")
            now = source_snapshot(root, {**state, "repos": {repo: info}}, agents)[repo]
            if info.get("fingerprint"):
                if now["fingerprint"] == info["fingerprint"]:
                    repo_reports[repo] = {"baseline": sha, "head": now["sha"], "files": []}
                    continue
            paths = diff_paths(git(repo_dir, "diff", "--name-status", "-z", "-M", sha))
            paths.update(decode_paths(git(repo_dir, "ls-files", "-o", "--exclude-standard", "-z")))
            paths.update(info.get("dirty_files", []))
            paths.update(now["dirty_files"])
            paths = sorted(p for p in paths if relevant_evidence(p, p if repo == "." else f"{repo}/{p}", explicit) and not excluded(repo_dir / p, agents))
            dirty_hashes = info.get("dirty_hashes", {})
            if not isinstance(dirty_hashes, dict):
                raise ValueError("dirty_hashes must be an object")
            paths = [p for p in paths if p not in dirty_hashes
                     or file_fingerprint(repo_dir / p) != dirty_hashes[p]]
            if info.get("fingerprint") and now["fingerprint"] != info["fingerprint"] and not paths:
                raise ValueError("source fingerprint changed without Git-visible paths; full review required")
            head = git(repo_dir, "rev-parse", "HEAD").decode().strip()
            repo_reports[repo] = {"baseline": sha, "head": head, "files": paths}
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            fallbacks[repo] = str(exc)
            continue
        for rel in paths:
            shown = rel if repo == "." else f"{repo}/{rel}"
            changed.add(shown)
            owned = False
            for area in areas:
                ownership = match_any(shown, area.get("paths", []))
                watched = match_any(shown, area.get("watch", []))
                cited = referenced(shown, page_refs[area["page"]])
                owned |= ownership
                if ownership or watched or cited:
                    touched[area["id"]].add(shown)
            for page, tokens in page_refs.items():
                if referenced(shown, tokens):
                    referenced_pages[page].add(shown)
            if not owned and not match_any(shown, ok_globs):
                unmapped.add(shown)
            if Path(rel).name in INDEX_HINTS:
                hints.add(shown)
    return {
        "repos": repo_reports, "changed_files": sorted(changed),
        "touched_areas": {k: sorted(v) for k, v in sorted(touched.items())},
        "referenced_pages": {k: sorted(v) for k, v in sorted(referenced_pages.items())},
        "unmapped": sorted(unmapped), "index_hints": sorted(hints),
        "fallback_repos": fallbacks, "discovered_repos": discovered,
        "unavailable_repos": unavailable,
        "freshness": "partial" if unavailable else ("stale" if changed or fallbacks or discovered else "current"),
        "needs_update": bool(changed or fallbacks or discovered),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("agents_dir", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    agents = args.agents_dir.absolute()
    root = args.root.absolute() if args.root else Path(workspace_root(str(agents)))
    try:
        state = load_state(str(agents))
        errors = validate_state(state)
        if errors:
            raise ValueError("invalid state: " + "; ".join(errors))
        report = changes(agents, root, state)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for repo, data in report["repos"].items():
            print(f"## {repo}: {len(data['files'])} changed since {data['baseline'][:8]} (HEAD {data['head'][:8]})")
        for repo, reason in report["fallback_repos"].items():
            print(f"FULL FALLBACK {repo}: {reason}; run update --full for this repo.")
        if report["discovered_repos"]:
            print("New repos need mapping or explicit exclusion: " + ", ".join(report["discovered_repos"]))
        print(f"Touched areas ({len(report['touched_areas'])}):")
        for area, files in report["touched_areas"].items():
            print(f"- {area}: {len(files)} file(s)")
            for path in files:
                print(f"    {path}")
        for label, key in [("Referencing pages", "referenced_pages"), ("Unmapped changes (review even with zero touched areas)", "unmapped"), ("Index commands/layout hints", "index_hints")]:
            if report[key]:
                print(f"{label}: {json.dumps(report[key], ensure_ascii=False)}")
        if not report["needs_update"]:
            print("Nothing changed since the last run.")
    return 2 if report["fallback_repos"] else 0


if __name__ == "__main__":
    sys.exit(main())
