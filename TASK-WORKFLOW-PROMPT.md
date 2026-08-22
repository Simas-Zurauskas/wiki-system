# Task workflow prompt

Copy everything below the line, fill in the TASK field, and paste it as the first
message of a new agent session started in this workspace. Use it for work that
spans more than one file or repo, or that you want reviewed before it lands —
for a one-file change, just make the change.

---

TASK: {one-paragraph description, links (Jira link if there is one), attachments
location, anything else relevant}

HOW YOU CHECK YOUR OWN WORK — these four rules hold for every step below.

1. GROUNDED MEANS YOU RAN IT. Use every tool you have rather than your memory:
the test, type-check, lint and build commands; git for diffs, blame and history;
a subagent for every step marked INDEPENDENT; the app itself or a browser when
the change is user-visible; a database or API client when the claim is about
real data; docs or web search before assuming how a third-party library
behaves. "I read it and it looks right" is not a check. And SAFETY: local or
dev environments only, never production, and outside the repos and your task
folder change nothing the task did not ask for; redact tokens and personal
data from any output you paste. Anything you install, generate or leave
behind outside a repo is yours to name in the final summary.

2. INDEPENDENT MEANS A SEPARATE DISPATCH — a subagent in a fresh context that
has not seen your reasoning, never a second persona in this same turn. A
different model if you can pick one. A dispatch may read the code repos and
the wiki read-only — never wiki-{workspace-name}/tasks/, which holds your own
records — and is otherwise handed only the artifacts its step names —
records like TOOLING are excerpted for it, and it never sees this
conversation, PROGRESS.md, or another dispatch's return. Head each saved
return `independence: dispatched — {model or agent id}`. A separate OS
process counts as a dispatch — try that before concluding you cannot make
one. If you truly cannot, do the review yourself and head it with rule 3's
not-available line instead.

3. EVIDENCE OR IT DID NOT HAPPEN. "This passes", "that is already handled",
"that is out of scope" each carry a command plus the tail of its real output,
or a quoted path:line. With neither, it is a guess — write it down as one.
Read every count off the current state as you write it; never copy one
forward — except where the gate below expressly lets you cite its own newest
green run. When a mandated check cannot run here — no subagent, no test command,
no runnable app — write `{check}: not available — {reason}` where its evidence
would go and carry the item as UNVERIFIED: the gate accepts that line and the
final summary lists it as residual risk. Never silently skip a check.

4. NEVER MAKE A CHECK PASS BY WEAKENING THE CHECK — deleting or skipping a
test, loosening an assertion, widening a type, swallowing an exception,
hardcoding the value the test expects, or leaving a command out of the TOOLING
record so the gate stops asking for it. That is a failed phase, not a passed
one. If a test genuinely must change because the requirement changed, log it
as a deviation with a one-line why.

SETUP: First look for a folder in wiki-{workspace-name}/tasks/ that is already
this task (same ticket ID or task name). If one exists, use it: read its
PLAN.md and REQUIREMENT.md in full, and from PROGRESS.md the BASE and TOOLING
records plus the last few rows, and RESUME from where they left off — do not
start over or re-plan approved work, and keep the BASE and TOOLING records
already there — the pre-existing-failure list is frozen at task start. The
last PROGRESS row is the last completed step; edits beyond it
(diff against BASE) belong to the interrupted phase — verify or redo that
phase before continuing. Otherwise create
wiki-{workspace-name}/tasks/{nnn}-{task-name}/ — kebab-case, ticket ID right
after the number when there is one, {nnn} one above the highest present (001
for a new tasks/). That folder is {task-folder} below.

Leave the work uncommitted throughout unless I ask for a commit, a branch or a
PR.

Open PROGRESS.md with two records, because later steps read them back:
- BASE — `git -C {repo} rev-parse HEAD` and `git -C {repo} status --porcelain`
  for the workspace itself if it is a git repo and every git repo directly
  under it except wiki-{workspace-name}, plus any repo the task or plan names
  elsewhere, recorded before you edit it. A repo with no commits yet is
  recorded `no BASE — empty repo`. Files already dirty here are not yours —
  this record is what excuses them later.
- TOOLING — how tests, type checking, linting, builds and the app are
  actually run, filled per repo the first time the plan or an edit names it:
  find the real commands, never assume them, and write `none` where one does
  not exist — the gate only asks what this record names. Before your first
  edit there (or before the gate first runs its commands, whichever comes
  first), run those commands once and record every failure by name: this is
  the pre-existing-failure list.

UNDERSTAND — write REQUIREMENT.md in the task folder as you go. It is the
file every dispatch receives as "the requirement": anything not in it does
not exist for your reviewers.
- Open it with the verbatim TASK text and any ticket acceptance criteria,
  quoted; your restatement follows them, never replaces them.
