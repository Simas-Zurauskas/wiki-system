#!/usr/bin/env python3
"""Check a wiki-system map structurally, not semantically (stdlib, no network).

usage: check.py AGENTS_DIR [--root WORKSPACE] [--coverage]
Errors exit 1; malformed state and missing repos cannot pass as a clean map.
"""

import argparse
import glob
import json
from pathlib import Path
import os
import re
import sys
from collections import defaultdict

from common import (KEEP, MARKER, cited_paths, git_files, is_relevant, is_source, local_links, preservation_blocks,
                    load_state, match_any, source_files, validate_state, workspace_root)

CAPS = {"index.md": 150, "catalog.md": 250, "contracts.md": 150, "catches.md": 150}
AREA_CAPS = 100
OTHER_CAPS = 150
ANCHOR = re.compile(r"\.[A-Za-z0-9]{1,8}:\d+(?:[-–]\d+)?\b")


def caps_for(rel):
    return CAPS.get(rel, AREA_CAPS if rel.startswith("areas/") else OTHER_CAPS)


def path_exists(root, token):
    full = os.path.join(root, token)
    if any(c in token for c in "*?["):
        return bool(glob.glob(full, recursive=True))
    return os.path.exists(full)


def links_to(text, parent, destination):
    """Compare resolved local Markdown destinations, independent of link labels."""
    for target in local_links(text):
        path = os.path.join(parent, target)
        if os.path.realpath(path) == os.path.realpath(destination):
            return True
    return False


