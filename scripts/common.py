"""Shared helpers for the wiki-system scripts (stdlib only)."""

import fnmatch
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

SOURCE_EXT = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".astro", ".vue", ".svelte",
    ".py", ".go", ".rs", ".rb", ".php", ".java", ".kt", ".kts", ".swift", ".m", ".mm",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".sql", ".css", ".scss", ".graphql",
    ".prisma", ".toml", ".sh", ".html", ".htm", ".json", ".jsonc", ".yaml", ".yml", ".svg",
}

DOC_EXT = {".md", ".mdx", ".rst", ".txt"}
CONFIG_NAMES = {"Dockerfile", "Makefile", "Justfile", "Procfile", "_headers", ".gitignore",
                ".posthtmlrc", ".postcssrc", ".parcelrc", ".nvmrc", ".node-version"}
MARKER = "<!-- wiki-system: generated from code; refresh with /wiki-system update -->"
KEEP = re.compile(r"<!-- keep -->.*?<!-- /keep -->|<!-- AUTOREGEN_SKIP_BEGIN -->.*?<!-- AUTOREGEN_SKIP_END -->", re.S)
PRESERVE_PAIRS = (("<!-- keep -->", "<!-- /keep -->"),
                  ("<!-- AUTOREGEN_SKIP_BEGIN -->", "<!-- AUTOREGEN_SKIP_END -->"))
LINK = re.compile(r'\]\((<[^>]+>|[^)\s]+)(?:\s+"[^\"]*")?\)')


def local_links(text):
    """Decoded local Markdown destinations shared by validation and dependency discovery."""
    for target in LINK.findall(KEEP.sub("", text)):
        target = target.strip("<>")
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:|^#|^//", target):
            continue
        path = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if path:
            yield LINE_SUFFIX.sub("", path)


def preservation_blocks(text):
    blocks = KEEP.findall(text)
    for start, end in PRESERVE_PAIRS:
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        found = pattern.findall(text)
        if text.count(start) != len(found) or text.count(end) != len(found):
            raise ValueError("unbalanced or nested keep blocks / AUTOREGEN_SKIP blocks")
    for block in blocks:
        if sum(block.count(start) for start, _ in PRESERVE_PAIRS) != 1:
            raise ValueError("nested keep blocks / AUTOREGEN_SKIP blocks")
    return blocks


TICK = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
LINE_SUFFIX = re.compile(r":\d+(?:[-–]\d+)?$")

SKIP_DIRS = {
    "node_modules", "dist", "build", ".expo", ".astro", ".next", ".turbo", ".wrangler",
    "coverage", "vendor", "target", "Pods", "__pycache__", ".git", ".venv", "venv", ".cache", ".pytest_cache", ".mypy_cache", ".ruff_cache",
}

TEST_RE = re.compile(
    r"(^|/)(__tests__|__mocks__|tests?|e2e|\.maestro|fixtures|__snapshots__)/"
    r"|\.(test|spec|stories)\.[^/]+$"
)

GENERATED_RE = re.compile(
    r"\.(generated|gen)\.[^/]+$|(^|/)generated/|\.d\.ts$|(^|/)database\.types\.ts$"
    r"|routeTree\.gen\.ts$"
)

LOCK_NAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "deno.lock", "Cargo.lock",
    "poetry.lock", "Gemfile.lock", "composer.lock", "Podfile.lock", "bun.lockb",
}


def git_files(repo_dir):
    """Tracked plus untracked-not-ignored files, repo-relative. Falls back to a walk."""
    try:
        out = subprocess.run(
            ["git", "-C", repo_dir, "ls-files", "-z", "-co", "--exclude-standard"],
            capture_output=True, text=True, check=True,
        ).stdout
        return sorted(set(p for p in out.split("\0") if p))
    except (subprocess.CalledProcessError, FileNotFoundError):
        files = []
        for root, dirs, names in os.walk(repo_dir):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for name in names:
                files.append(os.path.relpath(os.path.join(root, name), repo_dir))
        return files


def is_source(rel):
    if is_sensitive(rel):
        return False
    parts = rel.split("/")
    if any(p in SKIP_DIRS for p in parts):
        return False
    if os.path.basename(rel) in LOCK_NAMES:
        return False
    if os.path.splitext(rel)[1].lower() not in SOURCE_EXT:
        return False
    if TEST_RE.search(rel) or GENERATED_RE.search(rel):
        return False
    return True


def is_sensitive(rel):
    parts = PurePosixPath(rel).parts
    return any(p.lower() in {"secrets", ".secrets"} or p.startswith(".env") for p in parts)


def is_relevant(rel):
    """Update evidence includes tests/docs/config even when it needs no dedicated page."""
    if is_sensitive(rel) or any(p in SKIP_DIRS for p in PurePosixPath(rel).parts):
        return False
    # Freshness is deliberately extension agnostic. Inventory's source LOC filter
    # is an aid to reading, never a boundary on what can invalidate a map.
    return not bool(GENERATED_RE.search(rel))


