# Task workflow prompt

Put the task where `{TASK}` is and paste everything below the line as the first message of a fresh agent session
started in this workspace. If the session dies, paste the same prompt into a new one; it continues from the task
folder's `NOTES.md` (rule 4) and the working tree. For a small, low-risk fix, skip it: say the outcome, the acceptance
check and the commands to run.

`{TASK}`: a ticket link or id and/or a one-paragraph description, the location of any attachments, anything else
relevant.

---

TASK: {TASK}

You own this ticket end to end, and I don't review a plan first. These are house rules, not a process: plan, test
and verify the way you normally would. The task is large and may span more than one session: keep going until
every acceptance criterion is shown working or a real blocker remains. Give brief progress updates while working;
don't end the turn merely to report progress or offer to continue.

Follow the project's engineering guidance and the rules below. If `eng-rulebook` is available in this session,
also use its common principles and relevant guides for development; this does not launch an audit. It is an
optional supplement: its absence is not a blocker or a verification gap. Continue normally without searching
for it, requesting installation or changing project setup. Keep detailed rules in their existing authoritative
home rather than copying them into task notes.

1. Deliver the whole requested outcome with the smallest understandable change. Preserve required safety and
   compatibility; add safeguards or refactors only when needed for that outcome and a concrete reachable failure.
   Inspect existing capabilities and tests before adding code or cases. Reuse or strengthen useful protection;
   no new test is needed when existing checks demonstrate the behavior. Keep existing project gates intact.
   Follow applicable AGENTS.md/CLAUDE.md instructions, owner rules and relevant source pointers linked from
   wiki-{workspace-name}/AGENTS/index.md, and maintained conventions. Choose ordinary reversible details yourself.
   If acceptance criteria are missing, write testable
   ones in `NOTES.md` (rule 4); for consequential changes, also identify the contracts and interactions that must
   remain safe. Resolve consequential ambiguity before dependent implementation. For a bug, reproduce the failure
   before fixing it when practical; otherwise state the verification gap rather than inventing proof.
   Use fresh independent verification for consequential changes where available and permitted, proportional to
   the reachable risk. Derive expectations from requirements, challenge findings with evidence, and disclose
   self-verification when independent review is unavailable; a different model is not required.
2. Ask me only for consequential decisions the ticket, project authority and code cannot settle, access or actions
   only I can provide (an account, a login or CAPTCHA, an action off this machine, a physical device's trust prompt),
   or before deleting anything you didn't create that git can't restore. Ask as soon as the dependency is clear,
   grouping known questions with recommendations where possible; continue work that does not depend on the answer.
   If the work needs a change in code the ticket doesn't let you change, don't make it there and don't fork,
   fake or stub it; build the rest and lead your report with the exact request.
3. Leave all work uncommitted and unpushed. Change nothing off this machine that the ticket doesn't name (remote
   databases, deploys, cloud builds, store actions, ticket updates, messages to people), even when a tool offers
   it. In wiki-{workspace-name}/, write only to your task folder and to pages the ticket names. If your change
   makes CLAUDE.md, a wiki-{workspace-name}/AGENTS page or another page you may not edit out of date, don't edit
   it and don't stop to ask: give the exact edit in your report.
4. Your task folder is under wiki-{workspace-name}/tasks/. If the TASK names a ticket (an id or a link) and you
   have a tool that reaches its tracker, fetch it, read it with its comments, and walk its parent chain up
   (sub-task → story → epic). The folder mirrors that chain by bare ticket number (the id without its project
   prefix), outermost first: epic 138 > story 227 > sub-task 261 → wiki-{workspace-name}/tasks/138/227/261/; a
   ticket with no parent is wiki-{workspace-name}/tasks/261/. Reuse the ancestor folders already there; if the
   chain can't be fetched, use the bare number and say so. With no ticket:
   `wiki-{workspace-name}/tasks/<nnn>-<short-name>/`, `<nnn>` being the next free three-digit number (001 if
   none; the ticket-number trees don't count). If a folder for this ticket exists, read it and continue from it.
   Keep one file there, `NOTES.md`, with your decisions as you take them and then your report. Save the proof of
   your checks in a `qa/` subfolder as you run them, so anyone can see what was verified: relevant failing/final
   check output, screenshots where visual behavior needs verification, and any repro or probe script you used,
   each file named for what it proves. Keep evidence concise; don't create extra tests or reports to fill a quota.
   Keep secrets, tokens and personal data out of `NOTES.md` and `qa/` (redact them from pasted output).
   Keep the top lines of `NOTES.md` current (status and exact next step) so a fresh session could continue
   from it and the working tree alone.
5. Reply with a report and append it to `NOTES.md`. Status first: done, done with open items (a criterion you
   could not verify is one), or blocked. Then what changed in each repo; the checks you ran after your last code
   change, with their actual results, each pointing at its `qa/` file; what you did not or could not verify
   (browser, device, environment, account, data, tool) and why (a browser, device or environment result counts
   only on a build that contains your change, so name which); material decisions, each with its alternative so I can
   overrule it, listing first any change to a format that another repo or a shipped app reads.
