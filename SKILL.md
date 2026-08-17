---
name: wiki-system
description: Generate, audit, and re-check structured codebase documentation. Use when the user wants to (a) bootstrap documentation for a project that has no or minimal docs, (b) audit existing docs against current source code to find drift or coverage gaps after a development gap, or (c) refresh stale wiki content. Operates in the user's workspace (CWD) — a folder holding the project's code repos and its docs side by side. Discovers the project's target repositories, plans a multi-section wiki, dispatches writer/verifier sub-agents, and produces a per-project wiki-{project}/ docs repo. Three commands: init (full generation), recheck (audit the existing wiki against code), and claude (generate/refresh CLAUDE.md).
---

# wiki-system

This skill generates and maintains structured codebase documentation. It runs in the user's **workspace** (CWD) — the folder holding the project's code repos and its docs — discovering the project's target repos, planning the wiki structure, dispatching writer and verifier sub-agents, and producing the project's `wiki-{project}/` docs repo.

**Skill version.** The canonical version is the single integer in the `VERSION` file beside this `SKILL.md`. Read it at run start; bump it there — and nowhere else — whenever the prompt files change materially. Every orchestrator (`init`, `recheck`, `claude`) composes a `generator_version` string — `"wiki-system v<VERSION> · <model-id>"` (with `<VERSION>` the integer read from the file and `<model-id>` the running model — e.g. `wiki-system v8 · claude-opus-4-8`) — and stamps it into the run's artifacts (`meta.generator_version` in `plan.yaml`, plus the per-run header in `decisions.md`). This is what lets a recheck distinguish "the source code drifted" from "this page/mapping was produced by an older skill or model" and decide whether a fuller re-audit is warranted.

## Two roots — read this first

This skill works with two unrelated roots. Confusing them is the most common failure mode.

| Root | What it contains | How to reference |
| --- | --- | --- |
| **Skill files** — this `SKILL.md`, `VERSION`, `init.md`, `recheck.md`, `claude-md.md`, `README.md`, `check-update.sh`, `specialists/`, `spec/` | The prompts and references that drive the orchestration. Live wherever Claude Code installed this skill (typically `.claude/skills/wiki-system/` or `~/.claude/skills/wiki-system/`). | Paths inside this skill (e.g. `specialists/technical.md`) are relative to the prompt file mentioning them. The skill machinery resolves them. |
| **Project files** — the docs root `wiki-{project}/` (= `<WIKI>/`, incl. `.internal/plan.yaml`), the sibling **code repos** (`repo-a/`, `repo-b/`, …), and the developer's local `CLAUDE.md` | The user's **workspace** — the directory Claude Code was invoked from. | Paths are relative to CWD (the workspace); `wiki/` in prompts means the resolved `<WIKI>/`. Never relative to this skill. |

When this skill or any of its sub-prompts says "read `specialists/technical.md`", that's a skill file. When it says "scan `api/src/`" or "write `wiki/.internal/plan.yaml`", those are project files relative to CWD.

## Pre-flight check (always run first)

Before picking a mode, establish the workspace and resolve the docs root.

0. **Skill self-update check (mechanical — do not reason about it).** Run
   `bash <skill-dir>/check-update.sh`, where `<skill-dir>` is the directory
   holding this `SKILL.md`. No output means the skill is current: proceed
   silently. Any output is a pre-formatted banner: relay it to the user
   **verbatim**, then ask whether to continue on the current version or stop
   so they can update first. Do not update the clone yourself, and do not
   inspect git state beyond what the banner says — the script has already
   done all of that.

1. Run `pwd` and `ls -la`. **CWD is the workspace** — the folder the user opened Claude Code in. It holds, as siblings: the project's docs folder `wiki-{project}/`, one or more **code repos** (each its own git repo, e.g. `repo-a/`, `repo-b/`), and the developer's local `CLAUDE.md`. **The workspace itself is normally NOT a git repo — that is expected, not an error.** Halt only if CWD is clearly wrong (`~`, `/`, or a folder with no code repos and no `wiki-*` folder) and ask where the project's workspace is.

2. **Resolve the docs root.** Find the project's docs folder: the `wiki-*/` directory in CWD that contains a `.internal/plan.yaml` marker. Call it `<WIKI>` (it is `wiki-{project}`, e.g. `wiki-acme`).
   - **Exactly one found** → that is the docs root; use it.
   - **None found** → no wiki has been built yet. Only `init` proceeds (it creates `wiki-{project}/` — see `init.md`); any other command halts and suggests `init`.
   - **Several found** → ask the user which project this run is for.

   **Throughout this skill and its sub-prompts, `wiki/` is shorthand for the resolved `<WIKI>/` folder** — e.g. `wiki/.internal/plan.yaml` means `<WIKI>/.internal/plan.yaml`, `wiki/AGENTS` means `<WIKI>/AGENTS`. The skill writes docs only inside `<WIKI>/`, never at the workspace root and never inside a code repo.

