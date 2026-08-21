# Task workflow prompt

Copy everything below the line, fill in the TASK field, and paste it as the first
message of a new agent session started in this workspace. Use it for work that
spans more than one file or repo, or that you want reviewed before it lands —
for a one-file change, just make the change.

---

TASK: {one-paragraph description, links (Jira link if there is one), attachments
location, anything else relevant}

HOW YOU CHECK YOUR OWN WORK — these four hold for every step below.

1. GROUNDED MEANS YOU RAN IT. Use every tool you have rather than your memory:
the test, type-check, lint and build commands; git for diffs, blame and history;
a subagent for every step marked INDEPENDENT; the app itself or a browser when
the change is user-visible; a database or API client when the claim is about real
data; docs or web search before assuming how a third-party library behaves.
"I read it and it looks right" is not a check. Local or dev environments only,
read-only outside the repos unless the task says otherwise, never production;
redact tokens and personal data from any output you paste.

2. INDEPENDENT MEANS A SEPARATE DISPATCH — a subagent in a fresh context that has
not seen your reasoning, never a second persona in this same turn. A different
model if you can pick one. A dispatch may read the code repos, and is handed only
the artifacts its step names; it is never given this conversation, PROGRESS.md,
or another dispatch's return — those carry your reasoning, which is the thing its
independence is protecting. Head each saved return with the line
`independence: dispatched — {model or agent id}`. If you cannot dispatch one,
head the self-review `independence: not available — self-review only` and carry
that item as UNVERIFIED rather than as reviewed.

3. EVIDENCE OR IT DID NOT HAPPEN. "This passes", "that is already handled",
"that is out of scope" each carry a command plus the tail of its real output, or
a quoted path:line. With neither, it is a guess — write it down as one. Read
every count off the current state as you write it; never copy one forward.

4. NEVER MAKE A CHECK PASS BY WEAKENING THE CHECK — deleting or skipping a test,
loosening an assertion, widening a type to escape the type checker, swallowing an
exception, hardcoding the value the test expects, or leaving a command out of the
TOOLING record so the gate stops asking for it. That is a failed phase, not a
passed one. If a test genuinely must change because the requirement changed, log
it as a deviation with a one-line why.

SETUP: First look for a folder in wiki-{workspace-name}/tasks/ that is already
this task (same ticket ID or task name). If one exists, use it: read PLAN.md,
PROGRESS.md and REQUIREMENT.md and RESUME from where they left off — do not
start over, do not re-plan approved work, and keep the BASE and TOOLING records
already there rather than taking them again; the pre-existing-failure list is
frozen at task start. Otherwise create
wiki-{workspace-name}/tasks/{nnn}-{task-name}/, kebab-case, ticket ID right
after the number when there is one, where {nnn} is one above the highest number
present (an empty or new tasks/ starts at 001).

Leave the work uncommitted throughout unless I ask for a commit, a branch or a PR.

Open PROGRESS.md with two records, because later steps read them back:
- BASE — `git -C {repo} rev-parse HEAD` and `git -C {repo} status --porcelain`
  for the workspace itself if it is a git repo, and every git repo directly
  under it except wiki-{workspace-name} — not just the ones you expect to
  touch — plus any repo the task or plan names elsewhere, recorded the first
  time it is named and before you edit it. A repo with no commits yet is
  recorded `no BASE — empty repo`. In each repo whose porcelain shows it
  dirty, snapshot that starting state now:
  `git add -A -N && git diff > {task-folder}/phase-0-{repo}.patch &&
  git reset -q`.
- TOOLING — how tests, type checking, linting and the app are actually run.
  Fill it per repo the first time the plan's file list or an edit names that
  repo: find the real commands, do not assume them, and write `none` explicitly
  where one does not exist — the gate only asks for what this record names.
  Run the test command once before your first edit in that repo and record any
  failure by name. A slow suite may be baselined on just the packages the
  localization map names — record `baseline scoped to {paths}`.

