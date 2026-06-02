---
name: wiki-system
description: Generate, audit, and re-check structured codebase documentation. Use when the user wants to (a) bootstrap documentation for a project that has no or minimal docs, (b) audit existing docs against current source code to find drift or coverage gaps after a development gap, or (c) refresh stale wiki content. Operates entirely on the user's current working directory — auto-discovers target repositories, plans a multi-section wiki, dispatches writer/verifier sub-agents, and produces a wiki/ folder. Four modes: bootstrap (full generation), recheck (audit the existing wiki against code), claude (generate/refresh CLAUDE.md), and notion (publish or audit a Notion mirror).
---

# wiki-system

This skill generates and maintains structured codebase documentation. It runs against whatever project the user is currently in — discovering target repos, planning the wiki structure, dispatching writer and verifier sub-agents, and producing `wiki/` in the user's working directory.

**Skill version.** The canonical version is the single integer in the `VERSION` file beside this `SKILL.md`. Read it at run start; bump it there — and nowhere else — whenever the prompt files change materially. Every orchestrator (`init`, `recheck`, `notion`, `notion recheck`) composes a `generator_version` string — `"wiki-system v<VERSION> · <model-id>"` (with `<VERSION>` the integer read from the file and `<model-id>` the running model — e.g. `wiki-system v9 · claude-opus-4-8`) — and stamps it into the run's artifacts (`meta.generator_version` in `plan.yaml` and `notion-sync.yaml`, plus the per-run header in `decisions.md`). This is what lets a recheck distinguish "the source code drifted" from "this page/mapping was produced by an older skill or model" and decide whether a fuller re-audit is warranted.

## Two roots — read this first

This skill works with two unrelated roots. Confusing them is the most common failure mode.

| Root | What it contains | How to reference |
| --- | --- | --- |
| **Skill files** — this `SKILL.md`, `VERSION`, `init.md`, `recheck.md`, `claude-md.md`, `notion.md`, `notion-recheck.md`, `README.md`, `specialists/`, `spec/` | The prompts and references that drive the orchestration. Live wherever Claude Code installed this skill (typically `.claude/skills/wiki-system/` or `~/.claude/skills/wiki-system/`). | Paths inside this skill (e.g. `specialists/technical.md`) are relative to the prompt file mentioning them. The skill machinery resolves them. |
| **Project files** — `wiki/`, `wiki/.internal/plan.yaml`, target repos like `api/`/`client/`, the user's `CLAUDE.md`, source code under `scope_files` | The user's actual project. Lives at whatever directory the user invoked Claude Code from. | Paths are relative to the user's **current working directory** — never to this skill. |

When this skill or any of its sub-prompts says "read `specialists/technical.md`", that's a skill file. When it says "scan `api/src/`" or "write `wiki/.internal/plan.yaml`", those are project files relative to CWD.

## Pre-flight check (always run first)

Before picking a mode, verify the working environment:

1. Run `pwd` to confirm CWD.
2. Run `ls -la` and confirm the directory looks like a project root — i.e., it contains code or repos, not just unrelated files. If the directory is `~`, `/`, or otherwise wrong, halt and ask the user where the project lives.
3. Note whether `wiki/.internal/plan.yaml` already exists. This drives the mode choice below.

## Invocations at a glance

Six invocations across four modes. **Four write local artifacts (`wiki/` and `CLAUDE.md`); two drive the Notion mirror.** The verification ground truth is always the **source code** — `recheck` checks the local files against it, `notion recheck` checks the *published Notion pages* against it; the push, `claude`, and `notion claude` commands verify nothing.