3. Note whether `<WIKI>/.internal/plan.yaml` exists — this drives the mode choice below.

## Invocations at a glance

Three commands (`recheck` has a cheap `diff` variant), all writing local artifacts (`wiki/` and `CLAUDE.md`). The verification ground truth is always the **source code** — `recheck` checks local files against code; `claude` verifies nothing.

| Command | Reads | What it does (exactly) | When to use |
| --- | --- | --- | --- |
| `/wiki-system init` | `init.md` | **Bootstrap the local wiki from scratch.** Scans every target repo (parallel per-repo sub-agents) → confirms the track set (`AGENTS` always on; `PRODUCT` and `TECHNICAL` opt-in) → writes `plan.yaml` → stubs pages → dispatches writers for the enabled tracks → dispatches verifiers (auto-fix `fail_soft` once) → finalizes `wiki/README.md` and installs the task workflow prompt (`wiki/TASK-WORKFLOW-PROMPT.md`, placeholder resolved). Does **not** write `CLAUDE.md` — it suggests `/wiki-system claude` at the end. | No wiki exists yet, or you want a forced full rebuild after a major architectural change. |
| `/wiki-system recheck` | `recheck.md` | **Audit the existing LOCAL wiki against current code.** Loads the trusted `plan.yaml` (does not re-plan), scans for undocumented source (coverage gaps, human checkpoint), verify-first on every page, regenerates only what drifted (one retry), refreshes root artifacts if structure changed (the repo manifest in each code-anchored track index — `wiki/AGENTS/index.md`, and `wiki/TECHNICAL/index.md` when enabled; SHAs + dirty flags — refreshes on **every** run, as do the installed `TASK-WORKFLOW-PROMPT.md` and the diff baseline `wiki/.internal/recheck-baseline.yaml`). Tolerates **partial access** — code repos absent from the workspace are skipped and their pages left as-is (the committed wiki is the source of truth for them). Does **not** write `CLAUDE.md`. | Periodic local audit — "haven't pushed in weeks", before a demo, after a development gap. |
| `/wiki-system recheck diff` | `recheck.md` § DIFF MODE | **Variant of recheck: audit only what changed since the last verified SHA.** Diffs each repo against its `recheck-baseline.yaml` entry (working tree, so uncommitted + untracked changes count), verifies only the change-derived page set (scope intersection + anchor pull-in + previously-flagged pages), and scans for gaps only among added/renamed/untracked files — no full-surface enumeration. Same gates, retries, and human checkpoints; falls back to full scope per repo when the baseline is missing or unusable, and refuses outright when the skill/model changed since the last run. Cheap; a cadence tier between full rechecks, not a replacement (it cannot see claims invalidated by distant changes — an advisory nudge recommends a periodic full run). | Frequent, cheap drift checks — after a merge burst, a daily/weekly quick audit between full rechecks. |
| `/wiki-system claude` | `claude-md.md` | **Create or update the workspace `CLAUDE.md`** (individual per developer, not committed) to a lean, ≤200-line agent-context file (product description, layout, conventions, build/run/test, a short on-request docs pointer). Points the Documentation section at `wiki/AGENTS`, and copies the external references from `wiki/LINKS.md` into it verbatim when that optional file exists. Synthesizes from the existing wiki / repo metadata; light scan only if no wiki exists. The **only** command that writes `CLAUDE.md`. | After `init`/`recheck`, or whenever the project's identity, layout, conventions, or commands changed and `CLAUDE.md` should catch up. |

Mental model: **`init` / `recheck`** = create / audit the local wiki. **`claude`** = (re)generate `CLAUDE.md` from the wiki/repo, pointing agents at `wiki/AGENTS`. The detailed routing for each mode is below.

## Optional: external references (`wiki/LINKS.md`)

Some projects keep product context **outside** the codebase — a Notion "Start
Here" page, a Linear project, a Figma file. A project surfaces those to agents by
hand-writing one optional file at the docs root, `<WIKI>/LINKS.md`:

```markdown
# External references

- [Start Here — Acme](https://www.notion.so/…) — product source of truth: positioning, roadmap, open decisions
- [Acme design system](https://figma.com/…) — component specs
```

What the skill does with it:

- **`claude` inlines the entries into `CLAUDE.md`** — each `- [Label](url) — note`
  bullet is copied **verbatim** into the `## Documentation` section
  (`claude-md.md` C1/C2). An agent's first read is `CLAUDE.md`, and it sits
  outside the docs repo, so the entries have to be *in* it: an agent that would
  have to open a second file to discover the Notion page exists will answer
  product questions from code instead. Every bullet, in file order — no cap, no
  summarizing, no reordering.
