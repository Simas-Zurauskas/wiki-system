#!/usr/bin/env python3
"""Capture source before writing a map; finalize only if that source and keep blocks survive."""

import argparse
import hashlib
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

from common import MARKER as TEXT_MARKER, evidence_paths, dependency_inputs, extra_dependency_files, relevant_evidence, is_sensitive, load_state, preservation_blocks, validate_state, workspace_root

MARKER = TEXT_MARKER.encode()


def git(repo_dir, *args):
    result = subprocess.run(
        ["git", "-C", str(repo_dir), *args], capture_output=True, timeout=30
    )
    if result.returncode:
        # Do not echo Git stderr: hooks/configuration can contain private values.
        raise ValueError(f"git {args[0]} failed for {repo_dir}")
    return result.stdout


def decode_paths(data):
    return [os.fsdecode(p) for p in data.split(b"\0") if p]


def excluded(path, agents):
    if path == agents or agents in path.parents:
        return True
    if is_sensitive(path.as_posix()):
        return True
    if path.name in ("CLAUDE.md", "AGENTS.md") and path.is_file() and not path.is_symlink():
        with path.open("rb") as fh:
            return fh.read(len(MARKER)).startswith(MARKER)
    return False


def file_fingerprint(path):
    """Hash file bytes and mode, or a symlink target without following it."""
    digest = hashlib.sha256()
    if path.is_symlink():
        digest.update(b"symlink\0" + os.fsencode(os.readlink(path)))
    elif path.exists():
        digest.update(str(path.stat().st_mode).encode() + b"\0")
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                digest.update(chunk)
    else:
        return "deleted"
    return digest.hexdigest()


def source_snapshot(root, state, agents):
    repos = {}
    explicit = evidence_paths(state, agents, root)
    dependencies = dependency_inputs(state, agents, root)
    for repo in state["repos"]:
        repo_dir = root / repo
        if not (repo_dir / ".git").exists():
            continue  # Keep its old baseline; callers report partial availability.
        sha = git(repo_dir, "rev-parse", "HEAD").decode().strip()
        files = set(decode_paths(git(repo_dir, "ls-files", "-co", "--exclude-standard", "-z")))
        extra = extra_dependency_files(root, repo, dependencies) - files
        files = sorted(files | extra)
        dirty = set(decode_paths(git(repo_dir, "diff", "--no-renames", "--name-only", "-z", "HEAD")))
        dirty.update(decode_paths(git(repo_dir, "ls-files", "-o", "--exclude-standard", "-z")))
        dirty.update(extra)
        dirty = sorted(p for p in dirty if relevant_evidence(p, p if repo == "." else f"{repo}/{p}", explicit) and not excluded(repo_dir / p, agents))
        dirty_set, dirty_hashes = set(dirty), {}
        digest = hashlib.sha256()
        # Content identity is independent of HEAD: committing reviewed dirty
        # content alone must not repeat writer work. Capture still records SHA.
        for rel in files:
            path = repo_dir / rel
            if not relevant_evidence(rel, rel if repo == "." else f"{repo}/{rel}", explicit) or excluded(path, agents):
                continue
            digest.update(os.fsencode(rel) + b"\0")
            fingerprint = file_fingerprint(path)
            digest.update(fingerprint.encode())
            digest.update(b"\0")
            if rel in dirty_set:
                dirty_hashes[rel] = fingerprint
        for rel in dirty_set - dirty_hashes.keys():
            # Staged deletions/rename old paths no longer appear in ls-files.
            dirty_hashes[rel] = file_fingerprint(repo_dir / rel)
        repos[repo] = {
            "sha": sha, "dirty": bool(dirty), "dirty_files": dirty,
            "dirty_hashes": dirty_hashes, "fingerprint": digest.hexdigest(),
        }
    return repos


def keep_blocks(agents, state):
    blocks = {}
    for rel in state["managed_pages"]:
        page = agents / rel
        if not page.is_file():
            continue
        if page.is_symlink() or is_sensitive(page.relative_to(agents).as_posix()):
            continue
        data = page.read_bytes()
        if not data.startswith(MARKER):
            continue  # Whole-file preservation handles opaque owner content.
        try:
            found = preservation_blocks(data.decode("utf-8"))
        except ValueError as exc:
            raise ValueError(f"{page.relative_to(agents)}: {exc}") from exc
        if found:
            blocks[page.relative_to(agents).as_posix()] = found
    return blocks


