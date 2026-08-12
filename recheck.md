Your task is to re-check an existing wiki against the current source code, surface
gaps, and correct drift — without re-planning or re-writing the wiki from scratch.

This prompt is a **recheck orchestrator**. It composes the same writer and
verifier sub-agent contracts defined by `init.md`, `specialists/agents.md`,
`specialists/technical.md`, `specialists/product.md`, and `specialists/verifier.md`. It
does NOT redefine those contracts. It respects the enabled `meta.tracks` (default `[agents]`):
it only verifies/regenerates pages for enabled tracks, and maps each page's `owner_agent`
to its verifier mode (`agents`/`technical`/`product`) per `init.md` Phase 3d.
Where this prompt links out, follow the linked spec exactly — do not
re-invent the rules.

---

## TWO ROOTS

This skill operates with two unrelated roots — same as `init.md` § TWO ROOTS. **Skill files** (this `recheck.md`, `init.md`, `specialists/`, `spec/`) are referenced by paths relative to this prompt file. **Project files** (`wiki/`, `wiki/.internal/plan.yaml`, the sibling code repos, source code) are relative to CWD (the **workspace**); `wiki/` means the resolved `wiki-{project}/` docs folder (SKILL.md § Pre-flight resolves it). Never confuse them.

---

## CONFIGURATION

This prompt inherits target-repo and product-description discovery from `init.md` § CONFIGURATION. Read it before starting. Recheck does not re-discover repos from scratch — it trusts the existing `wiki/.internal/plan.yaml`'s `meta.repos` list. If that list is missing, halt and re-run `init.md`. A repo from `meta.repos` being **absent from the workspace is not an error** — it is handled as partial access (Phase R1 step 5).

The only recheck-specific knobs:

```
- coverage_gap_scan: true | false   # default true; set false to skip Phase R2
- verify_breadth: all | by_complexity   # default all; by_complexity skips S-tier per init.md Phase 3d
- regen_disabled: false              # set true for a verify-only audit (no writer dispatches)
- diff_mode: false                   # true when invoked as `recheck diff` — scope R2/R3 to what
                                     # changed since the per-repo baseline; see § DIFF MODE
- diff_full_fallback_ratio: 0.5      # diff mode only: when the change-derived verify set exceeds
                                     # this fraction of plan pages, recommend a full run instead
```

(The auto-fix retry cap is fixed at one — see R4.2. It is not a configurable knob. After the cap, surviving failures route through tier-2 verifier escalation and, if still failing, the R4.3 user resolution gate.)

---

## DIFF MODE (`recheck diff`)