def references(page, root):
    if not page.is_file():
        return []
    text = page.read_text()
    tokens = [LINE_SUFFIX.sub("", t) for t in TICK.findall(KEEP.sub("", text)) if safe_relative(t)]
    for token in local_links(text):
        dest = Path(os.path.normpath(page.parent / token))
        try:
            tokens.append(dest.relative_to(root).as_posix())
        except ValueError:
            pass
    return tokens


def referenced(path, tokens):
    return any(path == t or path.startswith(t.rstrip("/") + "/") or match_any(path, [t]) for t in tokens)


def dependency_inputs(state, agents, root):
    """Watches/citations are explicit inputs; ownership only classifies Git inventory."""
    paths = [p for area in state.get("areas", []) for p in area.get("watch", [])]
    for page in state.get("managed_pages", []):
        paths.extend(references(agents / page, root))
    return paths


def extra_dependency_files(root, repo, inputs):
    """Expand explicit ignored dependencies only, pruning private/cache/link paths.

    Walk from each watch/citation's static prefix, never from ownership globs.
    A broad explicit watch is intentionally broad; callers should use narrow inputs.
    """
    repo_dir = root / repo
    found = set()
    for pattern in inputs:
        if repo != ".":
            if not pattern.startswith(repo + "/"):
                continue
            pattern = pattern[len(repo) + 1:]
        if not safe_relative(pattern):
            continue
        parts = PurePosixPath(pattern).parts
        static = []
        for part in parts:
            if any(c in part for c in "*?["):
                break
            static.append(part)
        seed = repo_dir.joinpath(*static)
        if seed.is_symlink() or is_sensitive(pattern):
            continue
        if any(part in SKIP_DIRS for part in static):
            continue
        try:
            seed.resolve().relative_to(repo_dir.resolve())
        except ValueError:
            continue
        if seed.is_file():
            found.add(seed.relative_to(repo_dir).as_posix())
            continue
        if not seed.is_dir():
            continue
        for base, dirs, names in os.walk(seed):
            dirs[:] = [name for name in dirs if name not in SKIP_DIRS
                       and not is_sensitive(name) and not (Path(base) / name).is_symlink()]
            for name in names:
                path = Path(base) / name
                rel = path.relative_to(repo_dir).as_posix()
                if not path.is_symlink() and relevant_evidence(rel, rel, [pattern]) and referenced(rel, [pattern]):
                    found.add(rel)
    return found


def evidence_paths(state, agents, root):
    paths = [p for area in state.get("areas", []) for field in ("paths", "watch") for p in area.get(field, [])]
    paths.extend(dependency_inputs(state, agents, root))
    return paths


def relevant_evidence(rel, shown, explicit):
    # Generated schemas can be explicit contracts. Never override privacy or
    # cache/vendor boundaries, even when an ownership glob is broad.
    if is_sensitive(rel) or any(p in SKIP_DIRS for p in PurePosixPath(rel).parts):
        return False
    return is_relevant(rel) or referenced(shown, explicit)


def loc(path):
    if os.path.islink(path):
        return 0  # Inventory never follows a link outside the source checkout.
    try:
        with open(path, "rb") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def source_files(root, repo):
    """[(display_path, loc)] for one repo. display_path is '<repo>/<rel>' unless repo is '.'."""
    repo_dir = os.path.join(root, repo)
    result = []
    for rel in git_files(repo_dir):
        if not is_source(rel):
            continue
        if not os.path.isfile(os.path.join(repo_dir, rel)):
            continue  # git ls-files includes tracked files deleted from the working tree.
        shown = rel if repo == "." else f"{repo}/{rel}"
        result.append((shown, loc(os.path.join(repo_dir, rel))))
    return result


def load_state(agents_dir):
    path = os.path.join(agents_dir, ".state.json")
    with open(path) as fh:
        return json.load(fh)


def match_any(path, globs):
    return any(fnmatch.fnmatch(path, g) for g in globs)


def workspace_root(agents_dir):
    """<root>/<WIKI>/AGENTS → <root> (multi-repo); <repo>/docs/AGENTS → <repo>."""
    return os.path.dirname(os.path.dirname(os.path.abspath(agents_dir)))


def looks_like_path(token):
    """Recognize documented paths, including root files; leave routes/symbols alone."""
    token = LINE_SUFFIX.sub("", token)
    if not token or token.startswith(("http:", "https:", "/", "<", "$", "@", "#")):
        return False
    if any(c in token for c in "\n{}<>|=()'\""):
        return False
    if re.match(r"(?:node|python[0-9.]*|yarn|npm|pnpm|git|bash|sh|uv|cargo|go|php|npx)\s", token):
        return False
    return (token.endswith("/") or ("*" in token and "/" in token)
            or os.path.splitext(token)[1].lower() in SOURCE_EXT | DOC_EXT | {".svg", ".png", ".webp"}
            or os.path.basename(token) in CONFIG_NAMES | LOCK_NAMES
            or ("/" in token and " " not in token))


