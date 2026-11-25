---
name: wiki-system
description: 'Create and maintain compact source-backed codebase maps for coding agents. Use when asked to document a codebase for agents, refresh its navigation map, check documentation freshness, or connect Codex/Claude entry instructions. Commands: init, update, update --full, check, context; aliases: recheck, recheck diff, claude. Supports Git repositories, linked worktrees and sibling-repo workspaces. Documentation refreshes only on request or through a project's own CI wiring (ci); ordinary coding reads relevant pointers without regenerating the map.'
---

# wiki-system

Help agents find the right source, understand connections and avoid consequential traps.
The map describes implemented behavior; code remains the evidence, owner rules govern work,
and declared product specifications govern intent. Documentation is not a substitute for reading source.
This skill and its task prompt work standalone; `eng-rulebook` is an optional development supplement.

## Commands

| Invocation | Read / action |
| --- | --- |
| `init` | [Create or rebuild a fresh source-backed map](init.md). |
| `update` | [Refresh affected documentation](update.md). |
| `update --full`, `recheck` | Same procedure, revisit every documented area and relevant flow. |
| `recheck diff` | Alias for incremental `update`. |
| `check` | Run the read-only checks below. No factual audit or fixes. |
| `context`, `claude` | [Connect Codex/Claude instructions](context.md). |
| `ci` | [Unattended refresh](ci.md), run by `action.yml` or `scripts/ci_run.sh`, never by hand. |

Use `$wiki-system …` in Codex or `/wiki-system …` in Claude. Both use this source.
No automatic audit, update, network check, install, commit or publishing; a project that wants
refreshes after merges wires the [CI action](README.md#ci) itself and owns the commit. Requests for human/product
wiki tracks are outside this agent-map workflow; existing documents are owner-owned inputs.

## Resolve the workspace before every command

1. Read applicable project instructions. Establish the **workspace root**, source repos and docs
   destination separately from this skill directory. Resolve bundled scripts relative to the skill.
2. Prefer the user's docs destination, then the declared/existing map, then one existing `wiki-*/`.
   Otherwise use `docs/` for a single repo or `wiki-<workspace>/` for sibling repos. Honor project
   restrictions on documentation placement; ask only if multiple plausible destinations remain.
3. Discover the current Git repo (`.`) or immediate sibling Git repos, including `.git` worktree
   files. Exclude dependencies, dot-folders and the actual docs repo by path, not a `wiki-*` name rule.
   Respect recorded repos/exclusions;
   a missing repo is unavailable, not deleted. Plain directories/unborn Git repos cannot produce
   a reliable baseline: explain the limitation rather than pretending they are current.
4. The map lives at `<WIKI>/AGENTS/`. `init` builds fresh from current source, replacing confirmed
   generated output; an old wiki does not turn it into a migration. Use [existing-output handling](reference/existing-output.md)
   to identify ownership and preserve owner material. Do not create compatibility pages, redirects,
   archives or old-path scaffolding unless the user explicitly requests them. A skill-version change
   alone does not turn an ordinary `update` into a rebuild.
5. Read the optional `project_rules` pointer in state, or an existing project-instruction pointer;
   when first establishing the map, also look for `<WIKI>/rules/development.md`. Keep policy outside the map,
   link it rather than copying it, and pass relevant constraints to delegated agents. A missing
   declared policy is an error. Read optional `<WIKI>/LINKS.md` for authority pointers; do not fetch
   its URLs or create/edit policy/authority files unless specifically requested.

Pass the resolved absolute `--root <workspace>` to **every helper**, including nested/external
map locations. Paths in map prose are workspace-relative; Markdown links are page-relative.

## Check

`python3 <skill>/scripts/check.py <WIKI>/AGENTS --root <workspace> [--coverage] [--json]`

Reports structure separately from freshness: exit 0 = structurally valid/current source snapshot;
1 = invalid structure/state; 2 = stale or partial/unavailable. `--coverage` gives advisory navigation
gaps, not a per-file documentation quota. Current source fingerprints do not prove claims true.
Do not fix anything in this command unless asked. No agents or network are needed.

## Ownership and verification

- Write only managed map pages/state, confirmed-generated wiki signposts and the missing task prompt during init/update. Preserve
  handwritten files, notes and preservation blocks byte-for-byte. Other docs, tasks, PRDs and
  source/config remain untouched; entry instructions change only through `context` or explicit authorization.
- Use [page guidance](reference/pages.md) when writing and the [bounded review brief](specialists/verifier.md)
  when reviewing. No minimum pages, agents or source-LOC-based splitting. Read only task-relevant references.
- Judge usefulness by representative change navigation, not brevity, page count or ownership coverage.
  Keep startup context small; retain enough workflow detail in the relevant on-demand pages.
- Capture source before writing and finalize only after checks and source review. Never move a baseline
  forward to hide an interrupted/failed run. Preserve unavailable repos' previous snapshots and report partial work.
- Report real checks, review scope, omissions and limitations. Use independent review for substantial
  work where available; disclose self-review and the actual agent route/model when known.
- Keep the shared skill and installation unchanged while using it in a project. To maintain this skill,
  see [README](README.md); preserve existing local work and validate meaningful helper behavior.