def handwritten_files(agents, state, capture_path=None):
    """Ownership requires both a declared managed path and the generated marker."""
    result = {}
    for page in sorted(agents.rglob("*")):
        if not page.is_file() and not page.is_symlink():
            continue
        rel = page.relative_to(agents).as_posix()
        if rel in (".state.json", ".state.lock") or page == capture_path or is_sensitive(rel):
            continue  # Tool artifacts and sensitive paths are excluded explicitly.
        if rel in state["managed_pages"] and not page.is_symlink() and page.read_bytes().startswith(MARKER):
            continue
        result[rel] = file_fingerprint(page)
    return result


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=path.parent, encoding="utf-8", delete=False) as fh:
            name = fh.name
            json.dump(value, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command, flag in [("capture", "--out"), ("finalize", "--snapshot")]:
        sub = commands.add_parser(command)
        sub.add_argument("agents_dir", type=Path)
        sub.add_argument(flag, required=True, type=Path)
        sub.add_argument("--root", type=Path)
    args = parser.parse_args()
    agents = args.agents_dir.absolute()
    root = args.root.absolute() if args.root else Path(workspace_root(str(agents)))
    try:
        state_bytes = (agents / ".state.json").read_bytes()
        state = json.loads(state_bytes)
        errors = validate_state(state)
        if errors:
            raise ValueError("invalid state: " + "; ".join(errors))
        current = source_snapshot(root, state, agents)
        unavailable = sorted(set(state["repos"]) - set(current))
        if args.command == "capture":
            output = args.out.absolute()
            if output.exists() or output.is_symlink():
                try:
                    previous = json.loads(output.read_text())
                except (OSError, ValueError):
                    previous = None
                if (output.is_symlink() or not isinstance(previous, dict)
                        or previous.get("root") != str(root) or previous.get("agents") != str(agents)
                        or "baseline_repos" not in previous):
                    raise ValueError("capture output already exists and is not this map's snapshot; refusing to overwrite it")
            for repo in state["repos"]:
                if (root / repo) in output.parents and not (agents == output.parent or agents in output.parents):
                    raise ValueError("snapshot output must be outside source repos or inside the generated map")
            atomic_json(args.out, {
                "root": str(root), "agents": str(agents), "repos": current,
                "baseline_repos": state["repos"], "baseline_generated": state.get("generated"),
                "keep_blocks": keep_blocks(agents, state), "handwritten_files": handwritten_files(agents, state, output),
            })
            print(f"Captured {len(current)} repo(s); baseline unchanged; unavailable: {unavailable}.")
            return 0
        saved = json.loads(args.snapshot.read_text())
        if saved.get("root") != str(root) or saved.get("agents") != str(agents):
            raise ValueError("snapshot belongs to another workspace/map")
        if saved.get("repos") != current:
            raise ValueError("source changed after capture; re-review affected pages and capture again")
        if saved.get("baseline_repos") != state["repos"] or saved.get("baseline_generated") != state.get("generated"):
            raise ValueError("baseline changed after capture; refusing to overwrite another run")
        for page, fingerprint in saved.get("handwritten_files", {}).items():
            if file_fingerprint(agents / page) != fingerprint:
                raise ValueError(f"handwritten file changed or disappeared: {page}")
        now_blocks = keep_blocks(agents, state)
        for page, blocks in saved.get("keep_blocks", {}).items():
            if now_blocks.get(page) != blocks:
                raise ValueError(f"keep blocks changed or disappeared: {page}")
        checked_pages = {page: file_fingerprint(agents / page) for page in state["managed_pages"]}
        check = subprocess.run(
            [sys.executable, "-B", str(Path(__file__).with_name("check.py")), str(agents), "--root", str(root), "--structure-only"],
            capture_output=True, text=True, timeout=60,
        )
        if check.returncode:
            raise ValueError("map check failed; baseline unchanged:\n" + check.stdout.strip())
        # Serialize finalizers; re-read the state under the lock before replacing it.
        # Ordinary editor writes are detected too; an external editor does not share
        # this lock, so no file protocol can make its arbitrary writes transactional.
        with (agents / ".state.lock").open("a") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            if (agents / ".state.json").read_bytes() != state_bytes:
                raise ValueError("state changed during final checks; baseline unchanged")
            if source_snapshot(root, state, agents) != current:
                raise ValueError("source changed during final checks; baseline unchanged")
            for page, fingerprint in saved.get("handwritten_files", {}).items():
                if file_fingerprint(agents / page) != fingerprint:
                    raise ValueError(f"handwritten file changed during final checks: {page}")
            if checked_pages != {page: file_fingerprint(agents / page) for page in state["managed_pages"]}:
                raise ValueError("managed pages changed during final checks; baseline unchanged")
            if keep_blocks(agents, state) != now_blocks:
                raise ValueError("keep blocks changed during final checks")
            state["version"] = 3
            state["repos"].update(current)
            state["snapshot_status"] = "partial" if unavailable else "current"
            state["unavailable_repos"] = unavailable
            state["generated"] = datetime.now(timezone.utc).isoformat(timespec="microseconds")
            state["generator_version"] = "wiki-system v" + Path(__file__).parent.parent.joinpath("VERSION").read_text().strip()
            atomic_json(agents / ".state.json", state)
        print(f"Finalized {len(current)} repo(s); source stable, keep blocks and handwritten files preserved, structure passed; {state['snapshot_status']} (unavailable: {unavailable}).")
        return 0
    except (OSError, ValueError, TypeError, KeyError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
