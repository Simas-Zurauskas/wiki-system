---
name: wiki-system
description: Generate, audit, and re-check structured codebase documentation. Use when the user wants to (a) bootstrap documentation for a project that has no or minimal docs, (b) audit existing docs against current source code to find drift or coverage gaps after a development gap, or (c) refresh stale wiki content. Operates in the user's workspace (CWD) — a folder holding the project's code repos and its docs side by side. Discovers the project's target repositories, plans a multi-section wiki, dispatches writer/verifier sub-agents, and produces a per-project wiki-{project}/ docs repo. Four commands: init (full generation), recheck (audit the existing wiki against code), claude (generate/refresh CLAUDE.md), and notion sync (publish the PRODUCT track to Notion).
---

# wiki-system

This skill generates and maintains structured codebase documentation. It runs in the user's **workspace** (CWD) — the folder holding the project's code repos and its docs — discovering the project's target repos, planning the wiki structure, dispatching writer and verifier sub-agents, and producing the project's `wiki-{project}/` docs repo.

**Skill version.** The canonical version is the single integer in the `VERSION` file beside this `SKILL.md`. Read it at run start; bump it there — and nowhere else — whenever the prompt files change materially. Every orchestrator (`init`, `recheck`, `claude`, `notion sync`) composes a `generator_version` string — `"wiki-system v<VERSION> · <model-id>"` (with `<VERSION>` the integer read from the file and `<model-id>` the running model — e.g. `wiki-system v8 · claude-opus-4-8`) — and stamps it into the run's artifacts (`meta.generator_version` in `plan.yaml` and `notion-sync.yaml`, plus the per-run header in `decisions.md`). This is what lets a recheck distinguish "the source code drifted" from "this page/mapping was produced by an older skill or model" and decide whether a fuller re-audit is warranted.

## Two roots — read this first

This skill works with two unrelated roots. Confusing them is the most common failure mode.

| Root | What it contains | How to reference |
| --- | --- | --- |
| **Skill files** — this `SKILL.md`, `VERSION`, `init.md`, `recheck.md`, `claude-md.md`, `notion.md`, `README.md`, `specialists/`, `spec/` | The prompts and references that drive the orchestration. Live wherever Claude Code installed this skill (typically `.claude/skills/wiki-system/` or `~/.claude/skills/wiki-system/`). | Paths inside this skill (e.g. `specialists/technical.md`) are relative to the prompt file mentioning them. The skill machinery resolves them. |
| **Project files** — the docs root `wiki-{project}/` (= `<WIKI>/`, incl. `.internal/plan.yaml`), the sibling **code repos** (`repo-a/`, `repo-b/`, …), and the developer's local `CLAUDE.md` | The user's **workspace** — the directory Claude Code was invoked from. | Paths are relative to CWD (the workspace); `wiki/` in prompts means the resolved `<WIKI>/`. Never relative to this skill. |

When this skill or any of its sub-prompts says "read `specialists/technical.md`", that's a skill file. When it says "scan `api/src/`" or "write `wiki/.internal/plan.yaml`", those are project files relative to CWD.

## Pre-flight check (always run first)

Before picking a mode, establish the workspace and resolve the docs root.

1. Run `pwd` and `ls -la`. **CWD is the workspace** — the folder the user opened Claude Code in. It holds, as siblings: the project's docs folder `wiki-{project}/`, one or more **code repos** (each its own git repo, e.g. `repo-a/`, `repo-b/`), and the developer's local `CLAUDE.md`. **The workspace itself is normally NOT a git repo — that is expected, not an error.** Halt only if CWD is clearly wrong (`~`, `/`, or a folder with no code repos and no `wiki-*` folder) and ask where the project's workspace is.

2. **Resolve the docs root.** Find the project's docs folder: the `wiki-*/` directory in CWD that contains a `.internal/plan.yaml` marker. Call it `<WIKI>` (it is `wiki-{project}`, e.g. `wiki-acme`).
   - **Exactly one found** → that is the docs root; use it.
   - **None found** → no wiki has been built yet. Only `init` proceeds (it creates `wiki-{project}/` — see `init.md`); any other command halts and suggests `init`.
   - **Several found** → ask the user which project this run is for.

   **Throughout this skill and its sub-prompts, `wiki/` is shorthand for the resolved `<WIKI>/` folder** — e.g. `wiki/.internal/plan.yaml` means `<WIKI>/.internal/plan.yaml`, `wiki/AI` means `<WIKI>/AI`. The skill writes docs only inside `<WIKI>/`, never at the workspace root and never inside a code repo.

3. Note whether `<WIKI>/.internal/plan.yaml` exists — this drives the mode choice below.

## Invocations at a glance

