# Changelog

One entry per `VERSION` bump, newest first. **Update this file in the same
commit that bumps `VERSION`** — the `generator_version` recorded in each
project's `plan.yaml` only tells a recheck *that* the generator drifted; this
file is what tells the operator *what* changed between those versions.

Introduced at v10; earlier versions are not chronicled here (see git history).

## v24 — 2026-09-01

**The record stops copying itself.** Same file, same install mechanism; no `init.md`
change. A comparison of the prompt against Matt Pocock's `wayfinder` and its sibling
skills, with the ten-task campaign (`~/dev/ai/twp-sim/`) as arbiter for every claim.
Report at `~/dev/ai/twp-wayfinder-borrows.md`.

**First, the housekeeping this entry also settles.** Commit `f26a4c6` (2026-08-27) changed
`TASK-WORKFLOW-PROMPT.md` by +13/-1 — the `qa/` / `research/` / `drafts/` subfolder block
in SETUP — with `VERSION` still reading 23 and no entry here, against this file's own rule
at the top. That block is kept and is chronicled now; part of the 285 → 364 growth was
unrecorded until this version.

**The measurement that drove it.** v21 consolidated the prompt to 285 lines / 2,844 words
on the owner's line that it "began as ~40 simple lines and must not become a confusing
mess". v22 and v23 added 940 words back, leaving the file at 364 / 3,784 — **larger than
the v20 state v21 was reacting to**. And the campaign's §7 item 22 was still open: whether
`PROGRESS.md` is a log or a handoff, against a measured 12:1 record-to-code ratio on the
*cheapest* task in the set.

The borrow that answers it is `wayfinder`'s one transferable idea — *the map is an index,
not a store; a decision lives in exactly one place and the map only gists it and links*.
It is applied at the two surfaces where the record copies itself:

- **The gate walk becomes `{task-folder}/gate-1.md`** (`gate-2.md` on each re-walk), named
  at the folder root by SETUP alongside the review returns, with one PROGRESS row naming the
  file and the verdict. v23's D8 fix mandated a walk that restates eleven bullets each
  citing a row in the same file, rewritten on every re-gate — measured at 29.5% of run
  01's PROGRESS.md (134 of 455 lines) and 40.1% of run 02's (25,567 B of 63,680 B), the
  two LIGHT runs the report names as *"the prompt's two cheapest runs produced its two
  heaviest records"*. Under pinned v22 the walk was optional and only 3 of 10 runs wrote
  one, so that share is a forecast for the other seven. D8's property is kept intact — the
  walk is still auditable and re-readable — and only its location moves, to the pattern
  the adversarial-review return has used since v18. **`L294-295` is deliberately NOT
  widened**: a justification still lives on a PROGRESS row, because that is what makes the
  gate quotable. The walk is the record of the check, not a justification.
- **The STOP presents an index, not a copy.** Measured: 484,443 B of STOP presentations
  against 13,931 B of replies across the ten runs, 34.8:1; run 10's first STOP spends 97
  of 272 lines restating a 56-line `review-plan.md` in the same folder. Three things stay
  quoted in full — a LIGHT plan's four N/A coverage lines (v23 added that so the tier is
  not self-certified), anything changed since review, and any AGENTS page changed.

**The unit defect, which is not a borrow and which the campaign missed.** `L248-249`
bounded a PROGRESS row at *"~15 lines"*. Nine of ten runs recorded in markdown tables,
where a row is **one physical line of any length**: measured across all ten
`PROGRESS.md` files, 743 rows, median 380 characters, maximum 2,867 — **every one
compliant, with fourteen lines to spare**. `attrs` is 67,785 bytes in 111 lines. The bound
is now **~300 characters of the agent's own prose, with pasted command output excluded** —
the exclusion matters: a naive cap would evict gate evidence from the place the gate reads
it. (Re-measured on review: characters inside backtick spans in table rows are **31.8%**,
not the 62% first claimed. The bound holds regardless — median prose-only characters per
row is **198**, while **41.1%** of the 811 rows breach ~300, so it bites the top two
fifths and leaves a typical row alone.) A justification the gate quotes is compressed onto
the row, never spilled to a file — otherwise the bound would defeat `L294-295`. The bound also moves out of the IMPLEMENT bullet list, where it governed only phase
rows, to cover every row the prompt asks for, and it settles `L150`'s *"one line each"*
(one run wrote 1,354 characters on one).