UNDERSTAND — write REQUIREMENT.md in the task folder as you go. It is the file
every dispatch below receives as "the requirement": anything not in it does not
exist for your reviewers.
- Open it with the verbatim TASK text and any ticket acceptance criteria,
  quoted; your restatement follows them, never replaces them.
- Read the relevant existing code, configs and conventions first — start at
  wiki-{workspace-name}/AGENTS/index.md, and read
  wiki-{workspace-name}/AGENTS/invariants.md before touching protected areas;
  if the wiki has not been generated, say so and work from the code. If a
  ticket is linked, read it plus its parents and comments.
- LOCALIZE before you plan: where does the change live? Record the files and
  symbols as path:line, their callers and consumers found by actual search, and
  the repos implicated. The plan's phases cite this map.
- Restate the requirement in your own words, with its acceptance criteria and
  what is explicitly OUT of scope.
- List the protected surfaces you must NOT touch (schema, public API
  signatures, auth flows — do not infer scope from omission). Where the task
  deliberately changes one, list it as an in-scope exception with its exact
  bounds, so reviewers do not report a sanctioned change as a violation.
- List every assumption, and keep an OPEN RISKS section current from here on.
- A bug fix reproduces the bug first and pastes the failing output into
  REQUIREMENT.md — never fix a bug you have not seen fail. A
  behavior-preserving change instead names the sites it collapses or the defect
  it removes, as path:line.
- For small ambiguities, choose a reasonable default and state it in
  REQUIREMENT.md; for anything that materially changes design, cost, or
  behavior, stop and ask me.

PLAN: Write PLAN.md. State the chosen approach in two lines, and the strongest
alternative you rejected with the one reason — the review attacks that choice
too. Then numbered phases. A phase is the smallest change with its own runnable
check; split any phase that crosses repos or exceeds five non-test files. Each
phase names:
- what changes;
- which files — including the test files you will add or change;
- the exact command that verifies it, AND what its output must contain to count
  as a pass (a suite printing "0 tests found" is otherwise a pass). The check
  has to come from the requirement, not from the implementation restating
  itself;
- what could break, citing the localization map.

A phase that is deliberately behavior-preserving also names: every existing
test covering that code, the line it will break during IMPLEMENT, and which
named tests that break must turn red — the only proof the moved code is the
code being tested. If no test covers it, add a characterization test as its own
phase first — green on unmodified code, exempt from red-first; the break above
is what proves it bites.

Answer each of these in PLAN.md, one line each — either how it is handled or
"N/A — {reason}":
- invalid input
- empty and first-run state
- concurrency and idempotency
- failure and rollback path
- who is authorized
- untrusted input reaching a query, a shell, a path or a template
- migration or backfill for rows that already exist
- backwards compatibility for existing callers
- how anyone would know this broke in production

Close the plan with two things: a line per acceptance criterion naming the
phase and command that proves it, and a last phase of end-to-end verification —
the exact command or in-app action and what you must observe, exempt from
red-first.

TIER: the plan is LIGHT when the diff will sit in one repo, touch at most 3
non-test files, no protected surface and no dependency manifest, with no
behavior-preserving phase — and none of the concurrency, untrusted-input,
migration or authorization coverage lines carries a real handling (each is
N/A). Anything else is FULL. LIGHT skips the adversarial dispatch below (the
approval STOP is its review) and the per-phase restore patches.

ADVERSARIAL REVIEW (FULL only): one INDEPENDENT dispatch, read-only, given
PLAN.md and REQUIREMENT.md. Its verbatim return goes to
wiki-{workspace-name}/tasks/{task-folder}/review-plan.md, with one PROGRESS.md
line pointing at it.

Brief it to attack, not to approve: ask where the INCONSISTENCY is between the
plan and the requirement, never whether the plan looks sound — the two framings
return different findings. Have it:
- verdict each phase, the approach choice, and the end-to-end phase;
- attack each phase's verify command: what input, state or sequence does it not
  handle, and how could it pass while the change is wrong?