- **`init`/`recheck` add one pointer line** to `wiki/README.md` and the
  `wiki/AGENTS.md` signpost (`init.md` Phase 3e steps 1–2, `recheck.md` R5.2) —
  a link, not a copy. Those two files sit **beside** `LINKS.md` in the same
  repo, one hop away, and both are deliberately tiny.
- **The skill never fetches these URLs**, in any mode. No content sync, no
  reachability check, no MCP dependency: a target may be private or dead and
  nothing about the run changes. Nothing in the wiki or `CLAUDE.md` is ever
  derived from what is behind a link — verification ground truth stays the
  source code.
- **The skill never writes `LINKS.md`.** It is read-only input: never created,
  edited, or deleted, never a page in the plan, never a verifier's concern,
  never a coverage gap. **Absent = the feature is off** — nothing is emitted or
  asked, beyond a one-line nudge at the end of `claude`.

## Mode selection

### Mode 1 — Bootstrap (`init.md`)

Use when the user wants to generate documentation **from scratch** for a project that has none or wants a forced full rebuild.

Trigger signals:
- `wiki/.internal/plan.yaml` does NOT exist in CWD
- The user said "create docs", "bootstrap", "generate the wiki", "document this project from scratch", or similar
- The user asked for a full rebuild after a major architectural change

What it does:
- Phase 1: scans target repos
- Phase 2: plans the wiki structure (writes `wiki/.internal/plan.yaml`)
- Phase 3: dispatches writer and verifier sub-agents in parallel waves
- Phase 3e: finalizes `wiki/README.md` and writes the repo manifest (§ Repositories in each code-anchored track index — `wiki/AGENTS/index.md`, and `wiki/TECHNICAL/index.md` when enabled, never PRODUCT — git URL + verified SHA + dirty flag per repo) and the root agent signposts (docs-root `AGENTS.md` + one-line `CLAUDE.md` pointer; it does **not** write the workspace `CLAUDE.md` — it suggests `/wiki-system claude`), and installs the task workflow prompt (`wiki/TASK-WORKFLOW-PROMPT.md` with `wiki-{workspace-name}` resolved to the actual docs folder name)

Cost: high — typically 100+ sub-agent dispatches for a mid-sized multi-repo project.

**To execute Mode 1:** read `init.md` and follow its phases end-to-end.

### Mode 2 — Recheck (`recheck.md`)

Use when the user wants to **audit existing documentation** against the current source code, find coverage gaps, or refresh stale content. The plan is trusted — this mode does not re-plan.

Trigger signals:
- `wiki/.internal/plan.yaml` EXISTS in CWD
- The user said "recheck", "audit the wiki", "find documentation gaps", "verify docs against code", "refresh stale docs", or similar
- The user mentioned "I haven't pushed in weeks" / "before a demo" / "weekly health check"
- **Diff variant** (`/wiki-system recheck diff`): the user said "quick drift check", "what changed since the last recheck", "diff recheck", "cheap recheck", or wants a frequent check between full audits

What it does:
- Phase R1: loads existing plan (diff variant: plus the per-repo baseline `wiki/.internal/recheck-baseline.yaml`)
- Phase R2: scans for source code that has no documentation (coverage-gap detection — `init.md` does not provide this; diff variant: candidates come from the git change set, no enumeration agents)
- Phase R3: dispatches verifiers against every page in the plan (diff variant: only against the change-derived verify set — see `recheck.md` § DIFF MODE)
- Phase R4: dispatches writers to fix verification failures (one auto-fix retry per page, capped)
- Phase R5: refreshes root artifacts only if structure changed; the repo manifest in each code-anchored track index, the docs-root `AGENTS.md`/`CLAUDE.md` signposts, the installed `TASK-WORKFLOW-PROMPT.md`, and the diff baseline refresh every run

Cost: moderate — ~50 verifier dispatches for a mid-sized project, plus a handful of writer regens for failures. The diff variant is cheap on a quiet week — often < 5 verifiers and zero enumeration agents; it falls back to full scope per repo when its baseline is unusable, and refuses to run (recommending full) when the skill/model changed since the last run.

**To execute Mode 2:** read `recheck.md` and follow its phases end-to-end (the diff variant sets `diff_mode: true` per its CONFIGURATION and § DIFF MODE).

### Mode 3 — CLAUDE.md (`claude-md.md`)

Use when the user wants to **create or update the workspace `CLAUDE.md`** — the
agent-context file, **individual per developer and not committed**. This is the **only**
mode that writes `CLAUDE.md`; `init` and `recheck` never touch it.

