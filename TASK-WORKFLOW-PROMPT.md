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
"I read it and it looks right" is not a check.

2. INDEPENDENT MEANS A SEPARATE DISPATCH — a subagent in a fresh context that has
not seen your reasoning, never a second persona in this same turn. A different
model if you can pick one. A dispatch may read the code repos, and is handed only
the artifacts its step names; it is never given this conversation, PROGRESS.md,
or another dispatch's return — those carry your reasoning, which is the thing its
independence is protecting. If you cannot dispatch one, write this line verbatim:
`independence: not available — self-review only`, and carry that item as
UNVERIFIED rather than as reviewed.

3. EVIDENCE OR IT DID NOT HAPPEN. "This passes", "that is already handled",
"that is out of scope" each carry a command plus the tail of its real output, or
a quoted path:line. With neither, it is a guess — write it down as one. Read
every count off the current state as you write it; never copy one forward.

4. NEVER MAKE A CHECK PASS BY WEAKENING THE CHECK — deleting or skipping a test,
loosening an assertion, widening a type to escape the type checker, swallowing an
exception, hardcoding the value the test expects, or leaving a command out of the
TOOLING record so the gate stops asking for it. That is a failed phase, not a
passed one. The gate greps for the first two; the rest are in the CORRECTNESS
dispatch's brief. If a test genuinely must change because the requirement
changed, log it as a deviation with a one-line why.

SETUP: First look for a folder in wiki-{workspace-name}/tasks/ that is already
this task (same ticket ID or task name). If one exists, use it: read PLAN.md and
PROGRESS.md and RESUME from where they left off — do not start over, do not
re-plan approved work, and keep the BASE record already there rather than taking
it again. Otherwise take one above the highest number present — if the highest is
007, yours is wiki-{workspace-name}/tasks/008-{task-name}/, kebab-case, ticket ID
first if there is one. Create tasks/ if it does not exist. The folder holds
PLAN.md and PROGRESS.md; research findings and the verbatim return of every review
dispatch are saved as md files beside them.

Leave the work uncommitted throughout unless I ask for a commit, a branch or a PR.

Open PROGRESS.md with two records, because later steps read them back:
- BASE — `git -C {repo} rev-parse HEAD` and `git -C {repo} status --porcelain`
  for every git repo directly under this workspace except wiki-{workspace-name},
  not just the ones you expect to touch: a repo missing here is a change nobody
  reviews, and a repo already dirty now will show up in your final diff as though
  it were yours. A repo with no commits yet is recorded `no BASE — empty repo`.
- TOOLING — how tests, type checking, linting and the app are actually run, per
  repo. Find the real commands, do not assume them, and write `none` explicitly
  where one does not exist: the gate only asks for what this record names. Run the
  test command once on untouched code and record any failure by name, so a
  pre-existing failure is never mistaken for one of yours.

UNDERSTAND: Read the relevant existing code, configs, and conventions first
(start at wiki-{workspace-name}/AGENTS/index.md, and read
wiki-{workspace-name}/AGENTS/invariants.md before touching protected areas; if
the wiki has not been generated, say so and work from the code). If a ticket is
linked, read it plus its parents and comments. Restate the requirement in your own
words, including what is explicitly OUT of scope, and list the protected surfaces
you must NOT touch (schema, public API signatures, auth flows — do not infer scope
from omission). Where the task deliberately changes one of those, list it as an
explicit in-scope exception with its exact bounds, so the dispatches do not report
a sanctioned change as a violation. List every assumption. For small ambiguities,
choose a reasonable default and state it; for anything that materially changes
design, cost, or behavior, stop and ask me.

Then show the gap you are closing, where there is one, before you plan. A bug fix
reproduces it and pastes the failing output into PROGRESS.md — never fix a bug you
have not seen fail. New behavior shows that the behavior is absent today. A
behavior-preserving change instead names the sites it collapses or the defect it
removes, as path:line for each.

PLAN: Write the implementation plan to PLAN.md, split into numbered phases. Each
phase names:
- what changes;
- which files — including the test files you will add or change;
- the exact command that verifies it, AND what its output must contain to count as
  a pass (a suite printing "0 tests found" is otherwise a pass). The check has to
  come from the requirement, not from the implementation restating itself;
- the line it will break during IMPLEMENT to prove that check can go red. A check
  that cannot be made to fail is not verifying anything, and red on a missing
  import is not red on the assertion;
- what could break.

A phase without a runnable check is not a phase. A phase that is deliberately
behavior-preserving names every existing test covering that code — all of them
must go red when the line breaks — and carries the test count before and after,
which must match. If no existing test covers it, say so and add a characterization
test as its own phase first, green on unmodified code.

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

End the plan with an explicit end-to-end verification step.

ADVERSARIAL REVIEW: one INDEPENDENT dispatch, read-only, given PLAN.md, the
requirement and the protected-surfaces list. Its verbatim return goes to
wiki-{workspace-name}/tasks/{task-folder}/review-plan.md, with one PROGRESS.md
line pointing at it plus its independence line.