- Read the relevant code, configs and conventions first — start at
  wiki-{workspace-name}/AGENTS/index.md and read
  wiki-{workspace-name}/AGENTS/invariants.md before touching protected areas;
  if the wiki has not been generated, say so and work from the code. Read any
  linked ticket plus its parents and comments.
- LOCALIZE before you plan: where does the change live? Record in
  REQUIREMENT.md the files and symbols as path:line, their callers and
  consumers found by actual search, and the repos implicated — this is the
  localization map the plan's phases cite.
- Restate the requirement in your own words, with its acceptance criteria and
  what is explicitly OUT of scope.
- List the protected surfaces you must NOT touch (schema, public API
  signatures, auth flows — never infer scope from omission). Where the task
  deliberately changes one, list it as an in-scope exception with exact
  bounds, so reviewers do not report a sanctioned change as a violation.
- List every assumption, and keep an OPEN RISKS section current from here on.
- A bug fix reproduces the bug first and pastes the failing output into
  REQUIREMENT.md — never fix a bug you have not seen fail. A
  behavior-preserving change instead names the sites it collapses or the
  defect it removes, as path:line.
- For small ambiguities choose a reasonable default and state it in
  REQUIREMENT.md; for anything that materially changes design, cost or
  behavior, STOP and ask me — the questions in one numbered list, each with
  the option you would take by default, and record my answers in
  REQUIREMENT.md before you plan.

PLAN: Write PLAN.md. State the chosen approach in two lines and the strongest
alternative you rejected with the one reason — the review attacks that choice
too. Then numbered phases. A phase is the smallest change with its own
runnable check; split any phase that crosses repos or exceeds five non-test
files, and order phases so each leaves every earlier phase's check passing,
riskiest first where dependencies allow. Each phase names:
- what changes;
- which files — including the test files you will add or change;
- the exact command that verifies it AND what its output must contain to
  count as a pass (a suite printing "0 tests found" is otherwise a pass). The
  check comes from the requirement, never from the implementation restating
  itself;
- what could break, citing the localization map.

A behavior-preserving phase also names every existing test covering that
code, the site it will break during IMPLEMENT (file and symbol — the exact
line is resolved when the break happens), and which named tests must turn
red — the only proof the moved code is the code being tested. If no test
covers it, add a characterization test as its own phase first — green on
unmodified code, exempt from red-first; the break above is what proves it
bites.

Answer each of these in PLAN.md, one line each — how it is handled, or
"N/A — {reason}":
- invalid input
- empty and first-run state
- concurrency and idempotency
- failure and rollback path, and what this feature does when something it
  calls fails or returns the unexpected — a caller-supplied function, a
  dependency, a lazily-resolved thing, the clock
- who is authorized
- untrusted input reaching a query, a shell, a path or a template
- migration or backfill for rows that already exist
- backwards compatibility for existing callers
- how anyone would know this broke in production

Close the plan with a line per acceptance criterion naming the phase and
command that proves it AND the observation that would appear if the criterion
were violated — a check that cannot fail has not proved it. Then a final
end-to-end phase — the exact command or in-app action and what you must
observe, exempt from red-first.

TIER: the plan is LIGHT when the diff will sit in one repo, touch at most 3
non-test files, no protected surface (an in-scope exception is one — a
sanctioned change to a protected surface is still a change to it) and no
dependency manifest, with no
behavior-preserving phase — and the concurrency, untrusted-input, migration
and authorization coverage lines are all N/A. Anything else is FULL. LIGHT
skips the adversarial dispatch below — the approval STOP is its review, and
the STOP quotes those four N/A lines verbatim so my approval ratifies them.

ADVERSARIAL REVIEW (FULL only): one INDEPENDENT dispatch, read-only, given
PLAN.md and REQUIREMENT.md; its verbatim return goes to
{task-folder}/review-plan.md, with one PROGRESS.md line pointing at it.

Brief it to attack, not to approve: ask where the INCONSISTENCY is between
the plan and the requirement, never whether the plan looks sound — the two
framings return different findings. Have it:
- verdict each phase, the approach choice, the decomposition and its
  ordering, and the end-to-end phase;
- attack each verify command: what input, state or sequence does it not
  handle, and how could it pass while the change is wrong?
- attack every coverage line, N/A or not — name an input, a state, or a
  failure of something the feature calls that its answer does not cover;
- attack any divergence between the verbatim TASK text and the restatement;
- re-run the caller search behind the localization map — a caller it misses
  is a finding;
- where a step could mean two things, draft both readings; the divergence is
  a finding if the plan hangs on which reading wins and the state is
  reachable.
