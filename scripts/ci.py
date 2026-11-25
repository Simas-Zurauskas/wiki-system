#!/usr/bin/env python3
"""Unattended map refresh around a model run: prepare before it, conclude after it.

prepare  plans the run without a model, captures the source snapshot and writes brief.md.
conclude validates the model's result, confines its edits, finalizes and writes status.json.
Both write JSON into --work (outside every repo). Exit 0 unless the run failed.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from changed import changes
from common import load_state, validate_state, workspace_root
from snapshot import atomic_json, file_fingerprint, git

SCRIPTS = Path(__file__).resolve().parent
PROMPT = "TASK-WORKFLOW-PROMPT.md"
OUTCOMES = ("updated", "no_change", "failed")
DIFF_LIMIT = 400_000  # bytes of diff handed to the model per repo; it reads files for the rest


def run_script(name, *args):
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / name), *map(str, args)],
                          capture_output=True, text=True, timeout=300)


def structure_errors(agents, root):
    result = run_script("check.py", agents, "--root", root, "--structure-only", "--json")
    try:
        return json.loads(result.stdout)["errors"]
    except (ValueError, KeyError):
        return [(result.stdout or result.stderr).strip() or "check.py produced no report"]


def wiki_top(agents):
    return Path(git(agents, "rev-parse", "--show-toplevel").decode().strip()).resolve()


def in_top(path, top):
    """Path relative to the docs repo top; Git reports symlink-resolved paths."""
    return path.resolve().relative_to(top)


def wiki_changes(top):
    """Paths changed in the docs repo's working tree, relative to its top."""
    out = git(top, "status", "--porcelain=v1", "-z", "--untracked-files=all").decode()
    paths, fields, i = [], out.split("\0"), 0
    while i < len(fields) and fields[i]:
        status, path = fields[i][:2], fields[i][3:]
        paths.append(path)
        i += 2 if "R" in status or "C" in status else 1
    return sorted(paths)


def repo_state(root, repos):
    found = {}
    for repo in repos:
        repo_dir = root / repo
        if (repo_dir / ".git").exists():
            found[repo] = {"head": git(repo_dir, "rev-parse", "HEAD").decode().strip(),
                           "status": git(repo_dir, "status", "--porcelain=v1", "-z").decode()}
    return found


def has_commit(repo_dir, sha):
    try:
        git(repo_dir, "cat-file", "-e", f"{sha}^{{commit}}")
        return True
    except ValueError:
        return False


def brief(plan, report, errors):
    lines = ["# Wiki CI run", "", f"Mode: **{plan['mode']}**.", ""]
    if plan["mode"] == "full":
        lines.append("Revisit every documented area (`update --full`).")
    for repo, reason in report["fallback_repos"].items():
        lines.append(f"- `{repo}` has no usable baseline ({reason}); review its whole map scope.")
    for repo in report["unavailable_repos"]:
        lines.append(f"- `{repo}` is not checked out: keep its pages, mark dependent claims unverified.")
    for repo in report["discovered_repos"]:
        lines.append(f"- `{repo}` is a new sibling repo: leave it unmapped and name it in `limitations`.")
    if errors:
        lines += ["", "Structure errors to fix:"] + [f"- {e}" for e in errors]
    if report["changed_files"]:
        lines += ["", "Changed source since the baseline:"] + [f"- `{p}`" for p in report["changed_files"]]
    if report["touched_areas"]:
        lines += ["", "Touched areas:"] + [f"- {a}: {len(f)} file(s)" for a, f in report["touched_areas"].items()]
    for key, label in (("unmapped", "Unmapped changes"), ("index_hints", "Index hints")):
        if report[key]:
            lines += ["", f"{label}:"] + [f"- `{p}`" for p in report[key]]
    if plan.get("diffs"):
        lines += ["", "What changed, as unified diffs (read these, then the files themselves):"]
        lines += [f"- `{repo}`: `{path}`" for repo, path in plan["diffs"].items()]
    return "\n".join(lines) + "\n"