Four commands. **`init`/`recheck`/`claude` write local artifacts (`wiki/` and `CLAUDE.md`); `notion sync` drives the Notion mirror.** The verification ground truth is always the **source code** — `recheck` checks local files against code; `notion sync` and `claude` verify nothing.

| Command | Reads | What it does (exactly) | When to use |
| --- | --- | --- | --- |
| `/wiki-system init` | `init.md` | **Bootstrap the local wiki from scratch.** Scans every target repo (parallel per-repo sub-agents) → confirms the track set (`AI` always on + `PRODUCT` by default; `TECHNICAL` opt-in) → writes `plan.yaml` → stubs pages → dispatches writers for the enabled tracks → dispatches verifiers (auto-fix `fail_soft` once) → finalizes `wiki/index.md`. Does **not** write `CLAUDE.md` — it suggests `/wiki-system claude` at the end. | No wiki exists yet, or you want a forced full rebuild after a major architectural change. |
| `/wiki-system recheck` | `recheck.md` | **Audit the existing LOCAL wiki against current code.** Loads the trusted `plan.yaml` (does not re-plan), scans for undocumented source (coverage gaps, human checkpoint), verify-first on every page, regenerates only what drifted (one retry), refreshes root artifacts if structure changed. Tolerates **partial access** — code repos absent from the workspace are skipped and their pages left as-is (the committed wiki is the source of truth for them). Does **not** write `CLAUDE.md`. | Periodic local audit — "haven't pushed in weeks", before a demo, after a development gap. |
| `/wiki-system claude` | `claude-md.md` | **Create or update the workspace `CLAUDE.md`** (individual per developer, not committed) to a lean, ≤200-line agent-context file (product description, layout, conventions, build/run/test, a short on-request docs pointer). Points the Documentation section at `wiki/AI`. Synthesizes from the existing wiki / repo metadata; light scan only if no wiki exists. The **only** command that writes `CLAUDE.md`. | After `init`/`recheck`, or whenever the project's identity, layout, conventions, or commands changed and `CLAUDE.md` should catch up. |
| `/wiki-system notion sync [<root-url>]` | `notion.md` | **Publish the PRODUCT track to Notion — first time *and* every update (one verb).** With **no mapping**: under your root page, mirrors the `wiki/PRODUCT/` tree in place and writes the `notion-sync.yaml` mapping. With a **mapping**: re-renders and pushes only the PRODUCT pages whose content changed, in place (no duplicates). Trusts local hashes; never reads the Notion side or the code. | To first mirror the PRODUCT track to Notion (pass the root URL), and to push later edits. Needs the **Notion MCP** connected. |

Mental model: **`init` / `recheck`** = create / audit the local wiki. **`claude`** = (re)generate `CLAUDE.md` from the wiki/repo, pointing agents at `wiki/AI`. **`notion sync`** = push the local PRODUCT track → Notion (first publish + updates). The detailed routing for each mode is below.

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
- Phase 3e: finalizes `wiki/index.md` (it does **not** write `CLAUDE.md` — it suggests `/wiki-system claude`)

Cost: high — typically 100+ sub-agent dispatches for a mid-sized multi-repo project.

**To execute Mode 1:** read `init.md` and follow its phases end-to-end.

### Mode 2 — Recheck (`recheck.md`)

Use when the user wants to **audit existing documentation** against the current source code, find coverage gaps, or refresh stale content. The plan is trusted — this mode does not re-plan.

Trigger signals:
- `wiki/.internal/plan.yaml` EXISTS in CWD
- The user said "recheck", "audit the wiki", "find documentation gaps", "verify docs against code", "refresh stale docs", or similar
- The user mentioned "I haven't pushed in weeks" / "before a demo" / "weekly health check"

What it does:
- Phase R1: loads existing plan
- Phase R2: scans for source code that has no documentation (coverage-gap detection — `init.md` does not provide this)
- Phase R3: dispatches verifiers against every page in the plan
- Phase R4: dispatches writers to fix verification failures (one auto-fix retry per page, capped)
- Phase R5: refreshes root artifacts only if structure changed

Cost: moderate — ~50 verifier dispatches for a mid-sized project, plus a handful of writer regens for failures.

**To execute Mode 2:** read `recheck.md` and follow its phases end-to-end.

### Mode 3 — Notion (`notion.md`)

Use when the user wants to **publish the PRODUCT track to Notion** — a
one-directional push of the existing local `wiki/PRODUCT/` tree (disk → Notion).
A single invocation:

- `/wiki-system notion sync [<root-page-url>]` (→ `notion.md`) — publish. **One verb
  for both the first publish and every update:** with no mapping it creates the
  mirror under the supplied root page and writes the mapping; with a mapping it
  pushes only changed PRODUCT pages in place (no duplicates). Pass the root URL the
  first time (or you'll be asked).

> **Routing note.** Requests naming Notion are **Mode 3** (`notion sync` →
> `notion.md`, publish the PRODUCT track). For a bare "set up the Notion docs",
> route here — `notion sync` publishes the local `wiki/PRODUCT/` (build the local
> wiki first with **Mode 1** `init` if none exists). Route to **Mode 1**
> (`init.md`) for a **local** build (`init`, Notion not mentioned).

Trigger signals:
- The user said "sync to Notion", "publish the wiki to Notion", "push the docs
  to Notion", "publish the PRODUCT track to Notion", "set up the Notion mirror",
  or similar
- The user mentioned a Notion root/destination page

Requirements (checked by `notion.md` in its preflight, not here):
- The **Notion MCP** must be connected — this command drives Notion entirely
  through the `notion-*` MCP tools. No token/REST fallback.
- A destination root page (captured on first run and persisted to
  `wiki/.internal/notion-sync.yaml`; reused automatically thereafter).
- An existing local `wiki/PRODUCT/` tree to publish.

What it does — mirrors the PRODUCT track under the root page:
- Mirrors the `wiki/PRODUCT/` tree in place: folders-with-`index.md` become pages
  whose children are their sub-pages; leaf `.md` files become childless pages.
- Icons only on pages that have children. Two-pass: create pages to learn their
  ids, then rewrite cross-links into Notion page links.
- Idempotent and resumable via the persisted mapping — re-runs update changed
  pages in place rather than duplicating the tree.

**To execute Mode 3:** read `notion.md` and follow its phases end-to-end.

### Mode 4 — CLAUDE.md (`claude-md.md`)

Use when the user wants to **create or update the workspace `CLAUDE.md`** — the
agent-context file, **individual per developer and not committed**. This is the **only**
mode that writes `CLAUDE.md`; `init`, `recheck`, and `notion sync` never touch it.

Trigger signals:
- The user said "update CLAUDE.md", "regenerate CLAUDE.md", "fix up the project
  memory / agent-context file", or ran `/wiki-system claude`
- Just finished an `init`/`recheck` and wants `CLAUDE.md` brought in line
- The project's identity, layout, conventions, or commands changed

What it does: synthesizes a lean (≤200-line) `CLAUDE.md` from the cheapest sufficient
source — the existing `CLAUDE.md`, the wiki (`wiki/index.md` + `plan.yaml`), and repo
metadata — doing a light structural scan only if no wiki exists. Its Documentation
section links to `wiki/AI`. It bakes in the **on-request docs policy** (the wiki and
`CLAUDE.md` are refreshed only when explicitly asked, never as a side effect of feature
work) and confirms before overwriting an existing file.

Cost: low — no writer/verifier sub-agents; one orchestrator pass.

**To execute Mode 4:** read `claude-md.md` and follow its phases end-to-end.

### When the request is ambiguous

If the user's intent is unclear (e.g. "update the docs"), ask exactly one question:

> Does `wiki/.internal/plan.yaml` exist in this directory, and is the wiki roughly current? If yes I'll run **recheck** (cheaper, audits and fixes drift). If no I'll run **bootstrap** (full generation — heavier).

Then route accordingly. Do NOT choose silently.

If the user names a removed command, map it: `notion init`/`notion claude` were removed → use `init`/`claude`; `notion recheck` → use `recheck` then `notion sync`.

## What this skill does NOT do

- It does NOT modify source code in target repos. Read-only on `scope_files`.
- It does NOT touch `specs/`, `.claude/`, or config — those are not its concern (`specs/` is stagegate territory).
- The generation modes (bootstrap, recheck) do NOT publish to Notion — they only produce/maintain the local `wiki/` tree. Notion is its own mode: **Mode 3** (`notion.md`, `notion sync`), over the Notion MCP.
- It does NOT replace ADRs, design docs, tutorials, or onboarding guides. Those are out of scope by design — see `README.md` § What it solves.

## See also (skill files)

- `README.md` — full system explainer: philosophy, architecture, design decisions, failure modes
- `init.md` — bootstrap orchestrator (read this in Mode 1)
- `recheck.md` — recheck orchestrator (read this in Mode 2)
- `notion.md` — Notion publish orchestrator (push the local `wiki/PRODUCT/` track to Notion): `notion sync` (Mode 3)
- `specialists/ai.md`, `specialists/technical.md`, `specialists/product.md`, `specialists/verifier.md` — sub-agent prompts dispatched by the orchestrators (one writer specialist per track: `AI` always on + `PRODUCT` default, `TECHNICAL` opt-in)
- `spec/plan-schema.md` — authoritative schema for `wiki/.internal/plan.yaml`
- `spec/notion-sync-schema.md` — authoritative schema for `wiki/.internal/notion-sync.yaml` (the Notion mapping)