Invoked as `/wiki-system recheck diff` (sets `diff_mode: true`). Same phases,
same specialists, same gates, same retry caps — the only thing diff mode
changes is **scope**: R2 and R3 operate on what changed since each repo's
baseline instead of the whole surface. It is a cadence tier for frequent,
cheap runs between full rechecks — not a replacement for them (see "What diff
mode cannot catch" below).

**Git is a scoping mechanism here, not a drift detector.** Every page in the
change-derived set is still verified by a verifier sub-agent — nothing is
ever "grep-verified." Pages outside the set are skipped for one reason only:
their source snapshot is byte-identical between the baseline and now, so
there is nothing new to confront them with. The verifier remains the only
sanctioned drift detector (§ CONSTRAINTS).

### Baseline

The per-repo baseline is `wiki/.internal/recheck-baseline.yaml` — schema in
`spec/plan-schema.md` § recheck-baseline.yaml SCHEMA. Loaded in R1 step 6;
resolve per **present** repo:

- Entry present, `git -C <repo> cat-file -e <verified_sha>^{commit}`
  succeeds, and `dirty_overflow` is false → the repo runs in **diff scope**.
- File missing, entry missing or unparseable, SHA unreachable, or
  `dirty_overflow: true` → **per-repo fallback**: this repo runs at full
  scope this run (R2.1 enumeration + its pages verified per R3's breadth
  rules) and
  gets a fresh baseline entry at R5.2 with `mode: full`. Other repos
  continue in diff scope independently. Never reconstruct a baseline from
  the prose `## Repositories` manifest or from memory — an unusable baseline
  means full scope, not a guessed diff.
- **Run-level generator gate:** if the baseline file's `generator_version`
  differs from this run's, **refuse diff mode** and tell the user to run a
  full `recheck` — a prompt/model change shifts what counts as a defect, so
  a diff scope would structurally miss newly-detectable issues (the same
  logic as R1 step 1's `verify_breadth: all` preference). Do not silently
  degrade.
- Absent repos: unchanged partial-access rules (R1 step 5) — skipped
  entirely, baseline entries preserved verbatim.

### Change set (per diff-scoped repo)

```
git -C <repo> diff --name-status -M <verified_sha>      # baseline → WORKING TREE
git -C <repo> ls-files --others --exclude-standard      # untracked files
```

The change set is the union of: every `M`/`A`/`D` path; **both** sides of
every `R` rename row; every untracked file; and the baseline entry's
`dirty_files[]` (paths dirty at the last finalize — a file dirty then and
reverted since would otherwise diff as "unchanged" while the pages describe
its dirty state). Diffing against the working tree — not HEAD — is
deliberate: pages document the tree the developer sees, committed or not.

### Verify set (what R3 dispatches instead of all pages)

The union of:

1. **Scope intersection** — every page whose glob-expanded `scope_files`
   match any change-set path. Deleted files and both rename sides count: a
   page scoping a deleted file must be verified — its claims now point at
   nothing.
2. **Anchor pull-in** — grep the enabled track folders for the anchor form
   `<repo>/<changed-path>` (and the bare `<changed-path>` within repo-scoped
   page folders, per the manifest's anchor-resolution note); every page
   citing a changed file joins the set even when its `scope_files` don't
   cover it. Additive only — the grep can never remove a page from the set,
   and its results are never treated as verification.
3. **R1-flagged pages** — incomplete stubs (synthetic `fail_hard`, as ever)
   and pages with a prior `_failures.md` entry whose `resolution.status` is
   `deferred` or `pending`. R1 gives these priority; a diff run does not let
   them hide behind an unchanged scope.

`verify_breadth` still applies **within** this set (`by_complexity` skips
S-tier members per its normal rule). Pages outside the set are left exactly
as committed this run — not verified, not modified, not flagged.

- **Clean short-circuit:** when the change set itself is empty (no tracked
  diff, no untracked files, no carried `dirty_files[]`), skip the gap scan
  and all R3/R4 dispatches, report "no changes since baseline," and continue
  to R5 — the baseline still advances (trivially sound: the content is
  identical). An empty **verify set** with a NON-empty change set is *not* a
  short-circuit: the gap scan and the R2.4 checkpoint still run (an added
  file no page scopes or cites produces exactly this shape), and any user
  `extend`/`new` decision feeds R4.1 items (3)/(4) writer dispatches as
  usual.
- **Ratio guard:** if the set exceeds `diff_full_fallback_ratio` of plan
  pages, tell the user a full recheck costs barely more and recommend it;
  proceed in diff scope only if they explicitly choose to. Never decide
  silently.

### Gap scan (replaces R2.1's enumeration agents)

Do **not** dispatch per-repo enumeration sub-agents for diff-scoped repos.
Gap candidates are only: `A` paths, untracked files, and rename **new**
paths — filtered by the same documentable-kind and exclusion rules as
`init.md` Phase 1's surface enumeration (tests, generated code, lockfiles
etc. drop out). Bucket every candidate not matching any page's `scope_files`
as `uncovered_new`. A rename whose new path falls outside every scope glob
is reported with a **rename hint** — "renamed from `<old-path>`; suggested
home: the page(s) that scoped the old path" (list them all; when several,
name a reference-track page first) — so the natural R2.4 decision
is `extend`, the sanctioned way `scope_files` learns the new path (recheck
never patches the plan without a user decision). When the user chooses
`extend` on a rename-hinted row, **replace** the old path with the new one in
every page's `scope_files` that listed it — a rename is a move, not an
addition; leaving the old path behind ships a plan pointing at a nonexistent
file. Record the multi-page patch in `decisions.md`. The R2.2 page-thinning
check is agent-free and runs unchanged, as do the R2.3 report and the R2.4
human checkpoint.

### What diff mode cannot catch (why full rechecks stay in the cadence)

A claim invalidated by a *distant* change — "this loop is duplicated across
4 call sites" going stale when a 5th appears in a file no page scopes and no
anchor cites — is invisible to diff scoping; anchor pull-in narrows this
class but cannot close it. The full-breadth cross-page contradiction sweep
is likewise narrowed. Hence the **staleness nudge** (emitted at R5.2,
advisory only, never a gate): when any repo's `last_full_at` is older than
~30 days, or its baseline entry's `diff_runs_since_full` counter has reached
5, recommend a full `recheck` in the run summary.

---

## WHEN TO USE THIS PROMPT

| Situation | Use this | Use something else |
| --- | --- | --- |
| "I haven't pushed in weeks; verify everything before a demo" | ✅ this prompt | |
| "I want to find code that isn't documented at all" | ✅ this prompt | |
| "Quick drift check — what changed since the last recheck / after a merge burst" | ✅ this prompt, as `recheck diff` (§ DIFF MODE) | |
| "I added a new repo or changed the wiki's top-level structure" | | `init.md` (re-plan) |
| "A specific page looks stale; just check that one" | | Dispatch `specialists/verifier.md` directly against the page |

This prompt **trusts the existing `wiki/.internal/plan.yaml`**. It does not re-plan.
If the plan itself is wrong (new top-level area, schema bump, repo added),
stop and use `init.md` instead.

---

## ROLE

You are a recheck orchestrator. You do not write documentation pages directly.
Your job is to:

1. Load the existing plan and on-disk wiki state
2. Detect documentation coverage gaps in the source code
3. Dispatch verifier sub-agents against every relevant page
4. Dispatch writer sub-agents to correct any failures (with one auto-fix retry, max)
5. Re-finalize the wiki's root artifacts

You inherit three standing rules from `init.md`:

- The `wiki/.internal/plan.yaml` schema (`spec/plan-schema.md`) is authoritative
- Sub-agents follow their specialist prompts — do not override them
- Hand-edit zone markers (`<!-- AUTOREGEN_SKIP_BEGIN/END -->`) are preserved verbatim

---

## PHASE R1: LOAD EXISTING STATE

Sequential and fast. No sub-agents.

1. **Read `wiki/.internal/plan.yaml` in full.** This is the authoritative spec. If it does
   not exist, halt — this prompt requires a prior plan. Run `init.md` first.
   Note `meta.generator_version`: if it differs from the current generator (skill
   version in `SKILL.md` + this run's model id), the wiki was produced by an older
   skill or model. Prefer `verify_breadth: all` in that case even if you'd
   otherwise narrow it — a prompt/model change can shift what counts as a defect,
   so a drift-only scope may miss newly-detectable issues. Record the generator
   change in the decision log.
2. **Validate the plan against `spec/plan-schema.md` § INVARIANTS.** Any
   violation halts the recheck — fix the plan or run `init.md` to regenerate.
3. **Walk the enabled tracks under `wiki/`** (`wiki/AGENTS`, `wiki/TECHNICAL`, `wiki/PRODUCT` — only those the plan enables). For every page in the plan, confirm the file
   exists on disk and is not still a `*TODO*` stub. Pages that are still stubs
   are recorded as "incomplete from prior run" and flow into Phase R3 with an
   automatic `fail_hard` verdict (no verifier dispatch needed — there's nothing
   to verify).
4. **Read `wiki/.internal/verification/`** if it exists. Parse
   `_failures.md` per the schema in `spec/plan-schema.md` § `_failures.md`
   SCHEMA. Pages with `resolution.status: deferred` (or `pending` from an
   aborted prior run) get priority in Phase R3. Entries with terminal
   statuses (`regenerated`, `patched`, `shrunken`, `accepted`, `deleted`,
   `fail_hard_post_user`) require no action — they are audit history.
5. **Resolve repo availability (partial access).** For each repo in `meta.repos`,
   check whether its folder is present in the workspace (matched by folder name).
   Split into **present** and **absent** sets. A page is *backed by* a repo if any of
   its `scope_files` live under that repo's folder.
   - **Absent repos are skipped, not failed.** Pages backed *only* by absent repos are
     excluded from Phase R2 enumeration and Phase R3 verification this run — left
     exactly as committed, with the existing wiki treated as the **source of truth**
     for them: no coverage gap, no drift flag, no `fail_hard`, no deletion.
   - A page backed by a mix of present and absent repos is verified normally against
     the parts it can see; never flag absent-repo material as drift.
   - If any repo is absent, **report it at the start and end of the run** — e.g.
     "Skipped 2 repos not in this workspace (repo-x, repo-y); their pages were left
     unchanged and treated as source of truth — clone them and re-run to refresh."
     Never delete or `fail_hard` a page merely because its source repo is absent.
   - While resolving availability, **backfill remote provenance** for each *present*
     repo whose plan entry predates schema 1.5 (no `git_url` field): run
     `git -C <repo> remote get-url origin` and record `meta.repos[].git_url`
     (`null` if no remote — never guess), plus `default_branch` when cheaply
     determinable. This feeds the repo-manifest refresh in R5.2. Absent repos
     keep whatever their plan entry already has.
6. **Load the diff baseline (diff mode only).** Read
   `wiki/.internal/recheck-baseline.yaml` and resolve each present repo to
   diff scope or per-repo full fallback per § DIFF MODE "Baseline" —
   including the run-level generator gate, which may refuse diff mode
   outright. Plain recheck skips this step (the file is only written, at
   R5.2).

---

## PHASE R2: COVERAGE-GAP SCAN (HUMAN CHECKPOINT)

This is the capability `init.md` Phase 3d does not provide: detecting
**source code that has no documentation at all**, not just drift in what is
documented. Skip this phase only if `coverage_gap_scan: false` in CONFIGURATION.

The verifier checks claims *inside* a draft against source. It cannot say
"the source has three new endpoints that no page mentions." Phase R2 fills that
gap by scanning source for documentable surface and asking whether each piece
maps to a page in the plan.

**Diff mode:** for diff-scoped repos, R2.1's enumeration agents are NOT
dispatched — the candidate list comes from the change set instead (§ DIFF
MODE "Gap scan"). R2.2–R2.4 run unchanged. Repos that fell back to full
scope run R2.1 normally.

### R2.1 Enumerate documentable surface

Enumerate the documentable surface per **present** repo (Phase R1 step 5 — repos
absent from the workspace are skipped, their pages kept as source of truth).
**Dispatch one enumeration sub-agent per present repo, in parallel** (same pattern
and concurrency cap as `init.md` Phase 1's per-repo scan) — each reads its repo's `CLAUDE.md` first
(the source of truth for what counts as a unit of documentation there) and
returns that repo's surface list. This runs the repos concurrently and keeps raw
source out of the orchestrator's context.

Common surface to enumerate (adjust per repo):

- API: route files, controller files, model files, middleware, services, jobs,
  agent definitions, integration wrappers
- Client: page/screen components, hooks, providers, route files, API client modules
- Shared: types, utilities visible across boundaries

Each agent returns its repo's rows; the orchestrator merges them into one flat
list: `[{ repo, path, lines, kind }]`.

### R2.2 Match against existing scope_files

For each enumerated file, intersect against the union of `scope_files` globs
across every page in the plan. Each enumerated file falls into exactly one bucket:

| Bucket | Meaning |
| --- | --- |
| `covered` | At least one page's `scope_files` matches this file. Verifier in Phase R3 will check for drift. |
| `uncovered_new` | No page's `scope_files` matches this file, AND the file did not exist at plan generation time (per `meta.generated_at` and git log). Suggests a feature added since last plan. |
| `uncovered_existing` | No page's `scope_files` matches this file, AND the file existed when the plan was generated. Suggests a planning miss, not new code. |

Then check for **page thinning** on covered scope: for each page, sum `wc -l`
over its current `scope_files` and compare to the plan's `scope_loc_estimate`.
Flag pages where actual LOC exceeds the estimate by **2× or more** as
`expansion_candidate` — the page may be missing material added since it was written.

### R2.3 Write the coverage-gap report

Write `wiki/.internal/verification/_coverage_gaps.md` with three sections:

```markdown
## Uncovered (new since plan)
| Repo | File | Lines | Suggested home page |
| --- | --- | --- | --- |
...

## Uncovered (existed at plan time — planning miss)
| Repo | File | Lines | Suggested home page |
| --- | --- | --- | --- |
...

## Pages with growth ≥ 2× plan estimate (expansion candidates)
| Page id | Plan estimate | Actual LOC | scope_files |
| --- | --- | --- | --- |
...
```

For "Suggested home page," apply this heuristic: pick the existing page whose
`scope_files` cover the same directory or sibling files. If no clear fit,
mark "NEW PAGE NEEDED" with a proposed section.

### R2.4 Halt for human review (CHECKPOINT)

Present the coverage gap report to the user. Ask which of three actions to take
for each row:

- **extend** — append the file to an existing page's `scope_files` and re-dispatch
  that page's writer in Phase R4
- **new** — add a new page via a `split_request`-style patch to `wiki/.internal/plan.yaml`,
  stub it, and dispatch a fresh writer in Phase R4
- **defer** — do nothing this run; user accepts the gap

**Do not auto-decide.** Auto-expanding scope produces runaway costs and silent
plan creep. The user's decisions become inputs to Phase R4. If the user defers
all gaps, Phase R4 still runs against any failures from Phase R3.

After the user responds, patch `wiki/.internal/plan.yaml` accordingly (for `extend` or
`new` decisions). Stub any new pages per `init.md` Phase 3a before continuing.

---

## PHASE R3: VERIFY (FULL-BREADTH BY DEFAULT)

Parallel. Dispatch verifier sub-agents against every page in the plan — or,
in diff mode, against the change-derived verify set from § DIFF MODE — with
breadth controlled by CONFIGURATION:

- `verify_breadth: all` — every page in `pages[]` (default)
- `verify_breadth: by_complexity` — every page with `complexity` ≥ M, plus every
  page with `section_parity: strict` regardless of complexity (matches
  `init.md` Phase 3d default)

**R3 is mandatory and not elidable.** The verifier pass is the whole point of a
recheck. The *only* sanctioned ways to narrow it are the `verify_breadth` setting
above, the drift-driven page set from R2, and diff mode's change-derived
verify set (§ DIFF MODE — which may legitimately be empty on a quiet repo) —
all of which still run the verifier sub-agent on the pages they cover. Do **not** substitute a manual read
or a `grep`/stale-claim sweep for the verifier pass, and do not skip it by
declaring drift "high-confidence" and rewriting directly. (Surgical corrections
are allowed in R4 — but anything you edit must then be re-verified, never just
grep-checked.) A grep sweep catches the token patterns
you thought to search for; the verifier catches the ones you didn't — including
cross-page contradictions (a claim fixed on one page but left stale on a sibling),
which is a failure mode this skill has shipped before. If cost is the concern, set
`verify_breadth: by_complexity` — do not skip R3.

### R3.1 Dispatch

Read `specialists/verifier.md` once at the start of the phase. Then build a dispatch
batch using the verifier brief template in `init.md` § SUB-AGENT
DELEGATION PRINCIPLES — do not redefine the brief here.

For each verifier dispatch, set:

- `agent_id`: `verifier-<page-slug>.recheck` (the `.recheck` suffix
  distinguishes this run's reports from prior runs)
- `report_path`: `wiki/.internal/verification/<page-id>.yaml` (overwrites prior report
  for that page — the latest verdict is the live one)

Use the worker pool sizes from `init.md` § SCALING RULES (max 10
concurrent). Pages flagged as "incomplete stub" in Phase R1 skip verifier
dispatch and go straight to Phase R4 with a synthetic `fail_hard` verdict. Pages
backed **only** by repos absent from the workspace (Phase R1 step 5) are excluded
from the verify set entirely — not dispatched, left as committed.

Because the verifier is invoked unchanged from `specialists/verifier.md`, it
inherits that prompt's header-ignore rule: the line-1 generated-header (like an
`AUTOREGEN_SKIP` block) is not a claim, is not counted in `total_claims`, and is
never flagged as unanchored. So the header that R4 writers and R5.2 emit does not
churn or fail re-verification.

### R3.2 Collect verdicts

Tally `pass`, `fail_soft`, `fail_hard` counts.

**Apply the suspect-pass calibration rule** from `init.md` Phase 3d: a
`pass` whose report shows `stats.resolved == 0` on a `complexity ≥ M`
page is re-dispatched to the verifier once. If it still returns `pass`
with `resolved == 0`, accept the page but record it under a
"Low-confidence passes" heading in `_failures.md` (free-prose audit
section — does not enter the gate queue, does not block run completion).
S-tier pages with legitimately few claims are not gated.

If `regen_disabled: true` in CONFIGURATION, skip Phase R4 (including
R4.3) and jump to Phase R5 — Phase R5 will write a summary noting the
failures without attempting to fix them. This is the verify-only audit
mode.

---

## PHASE R4: CORRECT FAILURES

Parallel where possible. Dispatch writers to fix verified problems.

### R4.1 Build the correction queue

The queue is the union of:

1. Pages with verdict `fail_soft` from Phase R3
2. Pages with verdict `fail_hard` from Phase R3 — these are queued for the
   **R4.3 user resolution gate** at the end of this phase; they are not
   auto-dispatched by R4.2
3. Pages added via Phase R2.4 `new` decisions
4. Pages flagged for `extend` via Phase R2.4 (their `scope_files` were patched)

Pages in (1), (3), and (4) are auto-dispatched in R4.2. Pages in (2), and
any (1) page that escalates to `fail_hard` after its retry + tier-2
verifier, flow into R4.3.

### R4.2 Dispatch writers

Use the writer brief template in `init.md` § SUB-AGENT DELEGATION
PRINCIPLES. For `fail_soft` re-dispatches, attach the verifier's `issues` list
per the auto-fix re-dispatch protocol in `init.md` Phase 3d.

Every regenerated page keeps the generated-header as its first line (writers emit
it unchanged per their specialist prompts):

```
> _Generated by wiki-system from source — do not edit here. Run `/wiki-system recheck` to refresh; put durable hand-written notes in an `AUTOREGEN_SKIP` block._
```

**Carry forward prior failures (lightweight cross-run memory).** Whenever
a writer is dispatched against a page that has a prior `fail_hard` entry
in `_failures.md` from an earlier run — whether the dispatch is the R4.2
auto-fix retry OR the R4.3 user-initiated `regen_with_context` /
`patch_scope` — include a one-paragraph summary of the most recent prior
failure in the brief: "Last time this page failed for X — make sure the
rewrite does not repeat it." This is the cheapest form of learning across
runs — it reuses an artifact you already read in Phase R1 and stops
recurring mistakes, without any new buffer or injection machinery.

For each successful re-write, dispatch one verifier (Phase R3 brief, with
`.retry1` suffix on the report path).

**Re-verification is mandatory for every page whose content changed this run —
no exceptions.** This applies whether the page was changed by a writer
re-dispatch OR by a direct/surgical orchestrator edit (a one-line numeric or path
correction). Surgical edits are allowed for precise, evidence-backed fixes, but a
surgically-edited page is not "done" until a verifier sub-agent has re-checked it
and written a current report. A stale-claim grep may run as an *additional*
detector; it never replaces this re-verification. The reason is concrete: surgical
edits fix the page in front of you but routinely leave the same claim stale on a
sibling page — only a verifier reading each page against source catches that.

**Hard cap: one auto-fix retry per page.** This is identical to `init.md`
Phase 3d. If a re-verified page is still `fail_soft` or worse, run the
tier-2 verifier escalation (`init.md` Phase 3d — same spec; report path
`wiki/.internal/verification/<page-id>.tier2.yaml`). If tier-2 returns
`pass`, accept. Otherwise escalate to `fail_hard` and queue for R4.3. Do
not loop. Past runs that allowed multiple writer retries either oscillated
between two failure modes or compounded errors — the cap is load-bearing
and not configurable.

### R4.3 User resolution gate (CHECKPOINT)

Mirror of `init.md` Phase 3d.5 — full spec (per-page surface, resolution
menu, re-dispatch budget after user action, `delete_page` ripples,
`accept_with_banner` durability) lives there. Do not duplicate; read once
and apply. The recheck-specific differences:

- The queue is every page flagged `fail_hard` this run, from two sources:
  (a) R3 direct `fail_hard` verdicts that bypassed R4.2 auto-dispatch, and
  (b) R4.2 escalations — `fail_soft` pages whose retry + tier-2 verifier
  also failed.
- If the queue is empty, skip R4.3 entirely and proceed to Phase R5.
- For pages that already have a prior `_failures.md` entry from an earlier
  run (any status), surface the prior failure summary alongside this run's
  findings so the user sees the pattern. A page that has failed in the same
  way across three runs is a delete or scope-rewrite candidate, not another
  regen.
- The **Carry forward prior failures** rule from R4.2 also applies here:
  if the user picks `regen_with_context` or `patch_scope`, the writer
  brief carries the prior-failure summary alongside the user's hint.

The run does not advance to Phase R5 until every queued `fail_hard` page has
`resolution.status` set to a terminal value (not `pending`).

---

## PHASE R5: FINALIZE

Sequential. No sub-agents.

### R5.1 Re-run deterministic gates

Run the deterministic checks from `init.md` § QUALITY GATES — at minimum:

- Link graph (all relative links resolve)
- Orphan check (every page is inbound- and outbound-linked)
- Numeric consistency (counts agree across sibling pages)
- Plan coverage (every plan page exists on disk and is not a stub)
- Verification coverage (every page that should have a report has one)

Write a fresh `wiki/.internal/link-report.md`.

Also append this run's material decisions to `wiki/.internal/trace/decisions.md`
per the decision-log spec in `init.md` Phase 3e step 5 — including the per-run
**generator header** (skill version + model) and the orchestrator-only write rule
(coverage-gap decisions from R2.4, parity downgrades, `fail_hard` escalations,
writer disagreements). The log is append-only — never truncate prior runs.

Emit the **run-level diagnostics** from `init.md` Phase 3e step 6 (loop-friction
per section + the framework-level rubric critique) in the recheck summary — they
are especially useful here, where recurring drift across runs is the signal worth
catching.

### R5.2 Refresh root artifacts

Regenerate `wiki/README.md` from the now-current
reference tree per `init.md` Phase 3e. It is the human table of contents and
lists only the enabled tracks (`wiki/AGENTS`, `wiki/TECHNICAL`, `wiki/PRODUCT` — those
present on disk; never assume a track exists). Its first line is the
generated-header, verbatim:

```
> _Generated by wiki-system from source — do not edit here. Run `/wiki-system recheck` to refresh; put durable hand-written notes in an `AUTOREGEN_SKIP` block._
```

Hand-edit zones survive.
Skip the `wiki/README.md` regeneration if the recheck made zero structural
changes (no new pages, no extended scope, no successful regens) — there is
nothing new to surface at the root.

**Pre-v12 migration is NOT covered by that skip.** If the wiki still has a
docs-root `index.md` as its front door (generated before v12), migrate it this
run regardless of structural changes: write `wiki/README.md` per `init.md`
Phase 3e step 1 (carrying over any `AUTOREGEN_SKIP` blocks verbatim), delete
`wiki/index.md`, and refresh the `AGENTS.md` signpost's "humans start at" line.
If a hand-written user `README.md` (first line ≠ generated-header) already
occupies the slot, do not overwrite it silently — surface the conflict per the
migration note in `init.md` Phase 3e step 1.

**The repo manifest is NOT covered by that skip — refresh it on every run.**
Rewrite the `## Repositories` section of every enabled code-anchored track
index (`wiki/AGENTS/index.md`; `wiki/TECHNICAL/index.md` when the technical track
is enabled — never PRODUCT) per `init.md` Phase 3e step 2: for each **present**
repo, record the current
`git -C <repo> rev-parse HEAD` SHA, the dirty flag from
`git -C <repo> status --porcelain`, `git_url`/`default_branch` from the plan
(including any R1 backfill), and this run's verification date. An **absent**
repo keeps its existing manifest entry verbatim, annotated
"not present this run — last verified <date>". A recheck that verified pages
against new code but left old SHAs in the manifest would misstate what the
docs were checked against — this step is why the manifest can be trusted.

**The diff baseline is likewise NOT covered by that skip — write it on every
run.** Rewrite `wiki/.internal/recheck-baseline.yaml` (schema:
`spec/plan-schema.md` § recheck-baseline.yaml SCHEMA) from the same finalize
data as the manifest. Per present repo: `verified_sha` =
`git -C <repo> rev-parse HEAD`, `verified_at` = today, `mode` = how this repo
was verified this run (`diff`, or `full` — a plain recheck, or a per-repo
fallback inside a diff run), `dirty_files` = the repo-relative paths from
`git -C <repo> status --porcelain` (cap 100; beyond that set
`dirty_overflow: true` and leave the list empty),
`last_full_sha`/`last_full_at` advanced only when `mode: full`, and
`diff_runs_since_full` incremented on a diff-scoped verify and reset to 0 on
a full one (the counter behind the staleness nudge). Absent repos keep their
entries verbatim. On diff runs, additionally append to each
diff-scoped repo's manifest bullet: "(diff recheck — last full verify
<last_full_at>)", and emit the staleness nudge (§ DIFF MODE) in the run
summary when it applies.

The `## Source repositories` list in `wiki/README.md` carries no SHAs, so it
is not part of the every-run refresh — but refresh it (even under the
zero-structural-changes skip) whenever the repo set or any
`git_url`/`default_branch` changed, including an R1 backfill; create the
section if a pre-v12 README lacks it.

Also rewrite the root agent signposts (`wiki/AGENTS.md` + `wiki/CLAUDE.md`)
per `init.md` Phase 3e step 2 — same every-run cadence, creating them if a
pre-signpost wiki lacks them.

**The installed task workflow prompt is likewise NOT covered by that skip —
refresh it on every run.** Reinstall `wiki/TASK-WORKFLOW-PROMPT.md` per
`init.md` Phase 3e step 2: re-read the skill's `TASK-WORKFLOW-PROMPT.md`
template, substitute every literal `wiki-{workspace-name}` with
`meta.wiki_dir`, prepend the install-header, and replace the file wholesale —
creating it when missing (wikis generated before v13). If an existing file's
first line is NOT the install-header it is user-owned: leave it untouched and
note the skip once in the run summary (valid opted-out state, not a failure).

### R5.3 Do NOT touch CLAUDE.md

`recheck` never writes `CLAUDE.md` — it is owned by the separate `/wiki-system
claude` command (`claude-md.md`). If Phase R2.4 added new pages or moved scope
(i.e. the layout the agent-context file describes may now be stale), **suggest**
the user run `/wiki-system claude` to refresh it. Otherwise say nothing about it.
Documentation is refreshed on request, not as a recheck side effect. The
`CLAUDE.md` standard (lean, ≤200 lines, count-free, history-free) and the
on-request policy live in `claude-md.md` — recheck neither enforces nor edits
them.

---

## QUALITY GATES (recheck-specific)

Run these before reporting the run as complete. Subset of `init.md`
§ QUALITY GATES, plus two recheck-only gates:

- [ ] **Plan unchanged unless user approved patches.** If `wiki/.internal/plan.yaml`
      changed, every change must correspond to a Phase R2.4 user-approved
      decision.
- [ ] **No silent regen.** Every regenerated page has a `fail_soft` verdict
      from Phase R3 in its prior `wiki/.internal/verification/<id>.yaml` (or is on the
      Phase R2.4 user-approved list). Pages that were regenerated without a
      failing verdict are a bug — investigate.
- [ ] **Every modified page re-verified (HARD GATE).** Every page whose content
      changed this run — by writer re-dispatch OR by a direct/surgical orchestrator
      edit — has a verification report written *this run* (`verified_at` is today,
      e.g. a `.recheck`/`.retry1` report). A page that was edited but has no
      current report fails this gate; do not report the run complete. A
      stale-claim grep sweep does NOT satisfy this gate. This is the gate that
      stops surgical edits from silently leaving sibling pages contradictory.
- [ ] **Baseline integrity.** `wiki/.internal/recheck-baseline.yaml` exists
      and, for every present repo, its `verified_sha` equals
      `git -C <repo> rev-parse HEAD` at finalize and `mode` reflects how the
      repo was verified this run. On a diff run, `decisions.md` records the
      baseline→HEAD SHAs and the set sizes (pages verified / skipped / gap
      candidates) per diff-scoped repo. A diff run that cannot state which
      baseline it diffed from is a bug.
- [ ] **Failures triaged.** Every `fail_hard` verdict from this run has a
      user-recorded resolution (`regen_with_context` / `patch_scope` /
      `scope_shrink_stub` / `accept_with_banner` / `delete_page` / `defer`)
      in its `_failures.md` entry. Entries with `resolution.status: pending`
      block this gate. `fail_hard_post_user` (a user-initiated re-attempt
      that also failed) is a valid terminal state and does **not** block
      the gate. Stale entries from prior runs are not removed (audit
      trail); the latest run's findings appear at the top with their
      decision metadata.

---

## CONSTRAINTS

- This prompt does not re-plan. `wiki/.internal/plan.yaml` may be patched only via
  Phase R2.4 user-approved decisions. Any other modification is a bug.
- This prompt does not modify writer or verifier specialist prompts. They are
  invoked unchanged.
- **Phase R3 (verify) is mandatory and the verifier is the only sanctioned
  drift detector.** Substituting a manual read, a `grep`/stale-claim sweep, or a
  "direct high-confidence rewrite" for the verifier pass is a spec violation. To
  reduce cost, narrow `verify_breadth` or run `recheck diff` (§ DIFF MODE — git
  scopes the verify set; it never substitutes for verification) — never skip R3.
- **Diff mode never degrades silently.** Per-repo fallbacks, the run-level
  generator refusal, and the ratio recommendation are all surfaced to the
  user; a diff run must state which repos ran in diff scope, which fell
  back, and why. R4/R4.3 run unchanged in diff mode — a smaller verify set
  never loosens failure handling.
- The baseline (`wiki/.internal/recheck-baseline.yaml`) is written only at
  R5.2 (single-writer, like the decision log) and never reconstructed from
  the prose manifest, memory, or guesswork — an unusable baseline means
  per-repo full scope, not a guessed diff.
- **Every page the run edits must be re-verified before R5** — writer
  re-dispatches and direct/surgical orchestrator edits alike (R4 + the
  "Every modified page re-verified" QUALITY GATE). An edited page with no
  current verification report means the run is not complete.
- Auto-fix retry cap is **one**. Multiple retries are forbidden.
- Phase R2 requires human checkpoint before patching the plan. Auto-decided
  expansion is forbidden.
- Files outside the enabled tracks under `wiki/` are out of scope. The recheck
  never writes to the wiki root except as Phase R5 specifies, and never reads,
  walks, or mentions user-owned docs-root files or folders (task workspaces,
  audit/research folders — anything the skill did
  not generate). This includes the R5.1 deterministic gates, which run at the
  generated-surfaces scope defined in `init.md` Phase 3e step 3 / § QUALITY
  GATES.
- **Partial access:** a repo from `meta.repos` absent from the workspace is skipped,
  not failed. Pages backed only by absent repos are never verified, modified, flagged,
  or deleted this run — the committed wiki is their source of truth. Report skipped repos.
- If the existing plan is invalid against `spec/plan-schema.md`, halt. This
  prompt cannot fix structural plan errors — that requires `init.md`.
- If the user halts at the Phase R2 checkpoint without responding, the run
  ends cleanly. Phase R3 onward only runs after explicit user input
  (or `coverage_gap_scan: false`).

---

## RELATIONSHIP TO OTHER PROMPTS

| File | Relationship |
| --- | --- |
| `init.md` | Authoritative for CONFIGURATION, sub-agent briefs, scaling rules, quality gates, hand-edit zone protocol. This prompt links to it; do not duplicate. |
| `specialists/agents.md` | Invoked unchanged in Phase R4 for `agents`-section writers (verifier mode `agents`). |
| `specialists/technical.md` | Invoked unchanged in Phase R4 for technical-section writers. |
| `specialists/product.md` | Invoked unchanged in Phase R4 for product-section writers. |
| `specialists/verifier.md` | Invoked unchanged in Phase R3. |
| `spec/plan-schema.md` | Authoritative for plan structure. Phase R1 validates against it; Phase R2.4 patches conform to it. Also hosts the § recheck-baseline.yaml SCHEMA read by § DIFF MODE and written at R5.2. |
