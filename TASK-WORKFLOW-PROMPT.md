# Task workflow prompt

Copy everything below the line, fill in the TASK field, and paste it as the first
message of a new agent session started in this workspace.

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
model if you can pick one. If you cannot dispatch one, write this line verbatim:
`independence: not available — self-review only`, and carry that item as
UNVERIFIED rather than as reviewed.

3. EVIDENCE OR IT DID NOT HAPPEN. "This passes", "that is already handled",
"that is out of scope" each carry a command plus the tail of its real output, or
a quoted path:line. With neither, it is a guess — write it down as one. Read
every count off the current state as you write it; never copy one forward.

4. NEVER MAKE A CHECK PASS BY WEAKENING THE CHECK — deleting or skipping a test,
loosening an assertion, widening a type to escape the type checker, swallowing an
exception, hardcoding the value the test expects. That is a failed phase, not a
passed one, and the final gate greps for it. If a test genuinely must change
because the requirement changed, log it as a deviation with a one-line why.

SETUP: Count the existing folders in wiki-{workspace-name}/tasks/ and enumerate:
if the planned folder is the fifth, it's wiki-{workspace-name}/tasks/005-{task-name}/.
The task folder contains PLAN.md and PROGRESS.md. Research findings and the raw
returns of every review dispatch are saved as md files in the same folder. If the
folder already exists, read both files first and RESUME from where they left off
— do not start over or re-plan approved work.

Open PROGRESS.md with two records, because later steps read them back:
- BASE — the current commit of every repo you may touch (git -C {repo} rev-parse
  HEAD). This is what FINAL REVIEW diffs against.
- TOOLING — how tests, type checking, linting and the app are actually run in
  this workspace. Find the real commands, do not assume them, and run the test
  command once on untouched code so a pre-existing failure is never mistaken for
  one of yours.

UNDERSTAND: Read the relevant existing code, configs, and conventions first
(start at wiki-{workspace-name}/AGENTS/index.md; read invariants.md before
touching protected areas). If a ticket is linked, read it plus its parents and
comments. Restate the requirement in your own words, including what is explicitly
OUT of scope, and list the protected surfaces you must NOT touch (schema, public
API signatures, auth flows — do not infer scope from omission). List every
assumption. For small ambiguities, choose a reasonable default and state it; for
anything that materially changes design, cost, or behavior, stop and ask me.

If this is a bug fix, reproduce it and paste the failing output into PROGRESS.md
before you plan — never fix a bug you have not seen fail. If it is new behavior,
show that the behavior is absent today.

PLAN: Write the implementation plan to PLAN.md, split into numbered phases.
Each phase: what changes, which files (name them), the exact command that
verifies it AND what its output must contain to count as a pass (a suite printing
"0 tests found" is otherwise a pass), and what could break. The check has to come
from the requirement, not from the implementation restating itself. For each
phase, name what you will break to prove the check works — revert the line or
flip the condition, watch it go red, put it back; a check that cannot be made to
fail is not verifying anything. A phase that is deliberately behavior-preserving
names the existing test covering that code and shows it green with the same test
count before and after.

Carry a line for each of these in PLAN.md, either how it is handled or
"N/A — {reason}": invalid input · empty and first-run state · concurrency and
idempotency · failure and rollback path · who is authorized · migration or
backfill for rows that already exist · backwards compatibility for existing
callers · how anyone would know this broke in production · the test that must
fail before the fix. End the plan with an explicit end-to-end verification step.
A phase without a runnable check is not a phase.

ADVERSARIAL REVIEW: one INDEPENDENT dispatch, read-only, given only PLAN.md, the
requirement and the protected-surfaces list — never this conversation. Its
verbatim return goes to
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
unmet or contradicted requirements, and out-of-scope changes; do NOT flag style
or propose extra scope. Cite the plan step for every finding.

Fold every accepted finding into PLAN.md, or reject it with a QUOTED ground — the
path:line that already handles it, or the plan line that already says it.
"Rejected, not a real case" with nothing quoted is not a rejection; record it as
an open risk. No finding is left unresolved.

STOP and present the plan, the findings and their dispositions, the assumptions
and the open questions. Do not implement until I approve. Record my approval and
any changes I request in PROGRESS.md.

IMPLEMENT phase by phase. Write each phase's test from the requirement, RUN it,
and paste the failing output into PROGRESS.md before implementing — a test that
has never been seen to fail is not evidence. After each phase, run its
verification plus the verifications of the phases already done, and append a row
to PROGRESS.md: date, phase, verify command + actual output tail, and any
deviation from the plan with a one-line why. If the change is user-visible,
exercise it once in the running app or browser and record what you saw — passing
tests are not the same as a working screen. Never rewrite past rows. If two
attempts at fixing a phase both fail, STOP and report rather than trying a third.

FINAL REVIEW: diff the working tree against the BASE commits from SETUP. Two
INDEPENDENT dispatches, each given the diff, the requirement and the
protected-surfaces list — and NOT this conversation. Same framing and disposition
rules as the adversarial review above; their verbatim returns are saved beside
it.

- CONFORMANCE — does the diff do what the requirement says, and only that? Drift
  from the plan, out-of-scope changes, protected surfaces touched, requirements
  unmet, debris left behind. Hunk by hunk, one verdict each, then roll up.
- CORRECTNESS AND BLAST RADIUS — for each changed function, what input or state
  makes it wrong: error paths, off-by-one, null and empty, ordering and
  concurrency, leaks? And what else reads or writes what this touches: callers,
  the other repos in this workspace, schema, public API shape, background jobs,
  caches, feature flags, and the invariants in
  wiki-{workspace-name}/AGENTS/invariants.md.

Then run the deterministic gate yourself — no judgment involved:
- the full test suite is green (command plus output tail), and type checking and
  linting are clean wherever TOOLING says those commands exist;
- every file in the diff is in the plan's named file list, or has a deviation row;
- the diff deletes no assertion and adds no skip / only / xfail / ignore marker
  without a one-line justification on its PROGRESS row;
- no focused or exclusive test is left behind;
- every one of the nine PLAN.md edge-case lines is present;
- the BASE commit is still an ancestor of HEAD.

Fix what the dispatches confirmed, log each fix, then RE-RUN the gate — a fix
invalidates the green run before it. Then summarize: what each dispatch returned
including the ones that found nothing, their independence lines, what was fixed,
what residual risk remains, and what you did NOT check.