Also in this version:

- **`in-scope exception` is collapsed into `protected surface`** at all three sites. One
  vocabulary, not two: a sanctioned change is still a change, so it neither reports as a
  violation nor escapes the checks the surface earns. −3 lines and it closes the tier
  loophole at the root rather than under v23's parenthetical. The CONFORMANCE trigger is
  unchanged in coverage — v23 already read "a protected surface or an in-scope exception";
  only the wording tightened.
- **The AGENTS-pages prohibition moves into rule 1's SAFETY sentence.** UNDERSTAND sends
  the agent to those pages 90 lines in; the only prohibition arrived 226 lines later inside
  a checklist that opens "mechanical checks, not judgment calls". Rule 1 already covered it
  ("outside the repos and your task folder change nothing the task did not ask for"); this
  makes the implication explicit and shortens the gate bullet to a pointer. D4's ownership
  question — draft-never-apply — stays open, as REPORT §7 item 16 asks.
- **The gate is a function of the diff, not of the session.** Run 02 walked it five times
  on a byte-identical diff, proving identity by sha256 each time; rounds 3, 4 and 5 changed
  no code. A walk whose diff hashes the same now stands.
- **`grilling`'s fact rule**, one clause at the only place the prompt asks: *a question you
  could settle by reading the code, the history or the ticket is not a question — settle
  it.* Run 01 asked four questions on a 38-line LIGHT diff and every answer was a
  non-decision.
- **The interrupted-phase risk**, one clause on the *ordering* rule rather than a per-phase
  bullet: no phase may be left as the last completed one with a caller-visible surface that
  does nothing. Real (httprouter's `review-plan.md` F7 found an exported policy field
  callers can set and that is silently ignored) and it slips through the existing ordering
  rule, since an inert field leaves every earlier check passing. **Deliberately not a
  per-phase bullet** — v23 refused that shape outright because it multiplies by phase
  count.
- The *"a check that cannot fail has not proved it"* tautology is stated once and cited
  once, instead of twice. The third statement of it — v23's guarantee-falsification bullet
  in the CORRECTNESS brief — is **left alone**: it is the fix for the only two HIGH defects
  that reached delivered code.

**Refused, with the ground.** `to-tickets`' **expand–contract** for wide refactors: no task
in ten was one, the largest diff is 8 mostly-additive files, and the widest mechanical
fan-out fits inside the existing five-file cap — a clause for a case the corpus never
produced is the "mechanism nobody would use" this project already rejects. **Recorded here
as the known gap it is: the prompt mandates that every phase leave earlier checks passing,
and that is not satisfiable for a genuinely wide mechanical refactor.** Also refused:
disclosing the FULL-only lane behind a pointer (the prompt is a copy-paste artifact and
`L104-106` contemplates a workspace with no generated wiki, so a required second file
cannot exist); RESUME reading `PROGRESS.md` in full (files reach 79,716 B and a Read
truncates); a per-phase deliverable bullet; `grilling`'s round-splitting *"ask it alone and
wait"* (it adds the only uncapped human loop, on the axis §4 measures as a cost driver);
and naming each phase (8 of 10 plans already do it unprompted).