| Command | Reads | What it does (exactly) | When to use |
| --- | --- | --- | --- |
| `/wiki-system init` | `init.md` | **Bootstrap the local wiki from scratch.** Scans every target repo (parallel per-repo sub-agents) → confirms the track set (`ai` + `product` by default; `technical` opt-in) → writes `plan.yaml` → stubs pages → dispatches writers for the enabled tracks → dispatches verifiers (auto-fix `fail_soft` once) → finalizes `wiki/index.md`. Does **not** write `CLAUDE.md` — it suggests `/wiki-system claude` at the end. | No wiki exists yet, or you want a forced full rebuild after a major architectural change. |
| `/wiki-system recheck` | `recheck.md` | **Audit the existing LOCAL wiki against current code.** Loads the trusted `plan.yaml` (does not re-plan), scans for undocumented source (coverage gaps, human checkpoint), verify-first on every page, regenerates only what drifted (one retry), refreshes root artifacts if structure changed. Does **not** write `CLAUDE.md`. | Periodic local audit — "haven't pushed in weeks", before a demo, after a development gap. |
| `/wiki-system claude` | `claude-md.md` | **Create or update the project-root `CLAUDE.md`** to a lean, ≤200-line agent-context file (product description, layout, conventions, build/run/test, a short on-request docs pointer). Synthesizes from the existing wiki / repo metadata; light scan only if no wiki exists. The **only** command that writes `CLAUDE.md`. | After `init`/`recheck`, or whenever the project's identity, layout, conventions, or commands changed and `CLAUDE.md` should catch up. |
| `/wiki-system notion sync [<root-url>]` | `notion.md` | **Publish to Notion — first time *and* every update (one verb).** With **no mapping**: under your root page, builds root body = `index.md`, a `Library` page holding the `wiki/library/` tree, and a one-time human-owned `Notes` placeholder; writes the `notion-sync.yaml` mapping. With a **mapping**: re-renders and pushes only the pages whose content changed, in place (no duplicates). Trusts local hashes; never reads the Notion side or the code. | To first mirror the wiki to Notion (pass the root URL), and to push later edits. Needs the **Notion MCP** connected. |
| `/wiki-system notion recheck` | `notion-recheck.md` | **Audit the PUBLISHED Notion content against the code.** Fetches each live Notion page and verifies it against its `scope_files`; regenerates drifted pages from code into **both** Notion and local; reconciles structure (missing/orphan/moved/renamed); rebuilds the mapping from Notion if it's lost. `Notes` is never touched. | Confirm the published docs are still accurate — after code changes, after someone edited Notion directly, or from a fresh checkout. Needs the Notion MCP and `plan.yaml`. |
| `/wiki-system notion claude` | `claude-md.md` | **Same as `claude`, but the `CLAUDE.md` Documentation section links to the published Notion pages** instead of local files. Resolves the handful of entry-point URLs from `notion-sync.yaml` (canonical URLs via the Notion MCP; no crawl). Writes a **local** `CLAUDE.md`. Requires an existing mapping — halts and suggests `notion sync` if none. | When the team's doc home is Notion and you want `CLAUDE.md` to point there. |

Mental model: **`init` / `recheck`** = create / audit the local wiki. **`claude` / `notion claude`** = (re)generate `CLAUDE.md` from the wiki/repo, with local- or Notion-linked pointers. **`notion sync`** = push local → Notion (first publish + updates). **`notion recheck`** = audit Notion → against the code. The detailed routing for each mode is below.

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

### Mode 3 — Notion (`notion.md` / `notion-recheck.md`)

Use when the user wants to **publish the existing `wiki/library/` tree to
Notion**, or push subsequent edits to that published mirror. This is a
one-directional sync (disk → Notion); it does not generate, verify, or alter
source content.

