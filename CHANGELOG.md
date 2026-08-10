# Changelog

One entry per `VERSION` bump, newest first. **Update this file in the same
commit that bumps `VERSION`** — the `generator_version` recorded in each
project's `plan.yaml` only tells a recheck *that* the generator drifted; this
file is what tells the operator *what* changed between those versions.

Introduced at v10; earlier versions are not chronicled here (see git history).

## v12 — 2026-08-10

**The docs-root front door is now `README.md`, not `index.md`.**

- The orchestrator-generated human front door / table of contents at the docs
  root is renamed `wiki/index.md` → `wiki/README.md`, so repo hosts (GitHub
  etc.) render it automatically when the wiki repo is browsed or pushed.
  Content spec, generated-header, `AUTOREGEN_SKIP` hand-edit zones, and the
  exhaustive-content rule are unchanged — only the filename moved. Renamed in
  every prompt: `SKILL.md`, `init.md` (Phase 3e step 1, tree, ownership table,
  gates, constraints), `recheck.md` (R5.2), `claude-md.md` (C0/C1 sources +
  the generated Documentation-section template now links `wiki/README.md`),
  `spec/plan-schema.md`, and all four specialists (the "never touch the wiki
  root" constraint; while there, the stale "hand-written" description of the
  root file in `product.md`/`technical.md` was corrected to
  "orchestrator-generated").
- **`README.md` consequently leaves user territory.** The v11 user-territory
  guarantee now names task workspaces and audit/research folders as examples;
  a user pointer at the root belongs inside an `AUTOREGEN_SKIP` block in
  `README.md`. Safeguard: a docs-root `README.md` whose first line is not the
  generated-header is a hand-written user file — runs must not overwrite it
  silently; the migration note has them halt and ask (default: wrap the user's
  content in an `AUTOREGEN_SKIP` block inside the generated file).
- **Migration for pre-v12 wikis** (`init.md` Phase 3e step 1; `recheck.md`
  R5.2, exempt from the zero-structural-changes skip): write `README.md`
  carrying over `AUTOREGEN_SKIP` blocks, delete the old docs-root `index.md`,
  refresh the `AGENTS.md` signpost's "humans start at" line (now
  `README.md`).

## v11 — 2026-08-07

**User-owned docs-root content is explicitly out of bounds; Notion publishing removed.**

- **BREAKING: Notion support dropped entirely.** `notion.md` and
  `spec/notion-sync-schema.md` deleted; the `notion sync` command (Mode 3) and
  every Notion reference removed from `SKILL.md`, `README.md`, `init.md`,
  `claude-md.md`, and the three writer specialists. The skill now has three
  commands (`init`, `recheck`, `claude`) and produces only the local `wiki/`
  tree — it publishes nowhere external. The former Mode 4 (`claude`) is now
  Mode 3. An existing `wiki/.internal/notion-sync.yaml` in a project is inert
  and can be deleted by its owner. Requests naming Notion get a brief "removed
  in v11" explanation instead of routing.
- `spec/comment-standard.moved.md` deleted. It was a tombstone pointing at an
  `eng-rulebook` skill that is not part of this repo and does not exist in most
  workspaces; nothing in the live prompts referenced it (the standard's content
  left this repo at v9).

- The docs root may contain user-created files and folders the skill did not
  generate — task workspaces (`tasks/`, `notes/`), audit/research folders, a
  hand-written `README.md`. These were already unmanaged in practice; the spec
  now guarantees it everywhere the wiki tree is read or walked: never written
  or deleted, never read into the Phase 1 documentation-state classification
  (the phase that historically deleted a pre-existing docs-root `README.md` as
  "outdated"), never walked by the link-graph/orphan checks (Phase 3e step 3
  **and** § QUALITY GATES — the latter is what recheck R5.1 executes), and
  never mentioned in generated files. New bullet in `SKILL.md` § What this
  skill does NOT do; matching constraint extension in `recheck.md`
  § CONSTRAINTS ("never reads, walks, or mentions").
- The content specs for `wiki/index.md` (Phase 3e step 1) and the root
  signposts `wiki/AGENTS.md` + `wiki/CLAUDE.md` (Phase 3e step 2) are declared
  **exhaustive** — orchestrators must not append extra sections or lines (past
  runs freelanced a `## Notes` section into index.md and a `notes/` line into
  AGENTS.md; both were spec-unprotected and could silently vanish on any run).
  A user pointer belongs in the user-owned `README.md` or an `AUTOREGEN_SKIP`
  block in `index.md` (AGENTS.md has no skip mechanism by design).
- Orphan-check exemptions now include the root signposts (found by filename
  convention, legitimately inbound-linkless) in both Phase 3e step 3 and the
  quality gate.
- **New `check-update.sh` + pre-flight step 0: mechanical self-update check.**
  Every invocation starts by running the script; the orchestrator only relays
  its output verbatim — zero git reasoning in the prompts. The script is
  silent unless the skill clone is behind its origin, in which case it prints
  a pre-formatted banner (local vs remote `VERSION` + SHAs, commits behind,
  and the right next step: `git pull --ff-only` for a clean clone, "reconcile
  manually" when the clone is dirty or has unpushed commits). Engineering
  properties: fetch is TTL-cached at 24h via a stamp inside `.git/` (never
  dirties the tree; stamp touched only on successful fetch so failures retry),
  fully non-interactive (`GIT_TERMINAL_PROMPT=0`, SSH BatchMode, bounded HTTP
  transfer), always exits 0, and offline runs still compare against the
  last-fetched remote state. Tradeoff: a push to origin may go unnoticed for
  up to 24h.

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
