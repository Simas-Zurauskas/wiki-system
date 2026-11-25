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
project. Reference `@stable` (moved to each release) to receive updates, or a release tag such as
`@v38` to pin. The pieces underneath, `action.yml` and `scripts/ci_run.sh`, can also be used directly.

- `.github/workflows/update.yml`, called from the **docs repo**: clones the source repos named in
  `.state.json` with a GitHub App token, plans without a model, runs Claude Code headless only when
  source or structure needs it, gives structure errors up to two repair passes, validates, pushes the map,
  and optionally sets a select property on the Notion cards whose pull requests it covered (a
  `Failed` result also comments the reason). Runs are serialized per docs repo. Each starts from
  the docs repo's current default branch and covers the baseline-to-head range, so a pending run
  that GitHub replaces loses nothing. The run log is kept as a 7-day artifact.
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
    uses: Simas-Zurauskas/wiki-system/.github/workflows/update.yml@stable
    with:
      source: ${{ inputs.source }}
      sha: ${{ inputs.sha }}
      full: ${{ inputs.full }}
      app-client-id: Iv23lieDEWGv0WCFG4aL   # your app's client ID; not secret
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
    uses: Simas-Zurauskas/wiki-system/.github/workflows/signal.yml@stable
    with: {wiki-repo: wiki-acme, app-client-id: Iv23lieDEWGv0WCFG4aL}
    secrets: {app-private-key: ${{ secrets.WIKI_APP_PRIVATE_KEY }}}
```

Per-project setup. Names that are not secret (the app's client ID, the docs repo name) go in the
caller files, so only real secrets are stored, and only where they are used. Repository-level secrets
work on every plan; on GitHub Free, private repos cannot read organization secrets, which is why the
app key is stored once per repo. On a paid plan it can be one organization secret shared with the repos.

| Where | Secret | Used for |
| --- | --- | --- |
| GitHub App, one per organization | | Contents read, Pull requests read, Actions write; installed on the docs repo and each source repo |
| Docs repo | `WIKI_APP_PRIVATE_KEY` | Reading the source repos |
| Docs repo | `ANTHROPIC_API_KEY` | The model step only |
| Docs repo | `NOTION_TOKEN` (optional) | Card reporting: a Notion connection with update content and insert comments |
| Each source repo | `WIKI_APP_PRIVATE_KEY` | Sending the signal |

Anyone who can change workflows in a repo that holds the app key can ask the app for a read token
to every repo the app is installed on. Install one app only across repos whose people may see each
other's code; give a client project with narrower access its own app.

Pause updates with the docs repo variable `WIKI_AUTO_UPDATE=false`. Adding a source repo: map it in
the docs repo (`.state.json` `repos`), install the app on it, and give it the signal caller and the app
key. The update workflow reads the repo list from state.

Safety comes from the wrapper, not the prompt: Claude runs in a scrubbed environment with only the API
key, `--bare`, `dontAsk` permissions, edits limited to the map, no shell, no network tools or
subagents, and turn and spend caps (the spend cap covers the update and its repair passes). `conclude` then refuses edits outside the map, any change
to a source checkout, a failed structure check, or a missing or failed `result.json`. A failed run
publishes nothing and leaves the baseline in place, so the next run covers the same range.
`scripts/ci_run.sh` is the same path for a local dry run.

Releasing: update CHANGELOG, then `scripts/release.sh <N>`. It sets VERSION, points the update
workflow at action tag `vN`, commits, tags `vN`, moves `stable` and pushes. Callers on `@stable` get
the release on their next run.

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
