# Task workflow prompt

Copy everything below the line, fill in the TASK field, and paste it as the first
message of a new agent session started in this workspace.

---

TASK: {one-paragraph description, links (Jira link if there is one), attachments
location, anything else relevant}

SETUP: Count the existing folders in wiki-{workspace-name}/tasks/ and enumerate:
if the planned folder is the fifth, it's wiki-{workspace-name}/tasks/005-{task-name}/.
The task folder contains PLAN.md and PROGRESS.md. Research findings should also be
saved to md files in the same folder for future reference. If the folder already
exists, read both files first and RESUME from where they left off — do not start
over or re-plan approved work.

UNDERSTAND: Read the relevant existing code, configs, and conventions first (start
at wiki-{workspace-name}/AGENTS/index.md; read invariants.md before touching
protected areas). If a ticket is linked, read it plus its parents and comments.
Restate the requirement in your own words, including what is explicitly OUT of
scope, and list the protected surfaces you must NOT touch (schema, public API
signatures, auth flows — do not infer scope from omission). List every assumption.
For small ambiguities, choose a reasonable default and state it; for anything that
materially changes design, cost, or behavior, stop and ask me.

PLAN: Write the implementation plan to PLAN.md, split into numbered phases.
Each phase: what changes, which files (name them), the exact command that
verifies it, and what could break. Include a dedicated edge-case section:
invalid inputs, concurrency, failure/rollback paths, empty/large data,
backwards compatibility. End the plan with an explicit end-to-end verification
step. A phase without a runnable check is not a phase.

ADVERSARIAL REVIEW: Review PLAN.md in a FRESH context (a subagent that sees
only the plan and the requirement — not the conversation that produced them).
Flag ONLY: correctness bugs or infeasible steps, security issues, unmet or
contradicted requirements, and out-of-scope changes. Do NOT flag style or
propose extra scope. Cite the plan step for every finding; if the plan is sound
and complete, say so explicitly. Fold every accepted finding into PLAN.md or
record "rejected, because ..." in PROGRESS.md — no finding is left unresolved.

STOP and present the plan, assumptions, and open questions. Do not implement
until I approve. Record my approval and any changes I request in PROGRESS.md.

IMPLEMENT phase by phase. Where practical, write the tests from the
requirements first and confirm they fail before implementing. After each phase,
run its verification and append a row to PROGRESS.md: date, phase, verify
command + actual output tail (evidence, never "it works"), and any deviation
from the plan with a one-line why. Never rewrite past rows and never silently
edit the approved plan — deviations are logged, not hidden.

FINAL REVIEW: In a fresh context, review the actual diff against PLAN.md
(same scoped rules as step 3): unhandled edge cases, drift from the plan,
missing tests. Fix what you find, log the fixes in PROGRESS.md, then summarize
what was reviewed, what was fixed, and any residual risk.