Trigger signals:
- The user said "update CLAUDE.md", "regenerate CLAUDE.md", "fix up the project
  memory / agent-context file", or ran `/wiki-system claude`
- Just finished an `init`/`recheck` and wants `CLAUDE.md` brought in line
- The project's identity, layout, conventions, or commands changed

What it does: synthesizes a lean (≤200-line) `CLAUDE.md` from the cheapest sufficient
source — the existing `CLAUDE.md`, the wiki (`wiki/README.md` + `plan.yaml`), and repo
metadata — doing a light structural scan only if no wiki exists. Its Documentation
section links to `wiki/AGENTS`. It bakes in the **on-request docs policy** (the wiki and
`CLAUDE.md` are refreshed only when explicitly asked, never as a side effect of feature
work) and confirms before overwriting an existing file.

Cost: low — no writer/verifier sub-agents; one orchestrator pass.

**To execute Mode 3:** read `claude-md.md` and follow its phases end-to-end.

### When the request is ambiguous

If the user's intent is unclear (e.g. "update the docs"), ask exactly one question:

> Does `wiki/.internal/plan.yaml` exist in this directory, and is the wiki roughly current? If yes I'll run **recheck** (cheaper, audits and fixes drift). If no I'll run **bootstrap** (full generation — heavier).

Then route accordingly. Do NOT choose silently.

If the user names a removed command: Notion publishing (`notion sync` and the older `notion init`/`notion claude`/`notion recheck`) was removed entirely in v11 — explain briefly that the skill no longer publishes to Notion and the local `wiki/` tree is the only output; route any remaining intent to `init`/`recheck`/`claude`.

## What this skill does NOT do

- It does NOT modify source code in target repos. Read-only on `scope_files`.
- It does NOT touch `specs/`, `.claude/`, or config — those are not its concern (`specs/` is stagegate territory).
- It does NOT touch user content inside the docs root. The skill's surface inside `<WIKI>/` is exactly: the enabled track folders (`AGENTS/`, plus `TECHNICAL/`/`PRODUCT/` when enabled), the docs-root `README.md` (the generated human front door — wikis generated before v12 used `index.md` for this; it is migrated to `README.md` on the next `init`/`recheck` run), the root signposts `AGENTS.md` + `CLAUDE.md`, the installed `TASK-WORKFLOW-PROMPT.md` (a paste-ready larger-task prompt with the `wiki-{workspace-name}` placeholder resolved to the actual docs folder name; refreshed every run unless the project takes ownership by deleting its install-header line — see `init.md` Phase 3e step 2), and `.internal/`. Anything else at the docs root — task workspaces (`tasks/`, `notes/`), audit/research folders, any file or folder the skill did not generate — is **user territory**: never written, never deleted, never read into the documentation-state classification, never walked by the link-graph/orphan gates, and never mentioned in generated files. Two deliberate exceptions, both narrow: the installed `TASK-WORKFLOW-PROMPT.md` names `tasks/`, because directing task work into that user-owned folder is its purpose; and the optional hand-written `LINKS.md` (§ Optional: external references) is **read** — never written — its entries copied into `CLAUDE.md` and its path linked from `README.md`/`AGENTS.md` when it exists, because a pointer nobody can find is worthless. Users may create docs-root files and folders freely without registering them anywhere. The content specs for `README.md` and the root signposts are **exhaustive** — orchestrators must not append sections or lines beyond them; a user who wants a pointer to their own folders puts it inside an `AUTOREGEN_SKIP` block in `README.md`. One safeguard: a docs-root `README.md` whose first line is NOT the generated-header is a hand-written user file — never overwrite it silently; surface the conflict and let the user decide (see the migration note in `init.md` Phase 3e / `recheck.md` R5.2).
- It does NOT publish anywhere external. The local `wiki/` tree is the only output (Notion publishing existed through v10 and was removed in v11).
- It does NOT replace ADRs, design docs, tutorials, or onboarding guides. Those are out of scope by design — see `README.md` § What it solves.

## See also (skill files)

- `README.md` — full system explainer: philosophy, architecture, design decisions, failure modes
- `init.md` — bootstrap orchestrator (read this in Mode 1)
- `recheck.md` — recheck orchestrator (read this in Mode 2)
- `claude-md.md` — `CLAUDE.md` orchestrator (read this in Mode 3)
- `specialists/agents.md`, `specialists/technical.md`, `specialists/product.md`, `specialists/verifier.md` — sub-agent prompts dispatched by the orchestrators (one writer specialist per track: `AGENTS` always on; `PRODUCT` and `TECHNICAL` opt-in)
- `spec/plan-schema.md` — authoritative schema for `wiki/.internal/plan.yaml`