- attack every coverage-line N/A by naming the state that would make it real;
- attack any divergence between the verbatim TASK text and the restatement;
- re-run the caller search for the symbols the localization map names — a
  caller the map misses is a finding;
- where a step could mean two things, draft both readings; the divergence is a
  finding if something in the plan hangs on which reading wins and the state is
  reachable.
Findings are correctness bugs, infeasible steps, security issues, unmet or
contradicted requirements, coverage gaps and out-of-scope changes — a
requirement or coverage line the plan does not handle IS a finding; extra scope
means additions beyond the requirement, never gaps within it. Do NOT flag
style. Cite the plan step for every finding.

Fold every accepted finding into PLAN.md, or reject it with a QUOTED ground —
the path:line, PLAN.md or REQUIREMENT.md line that already handles it.
"Rejected, not a real case" with nothing quoted is not a rejection; record it
under OPEN RISKS. No finding is left unresolved. A fold that alters a phase's
file list, verify command or pass criteria is listed at the STOP as changed
since review.

STOP and present the plan, the tier, the findings and their dispositions, the
assumptions and the open questions. Do not implement until I approve; record my
approval and any changes I request in PROGRESS.md. If a change of mine alters a
phase's file list, verify command or pass criteria, that phase alone goes back
through the adversarial dispatch (return saved as review-plan-2.md, and so on)
and comes back to me with its findings before you build it; wording-only edits
do not. Two such rounds are the budget — after that, remaining disagreement
goes under OPEN RISKS and my explicit go-ahead stands in for further re-review.

IMPLEMENT phase by phase.
- A phase that adds or fixes behavior starts red: write its test from the
  requirement, run it, and paste the red output onto the phase's PROGRESS row
  before you implement — red on a missing import is not red on the assertion.
  A bug fix's repro may serve as that red: copy its command and output tail
  onto the row.
- Make the change. Run THIS phase's verify command and paste the green tail.
  Re-run an earlier phase's check only when this phase touched a file that
  phase named; the full suite's turn is the gate. A command that cannot run in
  this environment records `verification: not available — {reason}` on the row
  and carries the item as UNVERIFIED.
- A behavior-preserving phase, after the change lands: break the planned line,
  confirm the named tests go red, restore the line, and re-run them green —
  that green is the restore proof. Record `broken: {path:line} — restored: yes`
  on the row. A named test still green after two break attempts is recorded on
  the row as a coverage gap — stop retrying. Never end a session with a line
  still broken.
- Append a row to PROGRESS.md: date, phase, verify command + actual output
  tail, and any deviation from the plan with a one-line why. Never rewrite past
  rows. Then, unless the tier is LIGHT, save the restore point in each repo
  this phase touched:
  `git add -A -N && git diff > {task-folder}/phase-{n}-{repo}.patch &&
  git reset -q`.
- A deviation that takes the diff outside LIGHT's bounds escalates the tier
  now: record it, and put the updated plan through the adversarial dispatch
  before the next phase.
- If two attempts at fixing a phase both fail, STOP and report rather than
  trying a third. Restore each touched repo: `git reset --hard {BASE}`, apply
  the newest phase patch (phase-0 at minimum for a repo that started dirty),
  and delete files the failed attempt created; a `no BASE` repo's patch is its
  whole tree. A LIGHT task, having no patches, reports with the tree as-is.