Findings are correctness bugs, infeasible steps, security issues, unmet or
contradicted requirements, coverage gaps and out-of-scope changes — a
requirement or coverage line the plan does not handle IS a finding; extra
scope means additions beyond the requirement, never gaps within it. Do NOT
flag style. Cite the plan step for every finding.

Fold every accepted finding into PLAN.md, or reject it with a QUOTED ground —
the path:line, PLAN.md or REQUIREMENT.md line that already handles it.
"Rejected, not a real case" with nothing quoted is not a rejection; record it
under OPEN RISKS. No finding is left unresolved, and a fold that alters a
phase's file list, verify command or pass criteria is listed at the STOP as
changed since review. A fold that rewrites a phase's approach, or that you
originated rather than took from the review, goes back through the same
one-phase dispatch a change of mine would, before the STOP — inside the same
two-round budget. A fold that only implements a finding's own prescribed
remedy does not: the plan that gets built must be a plan a reviewer has
seen.

STOP and present, decisions first: what you need from me, as a numbered list
of questions each with the answer you would take by default, then the plan,
the tier, the findings and their dispositions, the assumptions and the open
questions. Do not implement until I approve; record
my approval and any changes I request in PROGRESS.md. If a change of mine
alters a phase's file list, verify command or pass criteria, that phase alone
goes back through the adversarial dispatch — given the full updated PLAN.md
and REQUIREMENT.md, briefed to report findings only on the changed phase,
saved as review-plan-2.md, and so on — and returns to me with its findings
before you build it — wording-only
edits do not, a LIGHT plan re-approves at the STOP itself with no dispatch,
and I can waive a round explicitly. Two such rounds are the budget for the
whole task, and the same is true of the fix budget below; after that,
remaining disagreement goes under OPEN RISKS and my go-ahead stands.

IMPLEMENT phase by phase.
- A phase that adds or fixes behavior starts red: write its test from the
  requirement, run it, and paste the red output into PROGRESS.md before you
  implement — red on a missing import is not red on the assertion. A bug
  fix's red may simply point at its repro in REQUIREMENT.md.
- Make the change. Run THIS phase's verify command and paste the green tail.
  Re-run an earlier phase's check only when this phase touched a file that
  phase named — the full suite's turn is the gate.
- A behavior-preserving phase, after the change lands: break the planned
  line, confirm the named tests go red, restore the line, and re-run them
  green — that green is the restore proof. Record
  `broken: {path:line} — restored: yes` on the row. A named test still green
  after two break attempts is recorded as a coverage gap — restore the line,
  still record `restored: yes`, and stop retrying. Never end a session with a
  line still broken.
- Append a row to PROGRESS.md: date, phase, verify command + output tail, and
  any deviation from the plan with a one-line why. Never rewrite past rows.
  A row is a record, not an essay: keep it under ~15 lines and put anything
  longer in a file beside PLAN.md that the row points at.
- An edit or deviation that breaks any LIGHT bound escalates the tier now:
  record it, put the updated plan through the adversarial dispatch, and STOP
  with its findings before the next phase.
- If two attempts at fixing a phase both fail, STOP and report rather than
  trying a third — leave the tree as it is and list on the final row exactly
  which files the failed attempt touched.

