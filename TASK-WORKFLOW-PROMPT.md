# Task workflow prompt

Put the task where `{TASK}` is and paste everything below the line as the first message of a fresh agent session
started in this workspace. If the session dies, paste the same prompt into a new one; it continues from the task
folder's `NOTES.md` (rule 4) and the working tree. For a one-file fix, skip it: say the outcome, the acceptance
check and the commands to run.

`{TASK}`: a ticket link or id and/or a one-paragraph description, the location of any attachments, anything else
relevant.

---

TASK: {TASK}

You own this ticket end to end, and I don't review a plan first. These are house rules, not a process: plan, test
and verify the way you normally would. The task is large and may span more than one session: keep going until
every acceptance criterion is shown working or a real blocker remains, and don't stop to report progress or offer
to continue.

1. Deliver all of the ticket and nothing beyond it: defer nothing because of the effort it takes, and add no
   refactor, layer or hardening it doesn't ask for. Where it leaves something open, choose what a careful owner
   would, note it and keep going; what CLAUDE.md, wiki-{workspace-name}/AGENTS/invariants.md and the existing
   conventions already settle is not open, so follow it. If it has no testable acceptance criteria, write the ones
   you will build to in `NOTES.md` (rule 4) before you code. For a bug, watch it fail before you fix it, so you
   know the fix hits the cause.
2. Ask me only for what only I can give (an account, a credential, a login or CAPTCHA, an action off this
   machine, a tap on a physical device's trust prompt), or before deleting anything you didn't create that git
   can't restore. Finish everything that doesn't depend on the answer, then ask once: a numbered list, each item
   with the answer you recommend. If the work needs a change in code the ticket doesn't let you change, don't make
   it there and don't fork, fake or stub it; build the rest and lead your report with the exact request.
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
   your checks in a `qa/` subfolder as you run them, so anyone can see what was verified: the bug's failing output
   before the fix, the output of the final test/type-check/lint runs, screenshots of user-visible changes, and any
   repro or probe script you used, each file named for what it proves. Keep secrets, tokens and personal data out
   of `NOTES.md` and `qa/` (redact them from pasted output). Keep the top lines of `NOTES.md` current (status,
   the exact next step) so a fresh session could continue from it and the working tree alone.
5. Reply with a report and append it to `NOTES.md`. Status first: done, done with open items (a criterion you
   could not verify is one), or blocked. Then what changed in each repo; the checks you ran after your last code
   change, with their actual results, each pointing at its `qa/` file; what you did not or could not verify
   (browser, device, environment, account, data, tool) and why (a browser, device or environment result counts
   only on a build that contains your change, so name which); your decisions, each with its alternative so I can
   overrule it, listing first any change to a format that another repo or a shipped app reads.
