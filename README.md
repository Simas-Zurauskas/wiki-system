# wiki-system

A compact codebase map for coding agents: where behavior starts, how components connect,
what must change together and which non-obvious constraints matter. Agents read the relevant
map section and then inspect current source. The map does not replace code, tests or owner policy.

## Use

- `init`: create a fresh source-backed map, replacing confirmed generated output when present.
- `update`: refresh affected navigation and constraints; `update --full` revisits every area.
- `check`: read-only structure and source freshness, never factual certification.
- `context`: connect minimal Codex/Claude entry pointers without replacing handwritten instructions.
- Compatibility: `recheck` = full update, `recheck diff` = update, `claude` = context.

Use `$wiki-system` in Codex or `/wiki-system` in Claude. Both discovery links target the same
canonical source. Ordinary development does not refresh docs automatically. Git-backed single repos,
linked worktrees and immediate sibling-repo workspaces are supported; always pass the resolved root
to helpers. Custom nested/external documentation destinations are valid.

## CI

Projects reuse two workflows from this repo and pass settings only, so a fix here reaches every
project. Reference `@v1` (moved to each release) to receive updates, or a release tag such as `@v34`
to pin. The pieces underneath, `action.yml` and `scripts/ci_run.sh`, can also be used directly.

- `.github/workflows/update.yml`, called from the **docs repo**: clones the source repos named in
  `.state.json` with a GitHub App token, plans without a model, runs Claude Code headless only when
  source or structure needs it, gives structure errors one repair pass, validates, pushes the map,
  and optionally sets a select property on the Notion cards whose pull requests it covered (a
  `Failed` result also comments the reason). Runs are serialized per docs repo; each covers the
  baseline-to-head range, so a replaced pending run loses nothing. The run log is kept as a 7-day artifact.
- `.github/workflows/signal.yml`, called from each **source repo** on push: starts the docs repo's
  update through the REST dispatch API. It never blocks a merge or deploy.

Docs repo caller (`.github/workflows/wiki-update.yml`):

```yaml
on:
  workflow_dispatch:
    inputs: {source: {default: ''}, sha: {default: ''}, full: {type: boolean, default: false}}
permissions: {contents: write}
jobs:
  update:
    if: vars.WIKI_AUTO_UPDATE != 'false'
    uses: Simas-Zurauskas/wiki-system/.github/workflows/update.yml@v1
    with:
      source: ${{ inputs.source }}
      sha: ${{ inputs.sha }}
      full: ${{ inputs.full }}
      app-client-id: ${{ vars.WIKI_APP_CLIENT_ID }}
      notion-property: Wiki            # optional; omit to skip card reporting
    secrets:
      anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
      app-private-key: ${{ secrets.WIKI_APP_PRIVATE_KEY }}
      notion-token: ${{ secrets.NOTION_TOKEN }}   # optional
```

Source repo caller (`.github/workflows/wiki-signal.yml`):

```yaml
on: {push: {branches: [main]}}
permissions: {}
jobs:
  signal:
    if: vars.WIKI_REPO != ''
    uses: Simas-Zurauskas/wiki-system/.github/workflows/signal.yml@v1
    with: {wiki-repo: ${{ vars.WIKI_REPO }}, app-client-id: ${{ vars.WIKI_APP_CLIENT_ID }}}
    secrets: {app-private-key: ${{ secrets.WIKI_APP_PRIVATE_KEY }}}
```

Per-project setup. Repository-level secrets and variables work on every plan, including private
repos on GitHub Free, where organization secrets are not available to them.