def cited_paths(text):
    return sorted({LINE_SUFFIX.sub("", t) for t in TICK.findall(KEEP.sub("", text))
                   if looks_like_path(t)})


def safe_relative(path):
    return isinstance(path, str) and bool(path) and not PurePosixPath(path).is_absolute() and ".." not in PurePosixPath(path).parts and "\\" not in path


def validate_state(state):
    """Validate v3 state; legacy adoption requires an explicit source review."""
    errors = []
    if not isinstance(state, dict):
        return ["state must be an object"]
    if state.get("skill") != "wiki-system" or type(state.get("version")) is not int or state.get("version") != 3:
        errors.append("state must declare skill wiki-system and version 3")
    if "project_rules" in state:
        rules = state["project_rules"]
        if not safe_relative(rules) or is_sensitive(rules) or not rules.endswith(".md"):
            errors.append("project_rules must be a non-sensitive workspace-relative Markdown path")
    repos = state.get("repos")
    excluded = state.get("excluded_repos", [])
    if not isinstance(excluded, list) or not all(safe_relative(p) and p != "." and "/" not in p for p in excluded):
        errors.append("excluded_repos must be a list of immediate repo names")
    if not isinstance(repos, dict) or not repos:
        errors.append("repos must be a nonempty object")
    else:
        if "." in repos and len(repos) != 1:
            errors.append("single-repo '.' cannot be combined with sibling repos")
        for repo, info in repos.items():
            if not safe_relative(repo) or (repo != "." and "/" in repo):
                errors.append(f"invalid immediate repo name: {repo!r}")
            if not isinstance(info, dict):
                errors.append(f"repo {repo}: metadata must be an object")
                continue
            if info.get("sha") is not None and not isinstance(info["sha"], str):
                errors.append(f"repo {repo}: sha must be a string or null")
            if "dirty" in info and type(info["dirty"]) is not bool:
                errors.append(f"repo {repo}: dirty must be boolean")
            if "dirty_files" in info and (not isinstance(info["dirty_files"], list) or not all(safe_relative(p) for p in info["dirty_files"])):
                errors.append(f"repo {repo}: dirty_files must contain relative paths")
            if "dirty_hashes" in info:
                hashes = info["dirty_hashes"]
                if not isinstance(hashes, dict) or not all(safe_relative(p) and isinstance(h, str) and (h == "deleted" or re.fullmatch(r"[0-9a-f]{64}", h)) for p, h in hashes.items()):
                    errors.append(f"repo {repo}: dirty_hashes must contain relative paths and SHA-256 hashes or deleted")
    managed = state.get("managed_pages")
    if (not isinstance(managed, list) or not all(safe_relative(p) and p.endswith(".md") and not is_sensitive(p) for p in managed)
            or len(set(managed)) != len(managed) or "index.md" not in managed):
        errors.append("managed_pages must be unique relative Markdown paths including index.md")
        managed = []
    areas = state.get("areas")
    if not isinstance(areas, list):
        errors.append("areas must be a list (may be empty)")
    else:
        ids, pages = set(), set()
        for area in areas:
            if not isinstance(area, dict):
                errors.append("each area must be an object")
                continue
            area_id, page = area.get("id"), area.get("page")
            if not isinstance(area_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", area_id) or area_id in ids:
                errors.append(f"invalid or duplicate area id: {area_id!r}")
            else:
                ids.add(area_id)
            if not safe_relative(page) or not page.endswith(".md") or page in pages:
                errors.append(f"area {area_id}: invalid or duplicate page")
            else:
                pages.add(page)
                if page not in managed:
                    errors.append(f"area {area_id}: page must be listed in managed_pages")
            for field in ("paths", "watch"):
                value = area.get(field, [])
                if not isinstance(value, list) or not all(safe_relative(p) for p in value) or (field == "paths" and not value):
                    errors.append(f"area {area_id}: {field} must contain relative globs")
    unmapped = state.get("unmapped_ok", [])
    if not isinstance(unmapped, list):
        errors.append("unmapped_ok must be a list")
    else:
        for item in unmapped:
            if not isinstance(item, dict) or not safe_relative(item.get("glob")) or not isinstance(item.get("why"), str) or not item["why"].strip():
                errors.append("each unmapped_ok entry needs a relative glob and a reason")
    if "review_summary" in state:
        review = state["review_summary"]
        if (not isinstance(review, dict)
                or not isinstance(review.get("pages"), list)
                or not all(isinstance(p, str) and p in managed for p in review.get("pages", []))
                or not isinstance(review.get("ordinary_area"), (str, type(None)))
                or (review.get("ordinary_area") is not None and review.get("ordinary_area") not in {a.get("id") for a in (areas if isinstance(areas, list) else []) if isinstance(a, dict) and isinstance(a.get("id"), str)})
                or review.get("method") not in ("self", "independent")
                or not isinstance(review.get("limitations"), list)
                or not all(isinstance(item, str) for item in review.get("limitations", []))):
            errors.append("review_summary needs managed pages, ordinary_area (string or null), method self|independent and limitations list")
    return errors
