# Adopting the agent map in an existing project

This is a short guide for an agent performing a requested project adoption, not an automatic
migration engine. Installing/updating the shared skill never modifies live project wikis.
Old instructions invoking `wiki-lite` now use `wiki-system`; adopt the old map before updating it.

| Before | Now |
| --- | --- |
| wiki-system through v28: `.internal/plan.yaml`, per-page reports, AGENTS spine and optional PRODUCT/TECHNICAL | Agent map with index, optional question-based pages and AGENTS/.state.json schema 3. |
| wiki-lite v1/v2: fixed index/catalog/contracts/catches and state skill `wiki-lite` | Same useful navigation principles; only index required, explicit generated ownership and corrected helpers. |
| `recheck`, `recheck diff`, `claude` | Aliases for full update, incremental update and context. |
| `invariants.md` / `catches.md`, old source-line links | Link the current index/constraint page; keep needed compatibility pointers during adoption. |
| Existing task prompt, owner docs/rules, LINKS and entry instructions | Remain project-owned; no wholesale replacement. |

## Before writing

Read the old state/plan, generated headers, preservation blocks, entry instructions and incoming
links. Identify confirmed generated files separately from handwritten material. Preserve a restorable
copy of both source skill/map versions and project output, including dirty work, before replacement.
Do not classify all files in AGENTS as generated. Existing legacy state fails the new checker with
an explicit schema error; it does not justify overwriting the old map or spoofing version fields.

When the user asks for adoption, archive only confirmed obsolete generated material outside active
AGENTS (for example under `<WIKI>/.archive/`). Preserve handwritten files and keep/AUTOREGEN_SKIP
bytes. Reuse true navigation knowledge after reading current source, then create schema 3 state
with explicit managed pages and run init's source capture/review/finalization. Do not transplant
old timestamps or baselines as fresh verification. No automatic schema conversion is required.

Preserve old `.internal/` as inactive history. The new skill never runs the old generator or uses
its per-page plan as active state. Tell the user that invoking an archived/old installed generator
could overwrite the new map; the live skill installation must point to the new canonical version.

## Links and owner material

Retarget links in owned generated pages/signposts within the requested adoption. If an installed
task prompt still points to `AGENTS/invariants.md`, preserve a small generated compatibility pointer
at that path when needed, rather than silently rewriting the customized prompt. Treat other incoming
links similarly based on actual consumers, not one redirect for every archived page.

Handwritten entry instructions and installed task prompts change only when requested. `context`
authorizes a small managed routing block, not rewriting the rest. Preserve wrapper direction and
owner policy. Product specs/PRDs remain authoritative inputs even though product/human wiki generation
is retired. Remove/archive old generated PRODUCT/TECHNICAL output only within a requested adoption;
never remove handwritten product definitions or external authority files.

After adoption, run structure/freshness checks and bounded source review, verify relevant old links
and entrypoints, and report unavailable sources or unresolved references. Keep backups until reviewed.