def check_project_rules(state, root, agents, errors):
    relative = state.get("project_rules")
    if not relative:
        return
    destination = os.path.join(root, relative)
    if os.path.commonpath([os.path.realpath(destination), os.path.realpath(agents)]) == os.path.realpath(agents):
        errors.append("project_rules: owner policy must live outside generated AGENTS")
    if not os.path.isfile(destination):
        errors.append(f"project_rules: file missing: {relative}")
    index = os.path.join(agents, "index.md")
    if os.path.isfile(index):
        with open(index, encoding="utf-8") as fh:
            if not links_to(fh.read(), agents, destination):
                errors.append("index.md: missing project_rules link")
    # Handwritten entry files are checked only where the owner opted into a block.
    folders = {root, os.path.dirname(agents)}
    folders.update(os.path.join(root, p) for p in state["repos"])
    folders.update(os.path.join(root, p) for p in state.get("excluded_repos", []))
    start, end = "<!-- wiki-system: project-rules -->", "<!-- /wiki-system: project-rules -->"
    for folder in sorted(folders):
        for name in ("AGENTS.md", "CLAUDE.md"):
            path = os.path.join(folder, name)
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as fh:
                body = fh.read()
            shown = os.path.relpath(path, root)
            if start in body or end in body:
                if body.count(start) != 1 or body.count(end) != 1 or body.find(end) < body.find(start):
                    errors.append(f"{shown}: malformed project-rules block")
                    continue
                block = body.split(start, 1)[1].split(end, 1)[0]
                if not links_to(block, folder, destination):
                    errors.append(f"{shown}: missing project_rules link in managed block")
            if name == "CLAUDE.md" and body.startswith(MARKER) and not links_to(body, folder, destination):
                errors.append(f"{shown}: missing project_rules link")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("agents_dir")
    ap.add_argument("--root")
    ap.add_argument("--coverage", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--structure-only", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    agents = os.path.abspath(args.agents_dir)
    root = os.path.abspath(args.root) if args.root else workspace_root(agents)
    errors, warns = [], []
    try:
        state = load_state(agents)
    except (OSError, ValueError) as exc:
        print(f"ERROR .state.json unreadable: {exc}")
        return 1
    problems = validate_state(state)
    if problems:
        for problem in problems:
            print(f"ERROR .state.json: {problem}")
        return 1
    repos = list(state["repos"])
    multi = repos != ["."]
    unavailable = [repo for repo in repos if not os.path.exists(os.path.join(root, repo, ".git"))]
    for repo in unavailable:
        warns.append(f"repo unavailable or not a git checkout: {repo}; source links cannot be checked")

    def in_unavailable(path):
        return any(os.path.commonpath([os.path.abspath(path), os.path.join(root, repo)]) == os.path.join(root, repo)
                   for repo in unavailable)
    pages = state["managed_pages"]
    for rel in pages:
        if not os.path.isfile(os.path.join(agents, rel)):
            errors.append(f"{rel}: required map page missing (listed in managed_pages)")
    index_links = set()
    for rel in pages:
        path = os.path.join(agents, rel)
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeError) as exc:
            errors.append(f"{rel}: unreadable: {exc}")
            continue
        try:
            preservation_blocks(text)
        except ValueError as exc:
            errors.append(f"{rel}: {exc}")
        body = KEEP.sub("", text)
        lines, words = len(body.splitlines()), len(body.split())
        soft = caps_for(rel)
        if not text.startswith(MARKER):
            errors.append(f"{rel}: first line is not the wiki-system marker; unmarked files are owner content")
        if lines > soft:
            warns.append(f"{rel}: {lines} generated lines, over soft budget {soft}")
        if rel.startswith("areas/") and words > 600:
            warns.append(f"{rel}: {words} generated words, over soft budget 600")
        if ANCHOR.search(body):
            warns.append(f"{rel}: line-number anchors should be replaced by paths and symbols")
        for target in local_links(body):
            dest = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if not os.path.exists(dest):
                if in_unavailable(dest):
                    warns.append(f"{rel}: link unavailable ({target})")
                else:
                    errors.append(f"{rel}: broken link ({target})")
            elif rel == "index.md":
                index_links.add(os.path.relpath(dest, agents))
        for token in cited_paths(body):
            if path_exists(root, token) or path_exists(os.path.dirname(path), token):
                continue
            if in_unavailable(os.path.join(root, token)) or in_unavailable(os.path.join(os.path.dirname(path), token)):
                warns.append(f"{rel}: cited path unavailable: {token}")
                continue
            first = token.split("/")[0]
            if multi and first not in repos and not token.startswith(("./", "../")):
                warns.append(f"{rel}: path without a known repo prefix: {token}")
            errors.append(f"{rel}: cited path does not exist: {token}")
    for rel in pages:
        if rel != "index.md" and rel not in index_links:
            warns.append(f"{rel}: not linked from index.md")
    folders = {root, *(os.path.join(root, repo) for repo in repos)}
    for folder in sorted(folders):
        for name in ("AGENTS.md", "CLAUDE.md"):
            entry = os.path.join(folder, name)
            if not os.path.isfile(entry):
                continue
            with open(entry, encoding="utf-8") as fh:
                text = fh.read()
            shown = os.path.relpath(entry, root)
            start, end = "<!-- wiki-system: context -->", "<!-- /wiki-system: context -->"
            managed = text.startswith(MARKER)
            if start in text or end in text:
                if text.count(start) != 1 or text.count(end) != 1 or text.find(end) < text.find(start):
                    errors.append(f"{shown}: malformed context block")
                    continue
                body = text.split(start, 1)[1].split(end, 1)[0]
            elif managed:
                body = text
                if len(KEEP.sub("", text).splitlines()) > 60:
                    warns.append(f"{shown}: over 60 generated lines (soft budget)")
            else:
                continue
            if not links_to(body, folder, os.path.join(agents, "index.md")):
                errors.append(f"{shown}: does not link to map index.md")
            if state.get("project_rules") and not links_to(body, folder, os.path.join(root, state["project_rules"])):
                errors.append(f"{shown}: missing project_rules link in context")
            for target in local_links(body):
                if not os.path.exists(os.path.join(folder, target)):
                    errors.append(f"{shown}: broken link ({target})")
    check_project_rules(state, root, agents, errors)
    if args.coverage:
        globs = [g for a in state["areas"] for g in a["paths"]]
        globs += [u["glob"] for u in state.get("unmapped_ok", [])]
        gaps = defaultdict(lambda: [0, 0])
        for repo in repos:
            if not os.path.exists(os.path.join(root, repo, ".git")):
                continue
            for p, n in source_files(root, repo):
                if os.path.abspath(os.path.join(root, p)).startswith(agents + os.sep):
                    continue
                if not match_any(p, globs):
                    gaps[os.path.dirname(p) or "(root)"][0] += 1
                    gaps[os.path.dirname(p) or "(root)"][1] += n
            evidence = []
            for p in git_files(os.path.join(root, repo)):
                shown = p if repo == "." else f"{repo}/{p}"
                if is_relevant(p) and not is_source(p) and not match_any(shown, globs):
                    if not os.path.abspath(os.path.join(root, repo, p)).startswith(agents + os.sep):
                        evidence.append(shown)
            if evidence:
                warns.append(f"navigation evidence outside area ownership ({len(evidence)}): " + ", ".join(evidence[:8]))
        for folder, (nf, n) in sorted(gaps.items(), key=lambda kv: -kv[1][1]):
            warns.append(f"uncovered: {folder}/ ({nf} files, {n:,} LOC)")
    freshness = None
    if not args.structure_only:
        from changed import changes
        try:
            freshness = changes(Path(agents), Path(root), state)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            errors.append(f"freshness could not be checked: {exc}")
    report = {"structure": "invalid" if errors else "ok", "errors": errors, "warnings": warns,
              "managed_pages": pages, "freshness": freshness["freshness"] if freshness else "not_checked",
              "changes": freshness}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for line in errors:
            print(f"ERROR {line}")
        for line in warns:
            print(f"WARN  {line}")
        print(f"\nStructure: {report['structure']} · {len(pages)} managed pages · {len(errors)} errors · {len(warns)} warnings")
        print(f"Freshness: {report['freshness']}; structural checks do not verify semantic accuracy.")
        if freshness and freshness["fallback_repos"]:
            print("Full source review required: " + json.dumps(freshness["fallback_repos"]))
    return 1 if errors else (2 if freshness and freshness["needs_update"] else 0)



if __name__ == "__main__":
    sys.exit(main())