| Where | Name | Value |
| --- | --- | --- |
| GitHub App | one per organization | Repository permissions Contents read, Pull requests read, Actions write; installed on the docs repo and each source repo |
| Docs repo | `WIKI_APP_CLIENT_ID` variable, `WIKI_APP_PRIVATE_KEY` secret | The app's client ID and private key |
| Docs repo | `ANTHROPIC_API_KEY` secret | API key used by the model step only |
| Docs repo | `NOTION_TOKEN` secret (optional) | Notion connection with update content and insert comments, shared with the tasks database |
| Docs repo | `WIKI_AUTO_UPDATE` variable (optional) | `false` pauses the updates |
| Each source repo | `WIKI_REPO` variable | Docs repo name; unset to stop signalling |
| Each source repo | `WIKI_APP_CLIENT_ID`, `WIKI_APP_PRIVATE_KEY` | Same app |

Adding a source repo: map it in the docs repo (`.state.json` `repos`), install the app on it and give
it the signal caller and its three settings. The update workflow picks the repo list from state.

Safety comes from the wrapper, not the prompt: Claude runs in a scrubbed environment with only the API
key, `--bare`, `dontAsk` permissions, edits limited to the map, read-only shell commands, no network
tools or subagents, and turn and spend caps. `conclude` then refuses edits outside the map, any change
to a source checkout, a failed structure check, or a missing or failed `result.json`. A failed run
publishes nothing and leaves the baseline in place, so the next run covers the same range.
`scripts/ci_run.sh` is the same path for a local dry run.

## What is maintained

`<WIKI>/AGENTS/index.md` and `.state.json` are required. Optional pages answer navigation questions;
there is no mandatory catalog/contracts/invariants spine or page count. Only declared managed pages
are generated. Handwritten files, preservation blocks, owner rules, LINKS, tasks and other docs survive.

The task workflow prompt is installed once when missing. Thereafter it belongs to the project.
Existing project copies are not upgraded as a side effect of this skill release. Old generated
output does not require a migration project: `init` writes a new map from source, with no compatibility
pages, redirects or archives unless explicitly requested. [Existing-output handling](reference/existing-output.md)
preserves owner material and snapshot integrity; it does not preserve the previous generated tree.

No other skill is required. The task prompt supplies standalone scope, testing and verification
guidance; when available, eng-rulebook supplements it. Its absence needs no installation or warning.

Inventory is mechanical; explanation still needs source reading. Writers work in useful batches;
review targets consequential contracts/constraints plus a rotating ordinary area. All verification
reports distinguish structure, source freshness and the actual semantic sample. A full refresh
revisits all documented areas, not every atomic claim or every source file.
Substantial map work also tries representative change requests from the index through source and
verification pointers. Area depth follows those tasks; smaller output is not itself a better map.

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

Official guidance reviewed on 2026-11-09 supports small startup instructions, relevant detail loaded
on demand, concrete project conventions/checks, and evaluation against actual tasks. It does not
prescribe a universal wiki layout, an area-page word limit or a required page count. This skill's
navigation trial is a local application of those principles, not a vendor-mandated workflow.

Keep durable owner rules in entry instructions, code explanations in linked map pages, and exact
contracts in source. Do not import the whole wiki into startup context: Claude imports load eagerly.
Codex and Claude instruction discovery differ, so check actual entry routes instead of assuming a
parent workspace file reaches every independently opened sibling repository. Avoid duplicating the
manual in wrappers. No hook, retrieval database or new background service is needed for this map.

The earlier wiki-lite experiments found correct outcomes both with and without the map, with slower
map-assisted runs in those small samples. That does not prove maps are useless or that v29 is faster.
Keep the usefulness check and measure source-backed answers, missed constraints, maintenance effort,
time and actual exposed usage. Do not infer tokens from transcript length or label sampled review exhaustive.

- [OpenAI: durable project guidance and verification](https://learn.chatgpt.com/guides/best-practices)
- [OpenAI: instruction discovery and scope](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [OpenAI: short routers and task-relevant context](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [Claude: concise instructions and verification](https://code.claude.com/docs/en/best-practices)
- [Claude: AGENTS/CLAUDE loading and compatibility](https://code.claude.com/docs/en/memory)
- [Anthropic: sufficient context and on-demand retrieval](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)
- [Context-file research and its evaluation limits](https://arxiv.org/abs/2602.11988)
