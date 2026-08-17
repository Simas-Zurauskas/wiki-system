# Changelog

One entry per `VERSION` bump, newest first. **Update this file in the same
commit that bumps `VERSION`** — the `generator_version` recorded in each
project's `plan.yaml` only tells a recheck *that* the generator drifted; this
file is what tells the operator *what* changed between those versions.

Introduced at v10; earlier versions are not chronicled here (see git history).

## v15 — 2026-08-17

**Optional `wiki/LINKS.md` — a pointer to product context that lives outside
the codebase** (a Notion "Start Here" page, a Linear project, a Figma file).

- **One optional, hand-written, user-owned file at the docs root**
  (`SKILL.md` § Optional: external references), holding
  `- [Label](url) — note` entries. Read-only input: the skill never creates,
  edits, or deletes it, and **never fetches the URLs** it names, in any mode.
- **`claude` copies the entries verbatim into `CLAUDE.md`** — an
  `**External references**` block in the `## Documentation` section
  (`claude-md.md` C1 step 5 / C2), every entry in file order, no cap. They are
  inlined rather than linked because `CLAUDE.md` is an agent's first read and
  lives outside the docs repo: an agent that must open a second file to
  discover the Notion page exists will answer product questions from code
  instead. The block is regenerated from `LINKS.md`, never merged with the
  previous file's — so a link added only to `CLAUDE.md` (per-developer,
  uncommitted) is deliberately dropped.
- **`init`/`recheck` add one pointer line** — not a copy — to `wiki/README.md`
  (Phase 3e step 1) and the `wiki/AGENTS.md` signpost (Phase 3e step 2), which
  sit beside `LINKS.md` in the same repo. `recheck` R5.2 re-evaluates presence
  every run; the `README.md` pointer is exempt from the
  zero-structural-changes skip, so an added or deleted `LINKS.md` is picked up
  even on a quiet run.
- **Absent = the feature is off** — nothing emitted, nothing asked, at zero
  cost to projects with no external hub. `claude` ends with a one-line nudge
  when the file is missing; it never creates it.
- **Why the wiki and not `CLAUDE.md`:** `CLAUDE.md` is per-developer and not
  committed, so a URL parked there is lost on the next regeneration and never
  reaches teammates. The wiki repo is committed, so the pointer is shared and
  survives.
- **Second sanctioned mention of user territory in a generated file** (the
  first being `TASK-WORKFLOW-PROMPT.md` naming `tasks/`): `LINKS.md` is never
  walked as a link-graph *source* and never classified in Phase 1, but it is a
  valid link *target*. If a user deletes it, the deterministic fix is to remove
  the pointer lines — never to create the file.
- No plan `schema_version` bump (stays 1.5) and no new artifact: nothing about
  this is recorded in `plan.yaml`. `LINKS.md` is never a page in the plan,
  never a verifier's concern, never a coverage gap. Ground truth for
  verification remains the source code — a linked page is never a source of
  facts, and no product description, convention, or command may be derived from
  one.

## v14 — 2026-08-12

**New `recheck diff` — audit only what changed since the last verified SHA.**

- New recheck variant, invoked `/wiki-system recheck diff` (`recheck.md`
  § DIFF MODE; SKILL.md routes it inside Mode 2). Same phases, specialists,
  gates, retry caps, and human checkpoints as a full recheck — only the
  **scope** changes: R2 and R3 operate on the git change set since each
  repo's baseline instead of the whole surface. Git is a scoping mechanism,
  not a drift detector: every page in the set still gets a verifier
  sub-agent; pages outside are skipped only because their source snapshot is
  byte-identical. The R3 "only sanctioned narrowings" rule now names the
  change-derived set alongside `verify_breadth` and the R2 drift set.
- **New machine-readable baseline** `wiki/.internal/recheck-baseline.yaml`
  (schema in `spec/plan-schema.md` § recheck-baseline.yaml SCHEMA): per repo
  `verified_sha`/`verified_at`/`mode` (full|diff), `dirty_files[]` (≤100,
  else `dirty_overflow`) and `last_full_sha`/`last_full_at`. Written by
  `init` finalize (Phase 3e step 2) and refreshed by **every** recheck at
  R5.2 (explicitly not covered by the zero-structural-changes skip);
  orchestrator-only single writer, like the decision log. Run-state artifact
  — no plan `schema_version` bump (stays 1.5).
