# Changelog

One entry per `VERSION` bump, newest first. **Update this file in the same
commit that bumps `VERSION`** — the `generator_version` recorded in each
project's `plan.yaml` only tells a recheck *that* the generator drifted; this
file is what tells the operator *what* changed between those versions.

Introduced at v10; earlier versions are not chronicled here (see git history).

## v18 — 2026-08-21

**The installed task workflow prompt is right-sized and its gate made satisfiable.**
Same file, same install mechanism, same section arc; `init.md`'s one-line arc
description is updated because the adversarial plan review is now tier-scoped.

Why: in live use the prompt's tasks ran very long, and a five-lens adversarial
audit (execution-cost simulation, gate satisfiability, logical consistency,
planning quality, verification economics — each a cold-read dispatch) plus a
best-practices sweep (ai-feature-delivery report, agent-papers corpus, current
vendor guidance) agreed on the cause: two unbounded checking loops, a gate that
was unsatisfiable on ~6 ordinary paths (teaching the agent to reinterpret it),
and heavy ceremony applied uniformly regardless of risk. The evidence base is
unambiguous that fresh-context review is a one-pass benefit, that every
verification loop needs a hard cap and a fail branch, and that ceremony should
tier by risk — while planning is where marginal rigor pays, so that side was
strengthened, not trimmed.

Loops bounded:

- **The fix→gate→re-dispatch loop at FINAL REVIEW is capped at two rounds**,
  then STOPs presenting the residual list — "never reinterpret a bullet to pass
  it" is now the gate's explicit fail branch. The re-run CORRECTNESS dispatch
  receives the fix's hunks plus its previous findings list, not the whole diff
  again.
- **Break-it retries are capped**: a named test still green after two break
  attempts is recorded as a coverage gap, not retried forever.
- **Cumulative per-phase re-verification is gone**: a phase runs its own check,
  re-runs an earlier phase's check only when it touched a file that phase
  named, and the full suite runs once — at the gate (which may cite the last
  green run when `git status` shows no edits since).

Gate made satisfiable (each was a hard contradiction before):

- UNVERIFIED items no longer deadlock the gate: the bullet now requires each to
  carry its verbatim `not available` line and appear under residual risk,
  instead of demanding "nothing is left UNVERIFIED" while two earlier rules
  mandate creating exactly that state.
- Red-first is scoped to phases that add or fix behavior; a behavior-preserving
  phase's proof is its post-change break-it (restore proven by re-running the
  named tests green, not by `git diff`, which cannot distinguish the break from
  the phase's own uncommitted change); characterization and end-to-end phases
  are exempt by name. The gate bullet reads "every phase the red-first rule
  covers".
- The one-dispatch collapse (one context both given and not given the plan) is
  replaced: one plan-blind CORRECTNESS dispatch always; a plan-aware
  CONFORMANCE dispatch only when the diff touches a protected surface or an
  in-scope exception, or spans repos. Return files are named
  (review-correctness.md / review-conformance.md) so the gate's existence check
  means something.
- "The requirement" and "the protected-surfaces list" now physically exist:
  UNDERSTAND writes REQUIREMENT.md (restatement + acceptance criteria,
  out-of-scope, protected surfaces + in-scope exceptions, assumptions, OPEN
  RISKS, repro output, localization map) and that file is what every dispatch
  receives — previously those inputs lived only in the conversation, which
  dispatches are forbidden.
- A flaky-test path exists (re-run once; green + file untouched by the diff →
  recorded flaky, treated as pre-existing); pre-existing dirty files are a
  quotable escape on the file-list bullet; an empty repo diffs as its whole
  tree and is exempt from the ancestor check; a successful dispatch records
  `independence: dispatched — {id}` so the gate's per-return check has a
  producer on the happy path; a post-gate fix's row counts as its deviation
  row.

Right-sizing:

- **TIER rule**: LIGHT (one repo, ≤3 non-test files, no protected surface, no
  dependency manifest, no behavior-preserving phase) skips the adversarial plan
  dispatch — the approval STOP remains its review — and the gate re-checks the
  tier against the actual diff, escalating a diff that outgrew it.
- Break-it only on behavior-preserving phases: for additive phases red-first
  already proves the assertion can fail; the prompt previously conceded this
  ("the only proof" language) while mandating both everywhere.
- TOOLING and its baseline suite run are taken lazily per repo the plan or an
  edit names, instead of every repo up front; BASE stays universal (seconds,
  and it is the diff anchor).
- The app/browser exercise happens once, as the plan's end-to-end phase,
  instead of per user-visible phase.

Planning strengthened (the audit's highest-scoring area; gaps closed):

- LOCALIZE before planning: files/symbols as path:line, callers and consumers
  by actual search, repos implicated — recorded in REQUIREMENT.md and cited by
  each phase's "what could break". Blast-radius analysis previously existed
  only in the post-implementation CORRECTNESS brief.
- The plan states its approach and the strongest rejected alternative; the
  adversarial brief attacks that choice, verdicts every coverage-line N/A, and
  is told a plan gap IS a finding (previously "do not propose extra scope"
  could be read as suppressing omissions).
- A phase-size rule (smallest change with its own runnable check), a mechanical
  re-review trigger (file list / verify command / pass criteria changed —
  wording-only edits do not re-dispatch), per-phase restore points
  (phase-{n}-{repo}.patch) that make "restore to last green" and crashed-session
  resume real, and a safety line (dev environments only, never production,
  redact secrets).

Trimmed: rule 4's incorrect claim about what the gate greps, the duplicated
filing rule in SETUP, the doubled falsifiability rationale, the
new-behavior gap demonstration (red-first shows the same absence), and the
per-phase cumulative verification. The summary now also names AGENTS pages the
diff made stale, closing the loop with `recheck diff`.

## v17 — 2026-08-19

**The installed task workflow prompt's mandates are given consumers.** Same file,
same install mechanism, same block structure. Nothing in `init.md` Phase 3e step 2
/ `recheck.md` R5.2 changes; `init.md`'s one-line arc description is updated
because the final review is no longer unconditionally two dispatches.

Why: v16 set the right bar — "nothing was added that no later step reads back" —
and then missed it for its own headline feature. An adversarial pass (three
independent dispatches: one attacking a proposed revision, one cold-reading the
shipped file, one simulating an agent executing it against a bug fix, a refactor
and a cross-repo schema change) found the break-it proof, the cumulative
re-verification and the app/browser exercise were roughly a quarter of the
prompt's mechanical cost while appearing in no gate item, no PROGRESS row spec and
no dispatch brief — and found four checks that were void in ways nothing surfaced.
The fix was not to shorten the prompt but to move its budget: every expensive
mandate now lands in an artifact the gate reads, and the checks that could silently
pass were closed.

Checks that were silently void, now closed:

- **Untracked files never reached FINAL REVIEW.** `git diff <BASE>` omits them, so
  a refactor's new shared helper or a migration file was invisible to both review
  dispatches — and `every file in the diff is in the plan's named file list` passed
  vacuously. FINAL REVIEW now runs `git add -A -N` per repo first.
- **SETUP contradicted the gate.** SETUP records pre-existing test failures; the
  gate demanded an unqualified green suite, so any repo with a known-red or flaky
  test made the gate unpassable and the agent's only out was to reinterpret it.
  The gate now allows exactly the failures TOOLING recorded, quoted from that
  record.
- **The gate never checked that the dispatches happened.** All three reviews could
  be self-attested via the `independence: not available` line with every gate item
  still green. A gate item now requires the return files to exist, each carrying a
  dispatch id or that line, and nothing left UNVERIFIED.
- **Rule 4 claimed gate coverage it did not have** — it named six weakening
  tactics and the gate greps two. The claim is narrowed to the two, and loosened
  assertions, widened types, swallowed exceptions and hardcoded expected values are
  now in the CORRECTNESS dispatch's brief. Under-recording TOOLING is named as a
  fifth weakening tactic, since the gate is parameterised by that record.
- **CONFORMANCE was asked to detect drift from a plan it was never given.** It now
  receives `PLAN.md`; CORRECTNESS AND BLAST RADIUS deliberately does not, so it
  cannot inherit the plan's blind spots. The requirement stays the standard — a
  diff that matches the plan and misses the requirement is a finding.

Mandates that had no consumer, now anchored:

- **The break-it proof** moves from PLAN (where the line to revert does not exist
  yet) to IMPLEMENT, and runs AFTER the change lands — for a behavior-preserving
  phase that is the only proof the moved code is the code being tested. It records
  `broken: {path:line} — restored: yes` on the phase row, and a gate item reads it.
  It stays mandatory for every phase: red-first proves a test fails, not that the
  assertion is what fails, and red on a missing import is not red on the assertion.
- **The app/browser exercise** becomes a gate item, with an
  `app verification: not available — {reason}` fallback mirroring the independence
  line — previously it was a conditional aside mid-paragraph, one of the highest
  value and least enforced checks in the file.
- **Red-first** gets a gate item (a red row recorded before its green one) rather
  than the plan checklist line it used to hide behind.
- **The coverage checklist** drops its hardcoded count and now requires each line
  to carry a handling or an `N/A — {reason}` — presence alone satisfied nothing.
  A line for untrusted input reaching a query, shell, path or template is added;
  the list had no security question, and `the test that must fail before the fix`
  moves out to the red-first gate item where it is actually enforced.

Guards added, one line each: BASE covers every repo directly under the workspace
except the wiki (the dangerous repo is the one you did not expect to touch) and
records `git status --porcelain`, so work already dirty at SETUP is not attributed
to the run; an empty repo is recorded rather than skipped; RESUME keeps the
existing BASE instead of re-recording a baseline that already contains earlier
phases; the task folder is excluded from the file-list gate item, since PLAN.md and
PROGRESS.md live in a repo now covered by BASE; PLAN names its test files, so a new
test file is not a deviation row; the marker check distinguishes an addition from a
move, which fired spuriously on exactly the refactors it should be quietest on;
protected surfaces carry an explicit in-scope exception, so a sanctioned schema
change is not reported as a violation by all three dispatches; the STOP after two
failed fix attempts restores the tree to its last green state, because that path
bypasses the gate; a fix made after FINAL REVIEW re-runs the CORRECTNESS dispatch,
not just the gate; and the work stays uncommitted unless asked — stated in SETUP,
where it is read before phase 1.

Scoping: the header above the `---` now carries an entry condition (more than one
file or repo, or you want it reviewed) — above the line, so it never enters the
agent's context and the size judgment stays with the human. The one in-session
scale-down is objective, not self-assessed: a diff confined to one repo touching no
protected surface may collapse the two final dispatches into one carrying both
briefs. `RESUME` is reachable again — the folder is looked up by ticket/task name
before a number is taken, and numbering is highest-plus-one rather than a count,
which collided after any deletion.

`PLAN` and `IMPLEMENT` are itemized to match the gate's format. Across the
simulations, the mandates that survived a long session were the ones that were
itemized or produced an artifact; the ones that died were prose, and the gate was
the only itemized section in the file.

**Contracts untouched.** Still zero markdown links (so the Phase 3e link-graph walk
finds nothing to resolve and the orphan exemption's "legitimately outbound-linkless"
rationale still holds); `tasks/` remains the only user-territory mention; nothing is
written into the generated track folders. 149 lines to 217.

## v16 — 2026-08-18

**The installed task workflow prompt's review steps are made checkable.** Same
file, same install mechanism, same gates, same block structure — the QA steps are
what changed. Nothing in `init.md` Phase 3e step 2 / `recheck.md` R5.2 changes.

Why: the old prompt asked for an adversarial review and a final review but made
neither *checkable*. Both were reading passes with no dispatch requirement, no
defined diff base, and no rule that a finding or a rejection carry evidence — the
configuration under which self-review measurably degrades output instead of
improving it. Every change below either produces an artifact, a required literal
string, or a mechanical check; nothing was added that no later step reads back.

- **Four rules at the top, covering every step.** Grounded means you ran it (use
  the real tools rather than memory — test/type-check/lint/build, git, subagents,
  the app or a browser for user-visible changes, docs or web search before
  assuming a library's behavior). INDEPENDENT means a separate subagent dispatch
  in a fresh context — preferably a different model — never a second persona in
  the same turn, with the verbatim fallback
  `independence: not available — self-review only` and the item carried as
  UNVERIFIED. Evidence or it did not happen: a command's output tail or a quoted
  `path:line`, and counts read fresh. And **never make a check pass by weakening
  the check** — deleted assertion, added skip, widened type, swallowed exception,
  hardcoded expected value — which the final gate greps for.
- **SETUP records BASE and TOOLING.** The per-repo base commit, which is what
  FINAL REVIEW diffs against and which the old prompt never named; and the
  workspace's real test / type-check / lint / run commands, verified green on
  untouched code so a pre-existing failure is not mistaken for the run's.
- **Before-state evidence.** Reproduce the bug and paste the failing output before
  planning; for new behavior, show it absent today.
- **Phases get independent oracles and a break-it check.** The verify command must
  come from the requirement rather than the implementation, must state what its
  output has to contain to count as a pass (so a suite printing "0 tests found"
  is not one), and must be shown to go red when the change is reverted or a
  condition flipped. A behavior-preserving phase instead names the existing
  covering test and shows it green with the same test count before and after.
- **A nine-item edge-case checklist in PLAN.md**, each line either the handling or
  `N/A — {reason}`, covering what a plan written by the same context that holds
  the blind spot reliably omits: invalid input, empty and first-run state,
  concurrency and idempotency, failure and rollback, authorization, migration and
  backfill, backwards compatibility, production observability, and the test that
  must fail before the fix. The gate checks all nine are present — a checklist
  rather than a review dispatch, because a mechanical check is cheaper and
  harder to skip.
- **ADVERSARIAL REVIEW is a real dispatch with a real brief.** Read-only, given
  only PLAN.md, the requirement and the protected-surfaces list — never the
  conversation — with its verbatim return saved in the task folder. Briefed to
  attack rather than approve: ask where the *inconsistency* is, never whether the
  plan looks sound; go phase by phase, one verdict each; attack each verify
  command specifically; draft both readings where a step is ambiguous; and count a
  constructed case only if the state is reachable and something hangs on it. Every
  finding is folded in or rejected with a **quoted** ground — an ungrounded
  rejection becomes a logged open risk.
- **FINAL REVIEW is two dispatches over the real diff, plus a deterministic
  gate.** Diffed against the SETUP base and given the requirement and
  protected-surfaces list but never the conversation: **conformance** hunk by hunk
  and **correctness and blast radius** per changed function. The gate is
  judgment-free: suite green with output tail, type-check and lint clean where
  those exist, every changed file in the plan's list or carrying a deviation row,
  no deleted assertion or added skip/only/xfail/ignore without justification, no
  focused test left behind, all nine edge-case lines present, base commit still an
  ancestor of HEAD. Fixes re-run the gate, because a fix invalidates the green run
  before it.
- **Implementation discipline**: red-first with the failing output pasted, each
  phase re-running the earlier phases' checks, one real exercise in the app or
  browser for user-visible changes, and a stop after two failed fix attempts
  rather than a third try.
- **Contracts untouched.** Still zero markdown links (so the Phase 3e link-graph
  walk finds nothing to resolve and the orphan exemption's
  "legitimately outbound-linkless" rationale still holds); `tasks/` remains the
  only user-territory mention; nothing is written into the generated track
  folders. 55 lines to 149.
- `init.md`'s one-line description of the prompt's arc updated to match.

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
