# Connect Codex and Claude entry instructions

`context` (alias `claude`) connects an existing map without scanning the whole codebase or
regenerating it. Follow SKILL.md preflight. Require a readable map index/state; if absent, use
`init` first. Read the index, declared owner policy and optional LINKS.md; do not fetch external URLs.

## One authority, small pointers

Inspect workspace and source-repo AGENTS.md/CLAUDE.md entrypoints, including symlink/import wrappers.
Preserve their existing direction of authority. Prefer one shared AGENTS.md with a thin CLAUDE.md
import where neither exists. Keep established CLAUDE.md authority and Codex wrappers working.
Do not depend on Claude's optional native AGENTS loading or change global settings.

Calling `context` authorizes creating missing entry files or updating a small managed routing block;
it does not authorize replacing handwritten instructions or unrelated generator output. Respect any
stricter project prohibition. In that case prepare a concrete proposed block and report the gap.
Use relative paths from each entry file, including agents starting inside sibling repos.

```markdown
<!-- wiki-system: context -->
Use [the codebase map](<relative path to AGENTS/index.md>) when locating behavior or planning a change.
Load only relevant area pages, then verify current source before editing.
<If declared: Read and follow [project rules](<relative policy path>) before planning, implementation or review; pass applicable constraints to delegated agents.>
<If present: [External references](<relative LINKS.md path>) identify product/spec authority; the map describes implemented code.>
<Without CI: Refresh the map only when asked, using wiki-system update; entry pointers use wiki-system context.>
<With CI: The map refreshes automatically after merges to <branch>; do not edit its pages in feature work. Entry pointers use wiki-system context.>
<!-- /wiki-system: context -->
```

Use exactly one of the refresh lines. Remove absent optional lines. Do not duplicate commands, area lists, catches or policy in entry files.
Aim for a few useful lines, not a hard cap that truncates owner content. A new CLAUDE.md can contain
`@AGENTS.md`; a new Codex wrapper around authoritative CLAUDE.md must explicitly instruct reading it.
Avoid reciprocal imports. If an existing wrapper already reaches the canonical file, do not add a
second copy. Report which root/repo entrypoints are actually connected.
In a sibling-repo workspace, verify discovery from both the workspace and the repo's own Git root;
a parent workspace instruction is not guaranteed to load when Codex opens that repo independently.
Markdown links route on demand; Claude `@` imports load their contents at startup. Import only the
small shared instruction file, not the map tree. Existing local planning docs may describe intent
or history; do not silently treat them as evidence of implemented behavior.

## Safe installation and validation

1. Save each original file's bytes in scratch. For a new managed block, preserve all surrounding
   content and preservation blocks exactly. Replace only one balanced existing block; duplicate or
   nested markers require resolving the conflict, not deleting unknown text. Never follow a symlink
   to overwrite an unrelated target; reuse the existing instruction route instead.
2. Check each proposed local link resolves and each wrapper reaches the intended authority without
   a cycle. Do not copy every LINKS entry into startup context or invent a policy file.
3. Install atomically, then run:
   `python3 <skill>/scripts/check.py <WIKI>/AGENTS --root <workspace> --structure-only`
   Check the installed result and compare outside-block bytes to the originals. On a structural
   failure caused by the change, restore only your unchanged-since-install writes, repair and retry.
4. Run public `check` and report freshness separately. Entry-file changes may make the source snapshot
   stale; disclose this rather than silently advancing a semantic baseline or rolling back valid
   pointers merely because an update is pending. Missing source repos likewise remain partial.

No global settings, hooks, policy edits, source changes or automatic documentation refresh.