Two invocations:
- `/wiki-system notion sync [<root-page-url>]` (→ `notion.md`) — publish. **One verb
  for both the first publish and every update:** with no mapping it creates the
  mirror under the supplied root page and writes the mapping; with a mapping it
  pushes only changed pages in place (no duplicates). Pass the root URL the first
  time (or you'll be asked).
- `/wiki-system notion recheck` (→ `notion-recheck.md`) — audit: verify the **live
  Notion content against the source code** (the same ground truth as local
  `recheck`), regenerate drifted pages from code into both Notion and local, and
  reconcile structure (missing / orphan / moved / renamed). Rebuilds the mapping
  from Notion if it's missing. `Notes` is never touched.

> **Routing note.** Any request naming Notion is Mode 3, even when it says
> "init"/"bootstrap"/"set up" (those map to `notion sync` — there is no separate
> Notion "init" verb). Only route to Mode 1 when Notion is **not** mentioned.
> **One exception:** `notion claude` routes to **Mode 4** (`claude-md.md`), not the
> Notion publish/audit orchestrators — it generates `CLAUDE.md` with Notion-linked
> pointers.

Trigger signals:
- The user said "sync to Notion", "publish the wiki to Notion", "push the docs
  to Notion", "mirror `wiki/library/` to Notion", "init Notion", "set up the
  Notion mirror", or similar
- The user mentioned a Notion root/destination page
- For `recheck` specifically: "is the published Notion still accurate", "audit
  Notion against the code", "did Notion drift from the code", "someone edited
  Notion directly", or re-establishing the link from a fresh checkout / after
  losing `notion-sync.yaml`

Requirements (checked by `notion.md` in its preflight, not here):
- The **Notion MCP** must be connected — this command drives Notion entirely
  through the `notion-*` MCP tools. No token/REST fallback.
- A destination root page (captured on first run and persisted to
  `wiki/.internal/notion-sync.yaml`; reused automatically thereafter).

What it does — builds this shape under the root page:
- **Root page body** = `wiki/index.md` (overview only).
- **`Library`** child page (body = `wiki/library/index.md`) holding the
  `wiki/library/` tree: folders-with-`index.md` become pages whose children
  are their sub-pages; leaf `.md` files become childless pages.
- **`Notes`** child page — a one-time placeholder for humans to edit directly
  in Notion. Created once and **never overwritten**; does NOT mirror
  `wiki/notes/` on disk.
- Icons only on pages that have children (so `Library` yes, `Notes`
  no). Two-pass: create pages to learn their ids, then rewrite cross-links into
  Notion page links.
- Idempotent and resumable via the persisted mapping — re-runs update changed
  pages in place rather than duplicating the tree.

`notion recheck` (`notion-recheck.md`) is the audit companion: where `sync`
pushes disk → Notion trusting local hashes, `recheck` fetches the **live Notion
content and verifies it against the source code** (the same ground truth as local
`recheck`). Pages whose published content drifted from the code — because the code
changed, a human edited Notion, or stale local was synced — are regenerated from
code and corrected in **both** Notion and local. It also reconciles structure and
can rebuild the mapping from Notion on a fresh checkout. The human-owned `Notes`
page is never touched.

**To execute Mode 3:** read `notion.md` for `sync`, or `notion-recheck.md`
for `recheck`, and follow its phases end-to-end.

### Mode 4 — CLAUDE.md (`claude-md.md`)

Use when the user wants to **create or update the project-root `CLAUDE.md`** — the
agent-context file. This is the **only** mode that writes `CLAUDE.md`; `init`,
`recheck`, and the Notion modes never touch it.

Trigger signals:
- The user said "update CLAUDE.md", "regenerate CLAUDE.md", "fix up the project
  memory / agent-context file", or ran `/wiki-system claude`
- The user ran `/wiki-system notion claude` (or asked for a `CLAUDE.md` that links to
  the Notion pages) → the **Notion variant**
- Just finished an `init`/`recheck` and wants `CLAUDE.md` brought in line
- The project's identity, layout, conventions, or commands changed

What it does: synthesizes a lean (≤200-line) `CLAUDE.md` from the cheapest sufficient
source — the existing `CLAUDE.md`, the wiki (`wiki/index.md` + `plan.yaml`), and repo
metadata — doing a light structural scan only if no wiki exists. It bakes in the
**on-request docs policy** (the wiki and `CLAUDE.md` are refreshed only when explicitly
asked, never as a side effect of feature work) and confirms before overwriting an
existing file.

**Two invocations:** `/wiki-system claude` links the Documentation section to the local
`wiki/` files; `/wiki-system notion claude` links it to the **published Notion pages**
(URLs resolved from `notion-sync.yaml` via the Notion MCP — requires an existing mapping,
else it halts and suggests `notion sync`). Both write a local `CLAUDE.md`.

Cost: low — no writer/verifier sub-agents; one orchestrator pass.

**To execute Mode 4:** read `claude-md.md` and follow its phases end-to-end (use its
§ NOTION VARIANT branch for `notion claude`).

### When the request is ambiguous

If the user's intent is unclear (e.g. "update the docs"), ask exactly one question:

> Does `wiki/.internal/plan.yaml` exist in this directory, and is the wiki roughly current? If yes I'll run **recheck** (cheaper, audits and fixes drift). If no I'll run **bootstrap** (full generation — heavier).

Then route accordingly. Do NOT choose silently.

## What this skill does NOT do

- It does NOT modify source code in target repos. Read-only on `scope_files`.
- It does NOT touch `wiki/notes/` — that folder is always hand-written.
- The generation modes (bootstrap, recheck) do NOT publish to Notion — they only produce/maintain the local `wiki/` tree. Notion is its own mode: **Mode 3** (`notion.md` for `sync`, `notion-recheck.md` for `recheck`), over the Notion MCP.
- It does NOT replace ADRs, design docs, tutorials, or onboarding guides. Those are out of scope by design — see `README.md` § What it solves.

## See also (skill files)

- `README.md` — full system explainer: philosophy, architecture, design decisions, failure modes
- `init.md` — bootstrap orchestrator (read this in Mode 1)
- `recheck.md` — recheck orchestrator (read this in Mode 2)
- `notion.md` — Notion publish orchestrator: `notion sync` (Mode 3)
- `notion-recheck.md` — Notion audit orchestrator (verify published content vs source code): `notion recheck` (Mode 3)
- `specialists/ai.md`, `specialists/technical.md`, `specialists/product.md`, `specialists/verifier.md` — sub-agent prompts dispatched by the orchestrators (one writer specialist per track: `ai` + `product` are default, `technical` is opt-in)
- `spec/plan-schema.md` — authoritative schema for `wiki/.internal/plan.yaml`
- `spec/notion-sync-schema.md` — authoritative schema for `wiki/.internal/notion-sync.yaml` (the Notion mapping)
