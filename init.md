# Create or rebuild a fresh agent map

Follow SKILL.md preflight and read [page guidance](reference/pages.md). Source is read-only.

`init` writes a new map from current source, even when generated documentation already exists.
Choose its structure for current workflows; do not migrate the previous page tree or retain old
paths for compatibility. Preserve handwritten material using [existing-output handling](reference/existing-output.md).
Link-preservation, redirects and archives are separate work only when explicitly requested.

## Find a useful scope

Run `python3 <skill>/scripts/inventory.py --root <workspace> <repo> [<repo> …]` and skim existing
repo documentation. Inventory LOC describes volume, not required page count; inspect small
integration/configuration files even when they barely affect totals. Identify questions the current
instructions cannot answer. If existing docs already answer them, explain that another map is
unnecessary; do not generate filler unless the user explicitly requests a map or experiment.

For a useful map, choose the smallest set of navigation questions: capabilities, main flows,
change entry points, boundaries and consequential constraints. One index may suffice. Add separate
pages only when retrieving them independently helps. Use existing authoritative repo docs instead
of copying them. Record intentional omissions with reasons, not a list of every undocumented file.

## Install the task prompt once

Once a useful map is selected, before source capture, if `<WIKI>/TASK-WORKFLOW-PROMPT.md` is missing,
copy the [template](TASK-WORKFLOW-PROMPT.md), replacing every `wiki-{workspace-name}` with the
actual docs path relative to the workspace. Prepend:

`> _Installed by wiki-system v<N> as a starting point. This file is the project's own: edit it freely; init and update never overwrite it._`

Read `<N>` from VERSION. Never overwrite an existing task prompt, even if its header is old.
If a newer template matters, mention the change once; updating a customized copy is a separate request.
No task directories are created by map generation.

## Capture, write, verify

1. If output exists, identify confirmed generated files and protected owner content using
   [existing-output handling](reference/existing-output.md). Keep a temporary restorable copy outside
   the wiki until review passes. Set up `.state.json` per page guidance, retaining valid existing repo
   baseline fields; declare both replaceable generated pages and planned new pages before capture.
   Add useful ownership/watch globs. This is a fresh source-writing pass, not an old-to-new migration plan.
2. Capture source **before writers**:
   `python3 <skill>/scripts/snapshot.py capture <WIKI>/AGENTS --root <workspace> --out <scratch>/snapshot.json`
   Keep scratch outside source repos or inside the excluded map. Never fake snapshot metadata.
3. Write the new map from opened source and remove superseded confirmed generated output from the
   managed list and filesystem. Update links in the generated pages/signposts being written to point
   directly to the new map. Do not create replacement pages solely to satisfy incoming links from
   untouched source READMEs, task prompts or history; report those links without blocking the rebuild.
   One writer is enough for a small job. If delegation helps, batch
   related areas and use [the writer brief](specialists/agents.md); give each writer only its assignment,
   relevant rules and pointers. Use disjoint page ownership; the orchestrator alone edits index/state.
   No fixed model/count, per-page agents or source-size-driven fan-out.
4. Run structural checks before finalization:
   `python3 <skill>/scripts/check.py <WIKI>/AGENTS --root <workspace> --structure-only --coverage`
   Resolve errors; consider warnings by navigation value and consequence, not size alone.
5. Review with [the bounded review brief](specialists/verifier.md). Record the actual batch in
   `review_summary`; unsupported claims become narrower statements or explicit uncertainties.
6. Finalize the captured source:
   `python3 <skill>/scripts/snapshot.py finalize <WIKI>/AGENTS --root <workspace> --snapshot <scratch>/snapshot.json`
   A refusal means reread the changed source, repeat affected work and capture again. Do not bypass
   preservation checks or update baselines by hand. Concurrent work must not be overwritten on rollback.
7. Run public `check` to report structure and freshness separately. Missing repos remain partial,
   with old pages/snapshots retained. Never claim their facts were reviewed.

## Finish

Report pages/words, actual agent use, structural/freshness results, semantic review scope, important
omissions and limitations. Remove temporary backups after successful review/checks unless the user
requests retention. A concise chat report suffices; do not create a report tree. Suggest
`context` if entry files are not connected. Leave source, entry instructions and user docs untouched.
