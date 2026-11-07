# Create a compact agent map

Follow SKILL.md preflight and read [page guidance](reference/pages.md). Source is read-only.

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

1. If output exists, follow [adoption](reference/adoption.md). Save the pre-edit map/state in scratch;
   record which files are generated and preserve all other files. Set up `.state.json` per page guidance,
   retaining existing repo baseline fields. Add managed page paths and useful ownership/watch globs.
2. Capture source **before writers**:
   `python3 <skill>/scripts/snapshot.py capture <WIKI>/AGENTS --root <workspace> --out <scratch>/snapshot.json`
   Keep scratch outside source repos or inside the excluded map. Never fake snapshot metadata.
3. Write the map from opened source. One writer is enough for a small job. If delegation helps, batch
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
omissions and limitations. A concise chat report suffices; do not create a report tree. Suggest
`context` if entry files are not connected. Leave source, entry instructions and user docs untouched.