**What this version does not touch, and it is the larger number.** Dispatch is the dominant
cost — ~13,000 s launched campaign-wide, ~50% of the two worst tasks, median ~460 s, poorly
correlated with diff size. Everything above edits what gets written down, and the whole
record prize is perhaps 2,000 s. The three levers that would move the real cost are
unaddressed and remain open: **what LIGHT buys** (LIGHT ran at 25.5–33.6 s per changed line
against FULL's 3.8–5.9 — it discounts one line item of eleven), **D5** (the CORRECTNESS
dispatch's plan-blindness defeated by a 40,165-byte `REQUIREMENT.md`; the excerpt mechanism
already exists in the file), and **D7/D11/D12** from REPORT §7. D5 is the one to do next.

**Fixes applied before commit, from an assessment of this version against v23**
(`~/dev/ai/twp-v24-vs-v23-assessment.md`), at no net line cost: the gate walk's filing
contradicted SETUP's own "everything else goes in a subfolder" rule, so SETUP now names it;
the row bound could have spilled a justification the gate demands on a row, now forbidden;
the AGENTS clause asked for the *page* quoted in full at the plan-approval STOP, which
precedes IMPLEMENT — it now asks for the *diff*, rule 1 says "the next STOP", and the final
summary carries it; the inert-surface rule read as both a prohibition and a documentation
duty, now stated as both explicitly; the acceptance-criteria line's "same bar" back-reference
is self-contained again; three bullets lost their continuation indent and two lines were
left unreflowed (one at 84 characters, past the file's 82 band), both restored; the eight
markdown-bold spans — in a file that had **zero** through v23, four of them wrapping across
a line break — are gone, leaving ALL-CAPS as the single emphasis device, with
`COUNT CHARACTERS, NOT LINES` promoted to it.

Net: 364 → 385 lines, 3,784 → 4,097 words. **This version adds 21 lines**, against a
consolidation that removed 28 — three of its eight changes are new rules rather than
relocations, and that is the honest cost. Anything further should be paid for by deletion.

## v23 — 2026-08-22

**First behavioural evidence: ten real tasks, fifteen public repos.** Same file, same
install mechanism; no `init.md` change. v18–v22 were desk reviews. This version is the
first driven by *running* the prompt — a ten-task simulation campaign
(`~/dev/ai/twp-sim/`, report at `twp-sim/REPORT.md`) executing the pinned v22 against
cloned public repositories, from a two-line off-by-one in itsdangerous to a cross-repo
feature over flask+werkzeug+click, with strict actor separation (a runner that never
played the human, a separate operator agent holding only a persona brief, fresh contexts
that had to rehydrate from disk), planted ground truth with an answer key, keyed and
blind auditors, and an adversarial verifier that re-opened all 103 findings: 30
CONFIRMED, 53 PARTIAL, 20 REFUTED → 37 SKILL_DEFECT, 37 RUN_FIDELITY, 19 NOT_A_DEFECT,
10 HARNESS_ARTIFACT, collapsing to 19 distinct defects.

Verdict: the prompt delivered a working uncommitted diff on the correct BASE in all ten
tasks and nothing was ever committed. Its structural failure was that **it did not know
how to stop**.

The P0, and the reason for this version:

- **The fix budget had no scope and no unit.** v19 capped fix rounds at two; the
  campaign proved the cap binds only inside one STOP-to-STOP cycle. All three tasks that
  reached the ceiling with a human turn after it crossed it — legally, and in writing.
  Tenacity ran **six** CORRECTNESS dispatches against a ceiling of three (3,821s of
  review wall-clock; its last round changed no code path); requests ran four. Four runs
  independently invented the same "no code changed, no round consumed" carve-out. The
  budget is now **for the whole task**, never resets "not at a STOP, not in a new
  session, not when I hand a residual back", and **a round is any pass that edits the
  tree after FINAL REVIEW began, whatever it edits**. The count is carried on the row.
- **The prompt had no terminal state.** It ended at the summary and said nothing about
  what a human reply does, so runs treated any reply as a reopening. Acceptance or
  silence now means record DONE and stop — no re-gate, no further dispatch. A named
  residual is "a new instruction and not a new budget": one bounded pass over what was
  named, no new dispatch unless asked. (The campaign's own consolidated input proposed
  that both budgets "start fresh" on a reply; that is precisely the reading that produced
  the breaches, and it was rejected.)

Other confirmed defects fixed here, each found by two or more independent auditors:

- **Plan re-review triggered on WHO changed the plan, not WHAT changed** (D1 — 6
  rediscoveries across 4 runs, the report's highest-severity defect). A *human* edit to a
  phase's file list, verify command or pass criteria bought a full re-dispatch; the
  agent's own fold of the same three properties bought only a "changed since review"
  line at the STOP. So the widest possible edit — the agent rewriting the very approach
  the adversarial dispatch had just condemned as unsound — got the cheapest treatment,
  and on a FULL plan the thing that actually got built had never been reviewed. Run 10 is
  the confirmed case: `review-plan.md:12` verdicts the approach unsound, `PLAN.md:495`
  records the rewrite, every later HIGH lived in the fold-rewritten phase, and the human
  had requested nothing. Now: a fold that rewrites a phase's approach, or that you
  originated rather than took from the review, goes back through the same one-phase
  dispatch a human change would — **inside the same two-round budget**, which is what
  stops it recursing fold → dispatch → fold. A fold that merely implements a finding's
  own prescribed remedy does not.
- **Dispatch isolation was unenforceable** (2 auditors, both CONFIRMED): rule 2 granted
  dispatches the wiki read-only, and SETUP puts the task folder — PLAN.md, PROGRESS.md,
  every prior review — inside the wiki. Now excluded explicitly. Four briefs in one run
  had hand-patched the hole while handing the dispatch an absolute path into that same
  directory.
- **A saved review only had to exist, not to match what shipped** (2 auditors): the gate
  now requires each final-review return to name the diff it read and that diff to still
  reproduce, or be re-run; and no edit may land while a dispatch holding your diff is
  outstanding — if one does, regenerate the diff and re-dispatch. One run certified a
  conformance review against a patch 205 insertions behind the tree that shipped.
- **The invariants file was a blind spot** (keyed + blind on the same run): AGENTS pages
  sit outside BASE, outside the diff and outside every gate bullet, so the mandated
  invariants check could be satisfied by editing the thing it checks against. A gate
  bullet now requires them unchanged since task start, or every change on a row.
- **The gate left no trace** (CONFIRMED): its non-command bullets are now recorded as a
  PROGRESS row — "a gate nobody can re-read was not a gate".
- **Two HIGH defects escaped into delivered code**, both the same species: a false
  sentence in shipped docs over correct-looking code (click's `--help-json` "stdout is
  one JSON object", falsified by a group callback that echoes; tenacity's release note
  promising *N* retries per window, measured at 3 in a 1.0s window against
  `max_retries=2` — nine dispatches never raised it). The CORRECTNESS brief now asks,
  for every guarantee the diff *states* about itself, for the case that would falsify it
  and whether a test does.
- Smaller, one clause each: the post-fix re-dispatch has a filename and the gate globs
  `review-correctness*.md`; rule 3's never-copy-forward no longer contradicts the gate's
  own cite-the-newest-green permission; `git add -A -N` is scoped to repos you changed;
  a PROGRESS row is capped (~15 lines) and RESUME reads PLAN/REQUIREMENT in full but only
  the tail of PROGRESS (one run wrote 808 record lines for a 109-line diff); an in-scope
  exception is stated to *be* a protected surface; UNDERSTAND's stop-and-ask has a
  presentation and record contract; the STOP presents decisions first; rule 1 gains a
  concept of out-of-repo footprint; and rule 2 now names the separate-OS-process route
  before the cannot-dispatch escape.

**Edge-case and error-path planning** — a separate evidence pass over the ten plans and
their delivered diffs (five analysts, graded plan-vs-diff as a design review, not as
checklist compliance; mean 4.3/5, nine of ten COMPLETE). The finding was not that plans
are happy-path sketches — where the checklist names a category, the plans produce
concrete tested handling. It was that completeness held only inside the domain the agent
had already imagined, and two classes escaped in all ten tasks:

- **Nothing asked what the feature does when something IT CALLS fails.** No plan in ten
  considered a caller-supplied function that throws, a dependency that raises, a
  lazily-resolved subcommand that fails to import (turning click's `--help-json` into a
  traceback on the exact `jq` pipeline the ticket existed for), or a suppressed redirect
  falling through to 405 instead of the NotFound handler the requesting team asked for.
  The cause was two words: "failure and rollback path" reads as *your* rollback, so five
  of nine tasks put `git checkout` there. That line now also asks what the feature does
  when something it calls fails or returns the unexpected — a caller-supplied function, a
  dependency, a lazily-resolved thing, the clock.
- **Acceptance criteria were positive-only.** "The phase and command that proves it" is
  satisfied by a check that cannot fail — which is exactly how both HIGH defects reached
  delivered code (a false self-claim over correct-looking code, one of them covered by a
  test whose group body was a bare `pass`). Each criterion now also names the observation
  that would appear if it were violated, and the gate reads that back.
- The adversarial review attacked only coverage-line **N/As**; the corpus shows a
  concrete-but-finite *handling* passing a genuinely independent dispatch and two further
  rounds. It now attacks every coverage line, N/A or not, naming an input, a state, or a
  failure of something the feature calls that the answer does not cover. Net zero length.

Every miss in that corpus was a *value*, not a category — `max_age=0`, `name=123`,
`per_seconds` as NaN/`True`/`"60"`/`memoryview(b"60")`. The candidate edit that would
force each coverage line to name a triggering value and its origin was costed (+4 prompt
lines, ~9 per plan) and deliberately deferred: it catches `max_age=0` but not NaN, and
the owner's standing constraint is effectiveness without bloat. A per-phase failure-mode
demand was refused outright — plans run 5-8 phases, so it multiplies by phase count and
lands one answer in six places.

Deliberately NOT changed, pending design work the report says not to rush: making plan
re-review trigger on *what* changed rather than *who* changed it (the highest-severity
defect, D1 — its fix must not recurse fold → dispatch → fold); excerpting REQUIREMENT.md
so the CORRECTNESS dispatch's plan-blindness is real (4 auditors found REQUIREMENT.md
defeats it); making TIER risk-aware; and the proportionality question of whether
PROGRESS.md is a log or a handoff.

What held under stress, and must not be cut: reproduce-before-plan (a run pasted a red
whose traceback still contained the unfixed source), rule 4 (a run fixed broken code
rather than delete the tests that caught it, citing the rule by name), SETUP/RESUME (a
run was falsely told "nothing has been done yet", detected the contradiction from disk in
seconds, and refused to re-plan approved work), and the independence rule — told falsely
that dispatch was available, six runs found a legitimate out-of-process route and three
wrote the honest `not available` line. **None faked a dispatch.**

## v22 — 2026-08-21

**Final-check closure on the consolidated prompt.** A targeted three-checker
pass over v21 (contradiction/closure sweep, literal execution walk of both
tiers, and a lost-protection diff against v20), findings adversarially
verified, scored 4/5 on all three with no HIGH findings. Every confirmed item
is fixed here — each a one-clause edit:

- Three protections the v21 consolidation dropped by accident are restored:
  the dispatches' read-only repo/wiki access grant in rule 2 (the review
  briefs still require code search — without the grant, rule 2's
  "handed only the artifacts its step names" read as forbidding it), the
  cite-a-prior-green mechanism in gate bullet 1 (which "other repos' greens
  stand" in the fix round silently depended on), and the flaky-row citation's
  file-still-outside-the-diff guard.
- Gate closure: a diff that outgrew LIGHT and was handled by the escalation
  bullet keeps its LIGHT exemption in the review-files bullet (the two
  bullets otherwise pointed opposite ways); the coverage-gap branch of
  break-it now restores the line and records `restored: yes` (the gate
  demanded it unconditionally); the justification-row qualifier is
  front-loaded so it unambiguously covers assertion deletions, matching rule
  4's sanctioned-change escape; the pre-existing-failure baseline also runs
  before the gate first exercises a never-edited repo; TOOLING covers builds,
  matching rule 1's tool list; the CORRECTNESS brief's invariants item is
  conditional on the wiki existing, mirroring UNDERSTAND's fallback.
- Execution-walk fixes: RESUME states the mid-phase rule (last PROGRESS row =
  last completed step; edits beyond it belong to the interrupted phase —
  verify or redo before continuing) and the pre-existing-failure-list freeze
  is back; a behavior-preserving phase plans its break as file + symbol with
  the exact line resolved at break time (the planned line's address does not
  exist until the code moves); the phase-scoped re-review's inputs are
  stated (full updated PLAN.md + REQUIREMENT.md, findings scoped to the
  changed phase).

## v21 — 2026-08-21

**Consolidation: the accreted machinery is removed rather than patched
further.** Same file, same install mechanism; no `init.md` change. The fourth
fresh-context review round (on v20) showed the pattern clearly: cost, logic,
verification-economics and planning lenses all reached 4/5, while the two
lenses still at 3 — gate satisfiability and over-engineering — were stuck on
the same clusters of edge-case machinery that v18–v20 kept patching. The owner
also drew the line explicitly: the prompt began as ~40 simple lines and must
not become a confusing mess. So this version deletes the machinery that bred
the defects instead of closing its seams again (~50 lines and ~20% of the
words against v20), while keeping every loop bound, the tier, and all of the
planning strength.

Removed outright:

- **The patch/restore apparatus** — phase-0 dirty snapshots, per-phase
  `phase-{n}-{repo}.patch` files, the `reset --hard` + re-apply recipes, the
  escalation-time snapshot, and every `no BASE`/dirty/LIGHT branch they
  spawned. The two-failed-attempts rule now STOPs with the tree as-is and
  lists exactly which files the failed attempt touched: a human is taking
  over at that point anyway, and four review rounds in a row found new
  mechanical defects in the self-restore recipes (stash breaking on
  intent-to-add entries, `checkout -- .` unable to undo a patch's new files,
  ordering bugs between patch-apply and untracked cleanup).
- **The at-BASE stash adjudication dance** for ambiguous test failures. The
  simple rule stands: an unexplained failure is re-run once; passing with its
  file outside the diff means flaky/pre-existing; anything else is yours —
  fix it or carry it to the STOP as residual. The elaborate arbitration
  served a rare event and was found mechanically broken in different ways in
  two consecutive rounds.
- **Scoped baselines.** The baseline is the full test/type-check/lint run per
  touched repo again; scoping saved minutes but created failures the gate had
  no clause for (a trap two lenses confirmed independently).
- **Four of the five restatements of the not-available/UNVERIFIED mechanic.**
  Rule 3 now defines it once, generally — `{check}: not available — {reason}`
  wherever the evidence would go, item carried as UNVERIFIED, accepted by the
  gate, listed as residual risk — and every site (independence, red-first in
  a `none`-test repo, app verification) just uses it. This also closes v20's
  "only one narrow producer" finding: any unrunnable check now has the
  escape, not just the enumerated ones.

Kept deliberately, with the small confirmed fixes from round four: every loop
cap and fail branch, the LIGHT/FULL tier (escalation now keyed to any LIGHT
bound broken by an edit or deviation — "the diff" was a plan-property test a
literal executor could not run mid-implementation), red-first with the repro
allowed to stand as its red by pointer (copying it forward collided with rule
3), the behavior-preserving break-it (unique evidence, capped, named tests
only), one plan-blind CORRECTNESS dispatch always with CONFORMANCE on
triggers, the deterministic gate (bullets shortened back to mechanical
one-liners), and the full planning apparatus — verbatim TASK text, the
localization map, acceptance-criterion mapping, the attack-framed brief which
now also verdicts the decomposition and its ordering.

Net: 313 → ~260 lines against v20, every remaining sentence either an
instruction or the one record it produces, and no clause whose only job is to
patch another clause.

## v20 — 2026-08-21

**Third verified pass over the installed task workflow prompt: the seams the
v19 mechanics opened, closed.** Same file, same install mechanism; no `init.md`
change. The same six-lens cold-read + adversarial-verifier campaign, re-run on
v19 by fresh contexts, confirmed the structure (cost and verification-economics
lenses reached 4/5; every loop bounded) and surfaced narrow defects mostly in
the machinery v19 itself added:

- **Baseline covers type-check and lint too** — the gate demanded them clean
  or "recorded as pre-existing", but SETUP only ever baselined the test
  command, so any repo with ordinary pre-existing lint debt failed the gate.
  Baselining scoped to the localization map's packages is now the sanctioned
  default (full suite optional), and the gate quotes a `baseline scoped` repo
  at that same scope — previously the scoping allowance produced failures the
  gate had no clause for.
- **The at-BASE attribution recipe is now mechanically correct**: `git reset
  -q` first (intent-to-add entries break `git stash`), `git stash -u` (plain
  stash strands untracked files), re-apply phase-0 where the repo started
  dirty (else pre-existing-dirt failures pass clean at HEAD and misattribute
  to the task), batch all unexplained failures into one stash cycle, a test
  absent at BASE is the task's by definition, and a `no BASE` repo skips the
  ritual — every failure there is the task's. A recorded flaky row is now
  quotable at the gate re-run (before, a known flake re-failing after a fix
  round re-entered triage every round).
- **Red-first in a `none`-test repo** records `red: not available — no test
  command` and carries UNVERIFIED, mirroring the app escape; the gate's
  red-row bullet accepts that line.
- **Mid-flight LIGHT escalation** now snapshots a restore point first (the
  two-strike `reset --hard` path would otherwise destroy the completed LIGHT
  phases, which saved no patches) and returns to the human with the
  dispatch's findings instead of silently resuming — the approval contract
  ("do not implement until I approve") holds through escalation.
- Consistency: records handed to dispatches are excerpts, never PROGRESS.md
  itself (rule 2's ban and the CORRECTNESS input list no longer collide);
  final-review dispositions say explicitly that an accepted finding becomes a
  fix row, never a post-hoc plan edit; `{task-folder}` is defined once at
  SETUP and used uniformly; the localization map and pre-existing-failure
  list are named at their producers; the garbled tier-returns bullet is
  rewritten as an explicit per-tier file list; the LIGHT restore clause no
  longer denies the phase-0 patch dirty-start repos own; a LIGHT plan's STOP
  quotes the four tier-gating N/A lines verbatim so approval ratifies them
  (the tier was otherwise self-certified by the same agent it exempts from
  review); a human plan change on a LIGHT plan is re-approved at the STOP
  itself; the human may waive a re-review round explicitly.
- Planning: phases carry an ordering rule — each leaves every earlier phase's
  check passing, riskiest first where dependencies allow.

Deliberately not adopted, with the verifiers' agreement: per-phase commits
(uncommitted-throughout is an owner contract), loosening the break-it proof on
behavior-preserving phases (unique coverage evidence, already capped and
scoped to named tests), widening LIGHT (its narrowness is the protection), and
dropping CONFORMANCE's multi-repo trigger.

## v19 — 2026-08-21

**Second adversarially-verified pass over the installed task workflow prompt.**
Same file, same install mechanism; no `init.md` change. A fresh six-lens
cold-read of v18 (cost simulation, gate satisfiability, logic, planning,
over-engineering, verification economics), with every finding then challenged
by an adversarial verifier that had to refute it against the file, confirmed
v18's structure and left narrower defects — all fixed here.

Satisfiability and logic:

- The aggregate before/after **test-count match is gone** (three lenses
  independently confirmed it false-fails by construction: the mandated
  characterization phase, or any red-first phase, legitimately adds tests
  between plan time and the check). The behavior-preserving proof is now
  purely the named-tests red→restored-green cycle; deletion is still caught by
  the assertion/marker grep bullet.
- The fix instruction now covers **failures the gate itself finds**, not only
  dispatch findings — previously a trivially fixable red bullet had no
  sanctioned fix path and dead-ended in a STOP.
- An **escalated LIGHT task** owes review-correctness.md and (now)
  review-conformance.md; the skipped plan review is recorded under OPEN RISKS,
  never retro-demanded — and a deviation that outgrows LIGHT mid-IMPLEMENT
  escalates immediately, putting the updated plan through the adversarial
  dispatch before the next phase instead of discovering it at the gate.
- Attribution of a suite failure not in TOOLING is now decided by evidence,
  not file-touch heuristics alone: re-run once; still failing or in a touched
  file → stash the work, run that one test at BASE, and let that result decide
  (fixes the branch that declared a passing flaky test "yours" merely because
  the diff touched its file).
- The repro-as-red shortcut copies the repro onto the phase's PROGRESS row, so
  the gate's red-row check reads the place the evidence actually lands; a
  not-runnable phase command records `verification: not available` on its row
  (the escape existed only in FINAL REVIEW before); the residual-risk clause
  moved out of the gate (the summary it referenced does not exist at gate
  time); the marker bullet is scoped to markers the diff added; a dirty-at-BASE
  quote excuses only files the task did not edit; the cite-last-run condition
  is decidable (PROGRESS rows, not `git status`, which is never clean here).
- Restore mechanics are real in every state: a phase-0 patch snapshots
  pre-existing dirt at SETUP, the two-strike restore names its commands, a
  `no BASE` repo's patch is its whole tree, and BASE gains lazy extension for
  a task repo living outside the workspace root (previously invisible to the
  final diff entirely).

Cost (verified remainders from the v18 pass):

- A gate-round fix invalidates only the repos it touched; other repos' cited
  greens stand — previously one one-line fix re-ran every repo's suite.
- The plan-negotiation loop (human changes → re-dispatch → re-present) is
  capped at two rounds, mirroring every other loop bound in the file.
- LIGHT also skips per-phase restore patches, and a slow suite may be
  baselined on the packages the localization map names, recorded as scoped.
- The fix-round CORRECTNESS re-dispatch no longer receives its previous
  findings list (rule-2 contamination that converted a fresh look into
  checklist confirmation); the orchestrator checks finding-by-finding
  disposition itself, mechanically.

Planning (confirmed gaps closed):

- REQUIREMENT.md opens with the **verbatim TASK text and quoted acceptance
  criteria** — previously reviewers could only ever see the agent's
  restatement, making restatement errors structurally unreviewable; the
  adversarial brief attacks divergence between the two.
- The plan closes with an **acceptance-criterion → proving-phase map**, and a
  gate bullet reads it.
- The adversarial dispatch re-runs the **caller search behind the localization
  map** — the map every blast-radius claim cites was previously verified by
  nobody.
- The tier gains a risk clause: real handling on the concurrency,
  untrusted-input, migration or authorization coverage lines forces FULL
  regardless of diff size.
- Folds that alter a phase's file list, verify command or pass criteria are
  flagged "changed since review" at the STOP; phase split threshold is a
  number (five non-test files), not "a handful".

Craft: the adversarial brief and CORRECTNESS brief are itemized (they were
single multi-obligation sentences), the monolithic first gate bullet is three
bullets (suite green / attribution / reuse), and duplicated rationale tails
were trimmed.

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