FINAL REVIEW: run `git add -A -N` in each repo you changed so untracked files
appear, then diff the working tree against the BASE commits (a `no BASE`
repo's diff is its whole tree); a repo you did not touch is diffed, not
staged. Make no edit while a dispatch you handed a diff to is outstanding —
a review of a diff you have since changed reviewed nothing; if an edit lands
anyway, regenerate the diff and re-dispatch. Dispatch INDEPENDENT review:
- CORRECTNESS AND BLAST RADIUS — always. Given the diff, REQUIREMENT.md, the
  TOOLING record and BASE's dirty-file list, but NOT the plan, so it does not
  inherit the plan's blind spots. Brief it:
  - does the diff do what REQUIREMENT.md says, and only that?
  - for each changed function, what input or state makes it wrong — error
    paths, off-by-one, null and empty, ordering and concurrency, leaks?
  - any check weakened (copy rule 4's list into the brief)? any obvious check
    command missing from TOOLING?
  - what else reads or writes what this touches — callers, the other repos,
    schema, public API shape, background jobs, caches, feature flags, and the
    invariants in wiki-{workspace-name}/AGENTS/invariants.md, if that file
    exists?
  - every guarantee the diff STATES about itself — in a docstring, a release
    note, a doc page, an error message — name the case that would falsify it
    and say whether a test actually falsifies it. Correct-looking code under
    a false sentence is the failure this bullet exists to catch.
  Save the return as review-correctness.md, and each later re-run as
  review-correctness-2.md, -3.md — the gate reads them all.
- CONFORMANCE — only when the diff touches a protected surface or an
  in-scope exception, or spans more than one repo. Given the diff, PLAN.md
  and REQUIREMENT.md. Hunk by hunk: drift from the plan, out-of-scope
  changes, protected surfaces touched, requirements unmet, debris left
  behind — the plan is evidence of intent, not the standard. Save as
  review-conformance.md.

Same acceptance and rejection rules as the adversarial review — an accepted
finding becomes a fix below, never a plan edit, and a deviation row or a BASE
dirty-file line is also a quotable rejection ground. If a user-visible change
was not yet exercised, run the end-to-end phase now and record what you saw.

Then run the deterministic gate yourself — mechanical checks, not judgment
calls; where a bullet allows a justification, that justification must already
exist on a PROGRESS row:
- in every repo whose diff against BASE is non-empty, every command TOOLING
  names is clean — full suite, type check, lint, command plus output tail —
  or its only failures are quoted from the pre-existing-failure list or from
  an earlier flaky row whose file the diff still does not touch. A repo's
  newest green run may be cited instead of re-run when no edit in that repo
  followed it — the PROGRESS rows are the record;
- a failure with no quote is re-run once: if it passes and its file is
  outside the diff, record it flaky on a PROGRESS row and treat it as
  pre-existing; otherwise it is yours — fix it, or carry it to the STOP as
  residual;
- every file in the diff is in the plan's named file list, has a deviation or
  fix row, or — untouched by you — is quoted from BASE's dirty-file record;
  your own task folder does not count;
- absent a justification row, the diff deletes no assertion and adds no
  skip / only / xfail / ignore / focused-test marker nor leaves one it added;
  code moved unchanged is not an addition, and a modified assertion is not a
  deleted one — say so on the row;
- every phase the red-first rule covers has its red recorded before its green
  row; every behavior-preserving phase records `restored: yes`;
- every coverage line carries a handling or an `N/A — {reason}`, and every
  acceptance criterion names the phase that proved it and its violation
  observation;
- a user-visible change was exercised, with what you saw on its row;
- the tier still fits the work; a diff that outgrew LIGHT unescalated runs
  the CONFORMANCE dispatch now and records the skipped plan review under
  OPEN RISKS;
- every review file this tier requires exists in the task folder —
  review-correctness*.md always, review-plan*.md unless LIGHT (a diff the
  previous bullet handled keeps its LIGHT exemption here),
  review-conformance.md when triggered — each headed by its independence
  line, and each final-review return names the diff it read and that diff
  still reproduces, or it is re-run; every UNVERIFIED item carries its
  `not available` line;
- wiki-{workspace-name}/AGENTS pages are unchanged since task start, or every
  change to them is on a PROGRESS row and named at the STOP — a mandated
  check must not be satisfied by editing the thing it checks against;
- in every repo you changed, BASE is still an ancestor of HEAD (`no BASE`
  exempt); if not, STOP and report — history moved under you.

Record the walk itself as a PROGRESS row: each bullet, PASS or the reason,
with the row or quote it rests on. A gate nobody can re-read was not a gate.

Fix what the dispatches confirmed and whatever the gate itself found red —
each fix is its own PROGRESS row, red-then-green on the row when it changes
behavior. A fix invalidates the prior green of every repo it touched; other
repos' greens stand. Re-run the gate; if the fix changed code, re-run the
CORRECTNESS dispatch on the fix's hunks, and check yourself that each finding
of its previous return is addressed on a fix row.

Two fix rounds are the budget FOR THE WHOLE TASK. The count never resets —
not at a STOP, not in a new session, not when I hand a residual back — and a
round is any pass that edits the tree after FINAL REVIEW began, whatever it
edits: code, tests, comments, docstrings, release notes. Carry the count on
the row. Still red after that, or a third round of findings — STOP and
present the residual list, and dispatch no further review. Never reinterpret
a bullet to pass it.

Then STOP and summarize: what each dispatch returned including the ones that
found nothing, what was fixed, the residual risk — OPEN RISKS plus every
UNVERIFIED item — what you did NOT check, anything you left outside the
repos, and any wiki-{workspace-name}/AGENTS pages whose claims this diff
makes stale.

That summary is the end of the task. If I accept it or say nothing, record
DONE as the last PROGRESS row and stop — do not re-run the gate, do not
dispatch again, do not look for more work. If I come back naming something to
fix, that is a new instruction and not a new budget: say on the row that the
budget is spent, change only what I named, re-run the gate over that change,
and present it — no new dispatch unless I ask for one.