def prepare(agents, root, work, full):
    state = load_state(str(agents))
    problems = validate_state(state)
    if problems:
        raise ValueError("invalid state: " + "; ".join(problems))
    top = wiki_top(agents)
    if top == work.resolve() or top in work.resolve().parents:
        raise ValueError("--work must be outside the docs repo")
    map_dir = in_top(agents, top).as_posix() + "/"
    pending = wiki_changes(top)
    if any(p.startswith(map_dir) for p in pending):
        raise ValueError(f"the map in {top} has uncommitted changes; start from a clean map")
    report = changes(agents, root, state)
    errors = structure_errors(agents, root)
    needs = bool(full or report["needs_update"] or errors)
    ranges = {}
    for repo, info in state["repos"].items():
        repo_dir = root / repo
        if not (repo_dir / ".git").exists():
            continue
        head = git(repo_dir, "rev-parse", "HEAD").decode().strip()
        base = info.get("sha")
        ranges[repo] = {"from": base if base and has_commit(repo_dir, base) else None, "to": head}
    diffs = {}
    for repo, r in ranges.items():
        # The model has no shell: hand it the baseline-to-head diff as a file.
        if r["from"] and r["from"] != r["to"]:
            patch = subprocess.run(["git", "-C", str(root / repo), "diff", "--no-ext-diff", "--no-textconv",
                                    r["from"], r["to"]], capture_output=True, timeout=120).stdout[:DIFF_LIMIT]
            name = f"changes-{repo.replace('/', '_') if repo != '.' else 'repo'}.diff"
            (work / name).write_bytes(patch)
            diffs[repo] = str(work / name)
    snapshot = work / "snapshot.json"
    if snapshot.exists():
        snapshot.unlink()
    capture = run_script("snapshot.py", "capture", agents, "--root", root, "--out", snapshot)
    if capture.returncode:
        raise ValueError("snapshot capture failed: " + capture.stderr.strip())
    plan = {
        "decision": "update" if needs else "skip",
        # Every repo is exactly at its baseline: nothing to record, so conclude leaves the map alone.
        "current": not needs and bool(ranges) and all(r["from"] == r["to"] for r in ranges.values()),
        "mode": "full" if full or report["fallback_repos"] else "incremental",
        "agents": str(agents), "root": str(root), "wiki": str(top),
        "prompt_existed": (agents.parent / PROMPT).exists(),
        "wiki_pending": {p: file_fingerprint(top / p) for p in pending},
        "ranges": ranges, "diffs": diffs, "repos": repo_state(root, state["repos"]),
        "structure_errors": errors, "changes": report,
    }
    atomic_json(work / "prepare.json", plan)
    (work / "brief.md").write_text(brief(plan, report, errors))
    print(f"decision={plan['decision']} mode={plan['mode']} changed={len(report['changed_files'])} "
          f"structure_errors={len(errors)}")
    return plan


def read_result(work):
    path = work / "result.json"
    if not path.is_file():
        return None, "the model wrote no result.json"
    try:
        result = json.loads(path.read_text())
    except ValueError as exc:
        return None, f"result.json is not JSON: {exc}"
    if not isinstance(result, dict) or result.get("outcome") not in OUTCOMES:
        return None, "result.json needs outcome updated|no_change|failed"
    for key in ("pages", "limitations"):
        if not isinstance(result.get(key, []), list):
            return None, f"result.json {key} must be a list"
    return result, None


def model_report(work):
    """Cost and stop reason from `claude -p --output-format json`: the main run plus any repair pass."""
    report = None
    for path in [work / "claude.json", *sorted(work.glob("claude-repair*.json"))]:
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if isinstance(data, list):  # stream/verbose output: the result message is last
            data = next((m for m in reversed(data) if isinstance(m, dict) and m.get("type") == "result"), {})
        if not isinstance(data, dict):
            continue
        if report is None:
            report = {key: data.get(key) for key in ("subtype", "is_error", "num_turns", "total_cost_usd")}
            if data.get("is_error"):
                report["error"] = " ".join(str(data.get("result") or data.get("api_error_status") or "").split())[:200]
            continue
        report["repair_pass"] = True
        report["subtype"], report["is_error"] = data.get("subtype"), data.get("is_error")
        for key in ("num_turns", "total_cost_usd"):
            report[key] = (report.get(key) or 0) + (data.get(key) or 0)
    return report


