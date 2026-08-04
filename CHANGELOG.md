# Changelog

One entry per `VERSION` bump, newest first. **Update this file in the same
commit that bumps `VERSION`** — the `generator_version` recorded in each
project's `plan.yaml` only tells a recheck *that* the generator drifted; this
file is what tells the operator *what* changed between those versions.

Introduced at v10; earlier versions are not chronicled here (see git history).

## v10 — 2026-08-04

**Repo manifest in every code-anchored track index; track `ai` renamed `agents`.**

- New orchestrator-owned `## Repositories` section written into the index of
  **each enabled code-anchored track** — `wiki/AGENTS/index.md` always, and
  `wiki/TECHNICAL/index.md` when the technical track is enabled; **never
  PRODUCT** (its pages must contain zero code references and it publishes to
  Notion for non-technical readers). Written at `init` finalize (Phase 3e
  step 2) and refreshed on **every** `recheck` (R5.2) — including runs with no
  structural changes, so the SHAs never lag the verification they claim. Per
  repo: the anchor prefix, git remote URL, default branch, the commit SHA the
  pages were verified against, a working-tree-dirty flag, and the verification
  date; closed by a fixed anchor-resolution note. This is what lets a reader
  outside the workspace (MCP, retriever, another agent) resolve
  `<repo>/<path>:<line>` anchors to real repositories. Each track index
  carries its own copy (a track is the unit of standalone consumption); copies
  cannot drift because one finalize step rewrites all of them from the same
  `meta.repos` data every run.
- **Track rename: `ai` → `agents`** (folder `wiki/AI/` → `wiki/AGENTS/`).
  "AI" was ambiguous — it reads as "docs about the product's AI features"
  rather than "docs for AI agents". The track is named by audience, like the
  others, and `AGENTS` rides the `AGENTS.md` ecosystem convention. Renamed
  consistently: track id in `meta.tracks`/`owner_agent`/verifier `mode`, the
  folder literal in the plan INVARIANTS, `specialists/ai.md` →
  `specialists/agents.md`, track-index H1 `# AI` → `# AGENTS`. Genuine
  artificial-intelligence prose ("AI/LLM agents" as the audience) unchanged.
- Plan schema 1.4 → **1.5** — **BREAKING** (folder literal changed): existing
  wikis migrate mechanically, no content regeneration — `git mv wiki/AI
  wiki/AGENTS` (or from the pre-1.4 layout), rewrite plan paths,
  `tracks: [ai]` → `[agents]`, `owner_agent: ai` → `agents`, bump
  `schema_version` to `"1.5"`, fix root-file links. `meta.repos[]` gains
  optional `git_url` + `default_branch`, captured at `init` discovery via
  `git remote get-url origin` — recorded as `null` when there is no remote,
  never guessed; `recheck` R1 backfills both for *present* repos on pre-1.5
  plans.
- Writer guard (`specialists/agents.md`, `specialists/technical.md`):
  `## Repositories` is orchestrator-owned — preserved verbatim, in place, when
  a writer regenerates its track index; never authored, edited, or deleted by
  a writer.
- **Root agent signposts**: `init`/`recheck` finalize now also writes
  `wiki/AGENTS.md` (≤15-line signpost: start at `AGENTS/index.md`, read
  invariants first, resolve anchors via the § Repositories manifest) and
  `wiki/CLAUDE.md` ("See AGENTS.md.") at the **docs root**, rewritten
  wholesale every run — so an agent reading the docs repo itself (MCP, clone,
  retriever) finds the front door. Distinct from the workspace `CLAUDE.md`,
  which stays owned by `/wiki-system claude`.

## v9 — 2026-08-03 (`a9a4f0a`)

**`ai` becomes the only default track.**

- Default track set is now `[ai]`; `product` joins `technical` as opt-in
  (previously `product` was on by default). `ai` remains always-on.
- `spec/comment-standard.md` tombstoned (`comment-standard.moved.md`).
