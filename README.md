# wiki-system

A compact codebase map for coding agents: where behavior starts, how components connect,
what must change together and which non-obvious constraints matter. Agents read the relevant
map section and then inspect current source. The map does not replace code, tests or owner policy.

## Use

- `init`: create the smallest useful map after inspecting existing docs.
- `update`: refresh affected navigation and constraints; `update --full` revisits every area.
- `check`: read-only structure and source freshness, never factual certification.
- `context`: connect minimal Codex/Claude entry pointers without replacing handwritten instructions.
- Compatibility: `recheck` = full update, `recheck diff` = update, `claude` = context.

Use `$wiki-system` in Codex or `/wiki-system` in Claude. Both discovery links target the same
canonical source. Ordinary development does not refresh docs automatically. Git-backed single repos,
linked worktrees and immediate sibling-repo workspaces are supported; always pass the resolved root
to helpers. Custom nested/external documentation destinations are valid.

## What is maintained

`<WIKI>/AGENTS/index.md` and `.state.json` are required. Optional pages answer navigation questions;
there is no mandatory catalog/contracts/invariants spine or page count. Only declared managed pages
are generated. Handwritten files, preservation blocks, owner rules, LINKS, tasks and other docs survive.

The task workflow prompt is installed once when missing. Thereafter it belongs to the project.
Existing project copies are not upgraded as a side effect of this skill release. See
[adoption notes](reference/adoption.md) for old wiki-system/wiki-lite output.

No other skill is required. The task prompt supplies standalone scope, testing and verification
guidance; when available, eng-rulebook supplements it. Its absence needs no installation or warning.

Inventory is mechanical; explanation still needs source reading. Writers work in useful batches;
review targets consequential contracts/constraints plus a rotating ordinary area. All verification
reports distinguish structure, source freshness and the actual semantic sample. A full refresh
revisits all documented areas, not every atomic claim or every source file.

Snapshot capture/finalization binds updates to the actual working tree, including dirty and
untracked evidence. Unavailable repos retain older snapshots and make the run partial. Unknown file
extensions cannot silently become clean; generated ownership does not include handwritten notes.

## Maintaining this skill

Read SKILL.md and the affected command/reference. Keep the entrypoint short; avoid copying a rule
into several procedures. VERSION is one integer for the library; state has a separate schema version.
Update CHANGELOG for meaningful behavior changes and preserve uncommitted work before consolidation.

Run:

```sh
python3 -B -m unittest discover -s tests -v
```

Also run the skill-creator validator when available, inspect local Markdown links, and perform a
bounded independent forward trial for substantial workflow changes. Tests should protect concrete
failures, not enforce prose wording or arbitrary counts. Helpers use Python's standard library and
Git on POSIX systems; snapshot finalization uses Unix advisory locks.
No new dependency, network update check, hooks, background process or per-rule ledger is required.

## Evidence and sources

The earlier wiki-lite experiments found correct outcomes both with and without the map, with slower
map-assisted runs in those small samples. That does not prove maps are useless or that v29 is faster.
Keep the usefulness check and measure source-backed answers, missed constraints, maintenance effort,
time and actual exposed usage. Do not infer tokens from transcript length or label sampled review exhaustive.

- [OpenAI: short routers and task-relevant context](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [Claude: concise instructions and verification](https://code.claude.com/docs/en/best-practices)
- [Claude: AGENTS/CLAUDE loading and compatibility](https://code.claude.com/docs/en/memory)
- [Context-file research and its evaluation limits](https://arxiv.org/abs/2602.11988)