FINAL REVIEW: run `git add -A -N` in each repo BASE names, so untracked files
appear, then diff the working tree against the BASE commits; a `no BASE` repo's
diff is its entire tree. Dispatch INDEPENDENT review:
- CORRECTNESS AND BLAST RADIUS — always. Given the diff, REQUIREMENT.md, the
  TOOLING record and BASE's dirty-file list, but NOT the plan, so it does not
  inherit the plan's blind spots. Brief it:
  - does the diff do what REQUIREMENT.md says, and only that?
  - for each changed function, what input or state makes it wrong — error
    paths, off-by-one, null and empty, ordering and concurrency, leaks?
  - any check weakened (copy rule 4's list into the brief)? any obvious check
    command missing from TOOLING?
  - what else reads or writes what this touches: callers, the other repos,
    schema, public API shape, background jobs, caches, feature flags, and the
    invariants in wiki-{workspace-name}/AGENTS/invariants.md?
  Save the return as review-correctness.md.
- CONFORMANCE — only when the diff touches a protected surface or an in-scope
  exception, or spans more than one repo. Given the diff, PLAN.md and
  REQUIREMENT.md. Hunk by hunk: drift from the plan, out-of-scope changes,
  protected surfaces touched, requirements unmet, debris left behind — the
  plan is evidence of intent, not the standard. Save as review-conformance.md.

Same disposition rules as the adversarial review; a deviation row or a BASE
dirty-file line is also a quotable rejection ground. If a user-visible change
was not yet exercised, run the end-to-end phase now and record what you saw; if
the app cannot run here, write `app verification: not available — {reason}` and
carry it as UNVERIFIED.

Then run the deterministic gate yourself — mechanical checks, not judgment
calls; where a bullet allows a justification, that justification must already
exist on a PROGRESS row:
- wherever TOOLING names a test command and the repo's diff against BASE is
  non-empty, the full suite is green (command plus output tail), or its only
  failures are the ones TOOLING recorded as pre-existing, quoted from that
  record; type checking and linting likewise;
- a failure not in TOOLING is re-run once: if it passes and the diff does not
  touch its file, record it flaky on a PROGRESS row and treat it as
  pre-existing; if it keeps failing, or the diff touches its file, stash the
  work, run that one test at BASE, unstash, and let that result decide whose
  it is — record which;
- the newest green full-suite run may be cited instead of re-run when no edit
  followed it — the PROGRESS rows are the record;
- every file in the diff is in the plan's named file list, has a deviation row
  (a fix row logged after the gate counts), or — for a file you did not edit —
  is quoted from BASE's dirty-file record; your own task folder does not count;
- the diff deletes no assertion and adds no skip / only / xfail / ignore /
  focused-test marker nor leaves one it added, absent a one-line justification
  on its PROGRESS row; code moved unchanged between files is not an addition,
  and a modified assertion is not a deleted one — say so on the row;
- every phase the red-first rule covers has a red row recorded before its green
  one; every behavior-preserving phase records `restored: yes`;
- every PLAN.md coverage line carries a handling or an `N/A — {reason}`, and
  every acceptance criterion names the phase that proved it;
- a user-visible change was exercised with what you saw on its row, or carries
  its `not available` line;
- the tier still fits the actual diff; a diff that outgrew LIGHT without the
  mid-implementation escalation runs the CONFORMANCE dispatch now and records
  the skipped plan review under OPEN RISKS;
- the review returns this tier's path required exist in the task folder, each
  headed by its independence line, and every UNVERIFIED item carries its
  verbatim `not available` line;
- in every repo you changed, the BASE commit is still an ancestor of HEAD
  (`no BASE` repos exempt); if not, STOP and report — history moved under you.

Fix what the dispatches confirmed and whatever the gate itself found red. Each
fix is its own PROGRESS row — red-then-green on the row when it changes
behavior. A fix invalidates the prior green of every repo whose files it
touched; other repos' cited greens stand. Re-run the gate; if the fix changed
code, re-run the CORRECTNESS dispatch on the fix's hunks, and check yourself
that each finding of its previous return is addressed on a fix row. Two fix
rounds are the budget: still red after that, or a third round of findings,
STOP and present the residual list — never reinterpret a bullet to pass it.

Then STOP and summarize: what each dispatch returned including the ones that
found nothing, what was fixed, the residual risk — OPEN RISKS plus every
UNVERIFIED item — what you did NOT check, and any
wiki-{workspace-name}/AGENTS pages whose claims this diff makes stale.