Brief it to attack, not to approve: ask where the INCONSISTENCY is between the
plan and the requirement, never whether the plan looks sound — the two framings
return different findings. Go phase by phase, one verdict each, then roll up.
Attack each phase's verify command specifically: what input, state or sequence
does it not handle, and how could it pass while the change is wrong? Where a step
could mean two things, draft both readings; the divergence is the finding. A
constructed case counts only if the state is reachable and something in the plan
hangs on which reading wins. Flag ONLY correctness bugs or infeasible steps,
security issues, unmet or contradicted requirements, and out-of-scope changes;
do NOT flag style or propose extra scope. Cite the plan step for every finding.

Fold every accepted finding into PLAN.md, or reject it with a QUOTED ground — the
path:line that already handles it, or the plan line that already says it.
"Rejected, not a real case" with nothing quoted is not a rejection; record it as
an open risk. No finding is left unresolved.

STOP and present the plan, the findings and their dispositions, the assumptions
and the open questions. Do not implement until I approve. Record my approval and
any changes I request in PROGRESS.md; if a change of mine materially rewrites a
phase, that phase goes back through the adversarial dispatch before you build it.

IMPLEMENT phase by phase.
- Start every phase red and paste the red output into PROGRESS.md before you
  implement — a check that has never been seen to fail is not evidence. For a
  phase that adds behavior, red is the new test written from the requirement.
- Then make the change. Then break the line the plan named, confirm every test it
  named goes red, and put the line back — for a behavior-preserving phase this is
  the only proof the moved code is the code being tested, so it happens AFTER the
  change lands, not before. Confirm with `git diff` that the file is back, and
  record `broken: {path:line} — restored: yes` on the phase's row. Never end a
  session with a line still broken.
- Run this phase's verification plus every earlier phase's, or the full suite,
  whichever is faster.
- Append a row to PROGRESS.md: date, phase, verify command + actual output tail,
  and any deviation from the plan with a one-line why. Never rewrite past rows.
- If the change is user-visible, exercise it once in the running app or browser and
  record what you saw — passing tests are not the same as a working screen. If the
  app cannot be run here, write `app verification: not available — {reason}` and
  carry it as UNVERIFIED.
- If two attempts at fixing a phase both fail, STOP and report rather than trying
  a third, with the tree restored to its last green state.

FINAL REVIEW: run `git add -A -N` in each repo first — untracked files do not
appear in `git diff`, and a new file is exactly what you least want unreviewed —
then diff the working tree against the BASE commits from SETUP. Two INDEPENDENT
dispatches. Same attack framing and disposition rules as the adversarial review
above; their verbatim returns are saved beside it. Where the diff is confined to
one repo and touches no protected surface, one dispatch carrying both briefs is
enough — say which you ran.

- CONFORMANCE — given the diff, PLAN.md, the requirement and the
  protected-surfaces list. Does the diff do what the requirement says, and only
  that? The plan is evidence of intent, not the standard: a diff that matches the
  plan and misses the requirement is a finding. Drift from the plan, out-of-scope
  changes, protected surfaces touched, requirements unmet, debris left behind.
  Hunk by hunk, one verdict each, then roll up.
- CORRECTNESS AND BLAST RADIUS — given the diff, the requirement and the
  protected-surfaces list, but NOT the plan, so it does not inherit the plan's
  blind spots. For each changed function, what input or state makes it wrong:
  error paths, off-by-one, null and empty, ordering and concurrency, leaks? Any
  assertion loosened, type widened, exception swallowed, or expected value
  hardcoded? And what else reads or writes what this touches: callers, the other
  repos in this workspace, schema, public API shape, background jobs, caches,
  feature flags, and the invariants in
  wiki-{workspace-name}/AGENTS/invariants.md.

Then run the deterministic gate yourself — mechanical checks, not judgment calls;
where a bullet allows a justification, that justification must already exist on a
PROGRESS row:
- the full test suite is green (command plus output tail), or its only failures are
  the ones TOOLING recorded as pre-existing, quoted from that record; type checking
  and linting are clean wherever TOOLING names a command;
- every file in the diff is in the plan's named file list, or has a deviation row —
  your own task folder does not count;
- the diff deletes no assertion and adds no new skip / only / xfail / ignore marker
  and leaves no focused or exclusive test behind, absent a one-line justification on
  its PROGRESS row; code moved unchanged between files is not an addition, but say
  so on the row;
- every phase has a red row recorded before its green one, and every break-it line
  records `restored: yes`;
- every PLAN.md coverage line carries a handling or an `N/A — {reason}`;
- a user-visible change was exercised in the app or browser with what you saw on its
  row, or carries the `app verification: not available` line;
- review-plan.md and the final-review returns exist in the task folder, each with a
  dispatch id or the independence line, and nothing is left UNVERIFIED;
- in every repo you changed, the BASE commit is still an ancestor of HEAD.

Fix what the dispatches confirmed, log each fix, then RE-RUN the gate — a fix
invalidates the green run before it. If a fix changed code, re-run the CORRECTNESS
dispatch too: nothing should ship that no independent reviewer has seen.

Then STOP and summarize: what each dispatch returned including the ones that found
nothing, their independence lines, what was fixed, what residual risk remains, and
what you did NOT check.