- **Change set** per diff-scoped repo: `git diff --name-status -M
  <verified_sha>` against the **working tree** (uncommitted counts) +
  `git ls-files --others --exclude-standard` (untracked) + the baseline's
  `dirty_files[]` (closes the dirty-then-reverted hole surgically instead of
  a whole-repo fallback). **Verify set**: pages whose `scope_files`
  intersect the change set (deletions and both rename sides count) +
  **anchor pull-in** (pages citing a changed path via `<repo>/<path>`
  anchors, additive only) + R1-flagged pages (stubs, deferred/pending
  failures). `verify_breadth` applies within the set; an empty set
  short-circuits cleanly to R5.
- **Diff-scoped gap scan**: R2.1's per-repo enumeration agents are not
  dispatched; candidates are added/renamed-new/untracked files under the
  usual kind/exclusion filters. A rename's new path is reported with a
  rename hint ("renamed from X — suggested home: the page that scoped X")
  so the R2.4 `extend` decision — still a human checkpoint — is how
  `scope_files` learns new paths. The R2.2 thinning check runs unchanged.
- **Fallbacks, never silent**: per-repo full scope when the baseline entry
  is missing/malformed, the SHA is unreachable, or `dirty_overflow` is set
  (no reconstruction from the prose manifest — a pre-v14 wiki's first
  recheck runs full and writes the baseline); run-level **refusal** when the
  baseline's `generator_version` differs from the current run's; a
  recommendation to run full when the set exceeds
  `diff_full_fallback_ratio` (default 0.5) of plan pages. New quality gate
  (**Baseline integrity**) requires the post-run baseline to match HEAD and
  the diff-run decision-log record (baseline→HEAD SHAs + set sizes).
- **Cadence framing**: diff mode is a fast tier between full rechecks, not a
  replacement — it cannot see claims invalidated by distant changes outside
  the change set. R5.2 emits an advisory staleness nudge (last full verify
  > ~30 days, or the baseline's `diff_runs_since_full` counter ≥ 5) and
  annotates diff-scoped manifest bullets with "(diff recheck — last full
  verify <date>)".

## v13 — 2026-08-12

**Every wiki now ships a task workflow prompt at its docs root.**

- `init` (Phase 3e step 2) and `recheck` (R5.2) install the skill's
  `TASK-WORKFLOW-PROMPT.md` — a paste-ready prompt developers use to run larger
  agent tasks (plan → adversarial review → approval → phased implement with a
  PROGRESS log → final review) — at the docs root as
  `wiki/TASK-WORKFLOW-PROMPT.md`, with every literal `wiki-{workspace-name}`
  placeholder replaced by the actual docs folder name (`meta.wiki_dir`).
  Refresh cadence matches the repo manifest and root signposts: every run,
  explicitly not covered by recheck's zero-structural-changes skip; created
  when missing on wikis generated before v13.
- The installed copy opens with a bespoke **install-header** (not the standard
  generated-header — the file has no `AUTOREGEN_SKIP` mechanism, so its header
  makes no skip-block promise). Opt-out: delete the header line and the file
  becomes user-owned — every subsequent run leaves it untouched (noted once in
  the run summary; a valid state, never a halt or gate failure). A pre-existing
  hand-written file at the path is treated the same way.
- Gates updated: the installed file joins the link-graph walk (it carries no
  relative links), is exempt from the orphan check alongside the signposts, and
  a new "Task workflow prompt" quality gate checks existence + header +
  zero remaining placeholders (or the user-owned opted-out state, which
  passes). `wiki/README.md`'s exhaustive content spec gains a one-line pointer
  to it. Surface lists updated in `SKILL.md` (including the one sanctioned
  mention of user-territory `tasks/` inside a generated file — directing work
  into that folder is the prompt's purpose), `init.md`, `recheck.md`, and the
  explainer `README.md`.
- The task folders the prompt creates (`wiki/tasks/NNN-*/` with `PLAN.md` +
  `PROGRESS.md`) remain **user territory** per the v11 guarantee — never
  walked, verified, or deleted by the skill.
- The source template itself was cleaned of Notion-paste artifacts (bogus
  `http://PLAN.md`-style links, doubled blank lines) so installed copies are
  valid plain markdown with no relative links.

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
- **`README.md` now lists its source repositories.** Its content spec gains a
  `## Source repositories` section — one row per `meta.repos` repo: folder
  name, one-line purpose, `git_url` (or "no remote — local only") +
  `default_branch`; never SHAs or dirty flags, closing instead with a pointer
  to the `## Repositories` manifest in the AGENTS index. Recheck R5.2
  refreshes it whenever the repo set or any `git_url`/`default_branch`
  changes (including an R1 backfill), and creates it on a pre-v12 README.

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