def conclude(agents, root, work):
    plan = json.loads((work / "prepare.json").read_text())
    if plan["agents"] != str(agents) or plan["root"] != str(root):
        raise ValueError("prepare.json belongs to another map or workspace")
    status = {"status": "failed", "summary": "", "pages": [], "limitations": [],
              "ranges": plan["ranges"], "mode": plan["mode"], "reason": ""}

    model = model_report(work)
    if model:
        status["model"] = model

    def fail(reason):
        if model and model.get("error"):
            reason = f"the model run failed ({model['error']}); {reason}"
        elif model and model.get("subtype") not in (None, "success"):
            reason = f"model run ended with {model['subtype']}; {reason}"
        status["reason"] = reason
        atomic_json(work / "status.json", status)
        print(f"status=failed reason={reason}")
        return status

    if plan["decision"] == "update":
        result, problem = read_result(work)
        if problem:
            return fail(problem)
        status["summary"] = str(result.get("summary", ""))[:500]
        status["limitations"] = [str(x)[:300] for x in result.get("limitations", [])][:10]
        if result["outcome"] == "failed":
            return fail(status["summary"] or "the model reported a failure")
    if repo_state(root, plan["repos"]) != plan["repos"]:
        return fail("a source checkout changed during the run; source repos are read-only")
    if plan.get("current"):
        status.update(status="no_change", summary="Nothing new since the last update.", freshness="current")
        atomic_json(work / "status.json", status)
        print("status=no_change (already current; map untouched)")
        return status
    top = Path(plan["wiki"])
    map_dir = in_top(agents, top).as_posix() + "/"
    allowed_prompt = None if plan["prompt_existed"] else in_top(agents.parent, top).joinpath(PROMPT).as_posix()
    pending = plan["wiki_pending"]
    outside = [p for p in wiki_changes(top) if not p.startswith(map_dir) and p != allowed_prompt
               and pending.get(p) != file_fingerprint(top / p)]
    if outside:
        return fail("edits outside the map: " + ", ".join(outside[:5]))
    # The source checkouts are proven unchanged above, but the model's edits may cite files that were
    # not evidence at capture time (ignored or generated ones), which changes the source fingerprint.
    # Re-read the source identity with the edited map, keeping the preservation data captured before.
    fresh = work / "snapshot-after.json"
    fresh.unlink(missing_ok=True)
    recapture = run_script("snapshot.py", "capture", agents, "--root", root, "--out", fresh)
    if recapture.returncode:
        return fail("could not re-read the source snapshot: " + recapture.stderr.strip()[:300])
    saved = json.loads((work / "snapshot.json").read_text())
    saved["repos"] = json.loads(fresh.read_text())["repos"]
    atomic_json(work / "snapshot.json", saved)
    finalize = run_script("snapshot.py", "finalize", agents, "--root", root, "--snapshot", work / "snapshot.json")
    if finalize.returncode:
        return fail("finalize refused: " + (finalize.stderr or finalize.stdout).strip()[:400])
    check = run_script("check.py", agents, "--root", root, "--json")
    try:
        report = json.loads(check.stdout)
    except ValueError:
        return fail("check.py produced no report after finalize")
    if report["structure"] != "ok":
        return fail("structure check failed: " + "; ".join(report["errors"][:3]))
    tool_files = {in_top(agents, top).joinpath(name).as_posix() for name in (".state.json", ".state.lock")}
    pages = [p for p in wiki_changes(top) if p.startswith(map_dir) and p not in tool_files]
    status.update(status="updated" if pages else "no_change", pages=pages, freshness=report["freshness"])
    if not status["summary"]:
        status["summary"] = "Map pages updated." if pages else "No map change needed; baseline advanced."
    atomic_json(work / "status.json", status)
    print(f"status={status['status']} pages={len(pages)} freshness={report['freshness']}")
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "conclude"):
        sub = commands.add_parser(name)
        sub.add_argument("agents_dir", type=Path)
        sub.add_argument("--work", type=Path, required=True)
        sub.add_argument("--root", type=Path)
        if name == "prepare":
            sub.add_argument("--full", action="store_true")
    args = parser.parse_args()
    agents = args.agents_dir.absolute()
    root = args.root.absolute() if args.root else Path(workspace_root(str(agents)))
    work = args.work.absolute()
    try:
        for repo_dir in [root / p for p in load_state(str(agents)).get("repos") or {}]:
            if repo_dir == work or repo_dir in work.parents:
                raise ValueError("--work must be outside source repos")
        work.mkdir(parents=True, exist_ok=True)
        if args.command == "prepare":
            prepare(agents, root, work, args.full)
            return 0
        return 1 if conclude(agents, root, work)["status"] == "failed" else 0
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        if work.is_dir():
            atomic_json(work / "status.json", {"status": "failed", "reason": f"{args.command}: {str(exc)[:400]}",
                                               "pages": [], "ranges": {}, "summary": "", "limitations": []})
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
