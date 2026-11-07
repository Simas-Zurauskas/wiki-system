#!/usr/bin/env python3
"""Compact source inventory for planning wiki-system areas. No agents, no network.

usage: inventory.py [--root DIR] [--expand LOC] [--min LOC] REPO [REPO ...]
       (use "." as REPO for a single-repo workspace)

Prints, per repo: totals, the docs it already has, package scripts, and a folder table
that expands big folders into their children (tests, generated code, assets and
lockfiles excluded).
"""

import argparse
import json
import os
from collections import defaultdict

from common import source_files

DOC_NAMES = ("README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", "ARCHITECTURE.md")


def folder_stats(files):
    """dir prefix (no trailing slash, '' = repo root files) → [files, loc] over all depths."""
    stats = defaultdict(lambda: [0, 0])
    for path, n in files:
        parts = path.split("/")
        for depth in range(1, len(parts)):
            key = "/".join(parts[:depth])
            stats[key][0] += 1
            stats[key][1] += n
    return stats


def children(stats, prefix):
    depth = prefix.count("/") + 1
    return sorted(
        (k for k in stats if k.startswith(prefix + "/") and k.count("/") == depth),
        key=lambda k: -stats[k][1],
    )


def rows_for(stats, prefix, expand, min_loc, max_depth, out):
    kids = children(stats, prefix)
    small_files = small_loc = 0
    for kid in kids:
        files, n = stats[kid]
        if n < min_loc:
            small_files += files
            small_loc += n
            continue
        if n >= expand and kid.count("/") < max_depth and children(stats, kid):
            out.append((kid + "/", files, n, "expanded"))
            rows_for(stats, kid, expand, min_loc, max_depth, out)
        else:
            out.append((kid + "/", files, n, ""))
    if small_files:
        out.append((prefix + "/(smaller folders)", small_files, small_loc, ""))
    if prefix in stats and kids:
        direct_files = stats[prefix][0] - sum(stats[k][0] for k in kids)
        direct_loc = stats[prefix][1] - sum(stats[k][1] for k in kids)
        if direct_files and prefix.count("/") >= 1:
            out.append((prefix + "/(files directly here)", direct_files, direct_loc, ""))


def package_info(repo_dir):
    path = os.path.join(repo_dir, "package.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path) as fh:
            pkg = json.load(fh)
    except (OSError, ValueError):
        return None
    scripts = sorted(k for k in pkg.get("scripts", {}) if not k.startswith("//"))
    return {"main": pkg.get("main"), "scripts": scripts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="+")
    ap.add_argument("--root", default=".")
    ap.add_argument("--expand", type=int, default=4000, help="expand folders above this LOC")
    ap.add_argument("--min", type=int, default=150, help="fold folders below this LOC")
    ap.add_argument("--max-depth", type=int, default=5)
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    for repo in args.repos:
        repo_dir = os.path.join(root, repo)
        files = source_files(root, repo)
        total = sum(n for _, n in files)
        name = os.path.basename(root) if repo == "." else repo
        print(f"## {name}\n")
        print(f"Source: {len(files)} files, {total:,} LOC (tests, generated, assets excluded)\n")

        docs = [d for d in DOC_NAMES if os.path.exists(os.path.join(repo_dir, d))]
        if os.path.isdir(os.path.join(repo_dir, "docs")):
            docs.append("docs/")
        print(f"Docs: {', '.join(docs) if docs else 'none'}")
        pkg = package_info(repo_dir)
        if pkg:
            if pkg["main"]:
                print(f"main: {pkg['main']}")
            print(f"scripts: {', '.join(pkg['scripts']) if pkg['scripts'] else 'none'}")
        print()

        prefix = "" if repo == "." else repo
        stats = folder_stats(files if repo != "." else [("./" + p, n) for p, n in files])
        top = prefix if prefix else "."
        root_files = [(p, n) for p, n in files if p.count("/") == (1 if prefix else 0)]

        out = []
        rows_for(stats, top, args.expand, args.min, args.max_depth, out)
        print("| Folder | Files | LOC |")
        print("| --- | ---: | ---: |")
        for path, nfiles, n, flag in out:
            shown = path[2:] if path.startswith("./") else path
            mark = " ▸" if flag else ""
            print(f"| `{shown}`{mark} | {nfiles} | {n:,} |")
        if root_files:
            n = sum(x for _, x in root_files)
            print(f"| (root files) | {len(root_files)} | {n:,} |")
        print("\n▸ = expanded into the rows below it\n")


if __name__ == "__main__":
    main()
