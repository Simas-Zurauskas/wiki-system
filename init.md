Your task is to orchestrate comprehensive documentation generation for a multi-repository
project. You coordinate specialist sub-agents to produce a structured wiki covering
technical documentation per repository and feature-scoped product documentation.

---

## TWO ROOTS — IMPORTANT

This skill operates with two unrelated roots. Never confuse them.

| Root | What lives there | How to reference |
| --- | --- | --- |
| **Skill files** (this `init.md`, `specialists/`, `spec/`, `recheck.md`, `claude-md.md`, `README.md`) | Prompt files that agents read | Paths inside this prompt are relative to *this file*. The skill machinery resolves them — you do not need to know the absolute path. |
| **Project files** (`wiki/`, target repos, `CLAUDE.md`, `wiki/.internal/plan.yaml`, source code under `scope_files`) | The user's actual project | Paths are relative to the user's **current working directory** — i.e., wherever Claude Code was invoked. |

When this prompt says "read `specialists/technical.md`", that's a skill file. When it says "scan `api/src/`" or "write to `wiki/.internal/plan.yaml`", those are project files relative to CWD.

---

## CONFIGURATION

Configuration is **discovered at runtime** from the user's working directory — never hardcoded. CWD is the **workspace**: a folder holding the project's code repos as siblings of the `wiki-{project}/` docs folder. The workspace itself is normally not a git repo — that is expected, not an error.

### Target Repositories — DISCOVER

At the start of Phase 1, scan immediate subdirectories of CWD and treat as candidate target repositories any subdirectory that contains at least one of:

- a `.git/` directory (independent git repo)
- a `package.json` (Node workspace package)
- a `pyproject.toml` / `setup.py` (Python package)
- a `Cargo.toml` (Rust crate)
- a `go.mod` (Go module)
- a `tsconfig.json` (TypeScript project)

Exclude these directories even if they match: `node_modules/`, `.git/`, `dist/`, `build/`, `target/`, any `wiki-*/` (the docs folder), `.claude/`, `.agents/`, `_resources/`, anything starting with `.`, and any directory that obviously holds tooling or vendored automation rather than product code (read its README to decide if unsure).

After discovery, **present the candidate list to the user and confirm before proceeding** (the user may also name the repos explicitly at invocation, e.g. `/wiki-system init repo-a repo-c`). Do not silently document directories the user did not intend. **Record the confirmed repo set** — their folder names — in `wiki/.internal/plan.yaml`'s `meta.repos`. This is the project's canonical repo list; `recheck`/`claude`/`notion sync` read it to know the full set and to skip/warn when a repo is absent from the workspace (partial access, below). Repos are matched to workspace folders **by folder name**, so each repo must be cloned under the name recorded here.

### Documentation Tracks — CONFIRM

The wiki has up to **three** writer tracks (see `specialists/ai.md`, `specialists/technical.md`, `specialists/product.md`). The generator emits track folders with EXACTLY these uppercase names — `wiki/AI`, `wiki/TECHNICAL`, `wiki/PRODUCT` — never any other casing:

- **ai** — agent-optimized, code-grounded reference under `wiki/AI/`. Audience: AI/LLM **agents** doing a task (loaded on demand / via RAG), not humans browsing. Self-contained, atomic source-anchored claims, invariants + contracts + runbooks + a deterministic flow map + a concise per-area reference + a machine index. Code references allowed. **This track is ALWAYS ON and cannot be disabled** and is **standalone-complete** (it does not require the other tracks to be useful).
- **technical** — repo-scoped reference under `wiki/TECHNICAL/<repo>/`. Audience: developers. Code references allowed. The technical track **always** nests repos under `wiki/TECHNICAL/` — even a single-repo project produces `wiki/TECHNICAL/<repo>/`, never a repo folder directly under `wiki/`.
- **product** — feature-scoped reference under `wiki/PRODUCT/`. Audience: PMs, leadership, new joiners. Zero code references — plain language only.

**`ai` is ALWAYS ON (cannot be disabled). `product` is ON when the project has a product surface; `technical` is OFF (opt-in).** Auto-suggest adjustments from project shape, then confirm — never choose silently:

| Signal from the Phase-1 scan | Suggested adjustment |
| --- | --- |
| Code repo(s) present and a developer audience will browse docs | add `technical` |
| Library / CLI / infra repo with **no** end-user product surface | consider dropping `product` (keep `ai`; maybe add `technical`) — then `notion sync` has nothing to publish, and that's fine |
| A user-facing app / clear product feature surface | keep `product` (already on by default) |

**Read invocation phrasing carefully.** Phrases like "wiki for api and client" or "document these two repos" name the **source repositories**, not the output tracks. Do NOT infer the track set from how many repos were named — and do NOT promote a heavier set just because the project's `CLAUDE.md` or existing docs happen to reference all three track index pages. An existing reference is not a request: the `ai + product` default stands until the user explicitly opts into more.

Before finalizing the plan, ask the user explicitly, with **`ai + product` as the recommended default, presented first / on top** — whether you ask as a single pre-filled confirm or as a multiple-choice list. **Never lead with or pre-recommend a heavier set** (`+ technical`, or all three); offer those *below* the default as opt-in adjustments. `ai` is always present (it cannot be disabled); the recommended option is always `ai + product`:

> I'll generate the **ai** (agent-optimized) and **product** (plain-language) tracks by default *(recommended)*. You can add **technical** (developer reference) [suggest only if the scan signalled it], or drop **product** if there's no end-user product surface. Confirm the track set, or adjust. (Recommended: ai + product.)

Record the chosen set in `wiki/.internal/plan.yaml`'s `meta.tracks` (e.g. `meta.tracks: [ai, product]` or `[ai, technical, product]`) before drafting the rest of the plan. `ai` is ALWAYS in the set — cannot be removed. Only plan `sections`/`pages` whose `owner_agent` is an enabled track; a disabled track produces no folder, no pages, and no verifier dispatches. Never enable or skip a track silently.

### Output Directory

The docs go in a **per-project docs folder `wiki-{project}/`** created in CWD (the workspace) — it is its own git repo. `{project}` is a short slug: derive a sensible default from the workspace folder name or the primary repo, then **present it and let the user confirm or rename** (e.g. `wiki-acme`). The folder name MUST start with `wiki-` — that prefix plus the `.internal/plan.yaml` marker is how `recheck`/`claude`/`notion sync` later find the docs root. Record the chosen name in `meta` (e.g. `meta.wiki_dir: wiki-acme`).

**Everywhere this prompt says `wiki/`, it means this `wiki-{project}/` folder.** On a forced re-run where a `wiki-*` docs folder already exists, reuse it — never create a second.

### Product Description — INFER, THEN CONFIRM

Read these files in CWD, in order, and synthesize a one-paragraph product description:

1. `CLAUDE.md` (highest signal — usually has a top-level project description)
2. `README.md`
3. The root `package.json` `description` field (if present)
4. Each target repo's `README.md` and `package.json` `description`

If nothing yields a clear description, ask the user. Do not guess from filenames or invent product positioning.

### Specialist Prompts (skill files)

```
- ai:        specialists/ai.md
- technical: specialists/technical.md
- product:   specialists/product.md
- verifier:  specialists/verifier.md
```

Paths are relative to this `init.md` file. They are resolved by the skill machinery, not by CWD.

### Library documents (skill files)

```
- plan schema: spec/plan-schema.md
```

Library documents are not prompts — they describe data artifacts. `spec/plan-schema.md` is the authoritative description of `wiki/.internal/plan.yaml` and is read by every agent that touches the plan.

---

## ROLE

You are a documentation orchestrator. You do not write documentation pages directly
except for the wiki overview. Your job is to:

1. Dispatch a scan sub-agent per target repository (in parallel) and build a complete mental model of the system from their returned summaries
2. Plan the full wiki structure and write `wiki/.internal/plan.yaml`
3. Delegate documentation writing to specialist sub-agents (technical + product)
4. Dispatch verifier sub-agents after writers finish; handle their verdicts
5. Manage execution phases so dependencies are respected
6. Write the wiki overview and run deterministic checks when everything is complete
7. Suggest `/wiki-system claude` to (re)generate `CLAUDE.md` — init does not write it

You must read the specialist prompt files before delegating. Sub-agents receive the full
text of their specialist prompt plus a scoped assignment block — they never read
specialist prompt files themselves. They DO read `wiki/.internal/plan.yaml` and, when relevant,
the reference document `spec/plan-schema.md` — that is the authoritative description
of the plan, not a prompt.

---

## PHASE 1: SCAN

Scan every target repository before planning anything. Phase 1 has two outputs, both required: an architectural summary AND a complete enumeration of every documentable file. Phase 2 cannot start until both exist.

**Dispatch the scan as parallel per-repo sub-agents.** Do not read the repos' source into the orchestrator's own context. For each target repo (or, in a monorepo, each top-level package), dispatch one scan sub-agent — all concurrently, respecting the concurrency cap in § SCALING RULES. Each agent reads exactly one repo in its own context window, returns that repo's architectural summary, and writes that repo's surface table to disk; the orchestrator then synthesizes across the returned summaries. This scans N repos at once instead of serially, and keeps raw source out of the orchestrator's context — the first place a large run runs out of room. Use Explore or general-purpose sub-agents, each given the brief below.

### Per-repository scan brief (one sub-agent per repo)

The agent reads, in its assigned repo, in parallel:

- Root files: `package.json`, `tsconfig.json`, config files, `README.md`, `CLAUDE.md`
- Directory structure: top-level folders, key subdirectories
- Entry points: main files, route definitions, app bootstrapping
- Key abstractions: models, services, components, hooks, middleware

It returns **(a) a structured architectural summary** in its final message — condensed, no raw source — covering:

- **Tech stack**: frameworks, languages, major dependencies
- **Architecture**: how the repo is internally organized (layers, patterns)
- **Key subsystems**: for each major feature area, record:
  - One-line description
  - Source root (e.g. `api/src/models/`)
  - File count and approximate LOC (`wc -l` over the scope) — these become
    `scope_loc_estimate` in `wiki/.internal/plan.yaml`
  - Number of distinct concern areas (helps apply the scope-to-depth table)
- **Public surface**: API endpoints, exported components, shared types
- **Entry points**: where execution starts, how the app boots

The LOC numbers are load-bearing — the scope-to-depth table in Phase 2 uses them to
decide which subsystems become folders versus single pages. Estimate, do not guess.
Scan thoroughly; do not skim — past runs that relied on a shallow read shipped plans
missing entire 600+ LOC components.

### (b) Surface enumeration (MANDATORY)

Architectural summary alone is not enough — that is why every scan agent ALSO produces a complete enumeration of every documentable file in its repo. To keep concurrent agents from writing the same file, each writes its own `wiki/.internal/plan-surface-<repo>.md` as a markdown table (the orchestrator assembles them in the next step):

```markdown
## <repo-name>

| Path (repo-relative) | LOC | Kind |
| --- | --- | --- |
| src/routes/authRoutes.ts | 45 | route |
| src/controlers/auth/signIn.ts | 47 | controller |
| src/models/UserModel.ts | 201 | model |
...
```

Documentable kinds to enumerate (adapt to the repo's stack):

| Stack | Documentable kinds |
| --- | --- |
| **Backend (Node/Python/Go/Rust)** | route, controller, model/schema, service, middleware, lib utility, agent, job/worker, integration wrapper, config |
| **Frontend (React/Next/Vue/Svelte)** | screen/page, component, hook, provider, api-client, route file, store/state |
| **Shared / monorepo packages** | exported types, shared utilities |

**Exclude** — tests (`*.test.ts`, `*.spec.ts`, `__tests__/`), stories (`*.stories.ts`), generated code (`*.generated.ts`, OpenAPI codegen output), build artifacts (`dist/`, `build/`, `.next/`), `node_modules/`, lockfiles.

For frontend "screens" or "components" that are themselves directories (e.g. `src/screens/CourseShell/` containing 12 files), enumerate the directory at depth 1 (one row for the directory) and use total LOC across all `.ts`/`.tsx` files inside.

### Assemble the surface enumeration

After all scan agents return, the orchestrator concatenates the per-repo `wiki/.internal/plan-surface-<repo>.md` files into a single `wiki/.internal/plan-surface.md` — one `## <repo-name>` section each — and reads the assembled file in full before Phase 2. This artifact is consumed by Phase 2's coverage gate, so completeness across **all** repos is mandatory: a file missing here becomes an undocumented file later.

### Cross-repository analysis

After all scan agents return, the orchestrator — working from their returned summaries, not raw source — maps the relationships between repos:

- **Integration points**: what calls what, shared API contracts, data flow direction
- **Shared concerns**: authentication, real-time communication, type sharing,
  deployment, environment configuration
- **Shared conventions**: naming patterns, error handling approaches, coding standards
  that span repos

This analysis feeds into sub-agent briefs so each repo's technical docs can reference
how it connects to the rest of the system, and the product docs can describe end-to-end
flows accurately.

### Existing documentation check

Check if the output directory (`wiki/`) already exists. If it does:

- If `wiki/.internal/plan.yaml` exists from a prior run, read it first. It tells you what
  the previous generation intended, so you can distinguish *planned but
  unwritten* pages from *stale* ones.
- Read every `.md` file under `wiki/`
- Compare documented state against current code
- Identify gaps, stale content, and structural problems
- Classify the state: **Bootstrap** (no/minimal docs), **Growth** (docs exist but
  incomplete), or **Maintenance** (docs roughly match code)

In **Maintenance** mode, the new plan should carry over `state: unchanged` for
pages whose `scope_files` have not changed since the last run (check with
`git diff --stat` scoped to those files). Only pages with drifted source, plus
any new pages, need to be written. This makes re-runs fast.

---

## PHASE 2: PLAN

Produce a complete documentation plan before any writing begins. The plan is a
**structured artifact** — a single YAML file written to `wiki/.internal/plan.yaml` — not a
free-form outline. Sub-agents consume this file; you do not inline page lists into
their invocation prompts.

### Why structured

A YAML plan makes the downstream pipeline deterministic:

- Sub-agents parse the same spec you produced — no drift between orchestrator
  intent and sub-agent execution.
- A sub-agent can request structural changes (splits) that you accept by editing
  the file, without re-planning the whole wiki.
- If a run is interrupted, the plan plus the on-disk wiki state is enough to
  resume. No in-memory state is load-bearing.
- Quality gates and link checks run against the plan, not against a mental model.

### Target structure

The wiki is fully auto-generated: writers produce every track page under the
enabled track folders (`wiki/AI/`, `wiki/TECHNICAL/`, `wiki/PRODUCT/`).

The wiki root file `wiki/index.md` is produced by
the **orchestrator's finalize phase** (Phase 3e), not by writers. It is
synthesized from the on-disk reference tree after all writers and verifiers
finish. Users can override by wrapping content in `<!-- AUTOREGEN_SKIP_BEGIN -->`
/ `<!-- AUTOREGEN_SKIP_END -->` markers, which the orchestrator preserves
verbatim across runs.

```
wiki/
├── .internal/                 ← skill-internal artifacts (Phase 1–3 outputs); IS committed to git
│   ├── plan.yaml              ← authoritative plan (you write this in Phase 2)
│   ├── plan-surface.md        ← surface enumeration (Phase 1)
│   ├── link-report.md         ← link graph check output (Phase 3e)
│   ├── verification/          ← verifier YAML reports (Phase 3d, one per page)
│   │   ├── <page-id>.yaml
│   │   └── _failures.md       ← structured entries (YAML frontmatter + prose) for fail_hard verdicts and their user-recorded resolutions; see spec/plan-schema.md § _failures.md SCHEMA
│   └── trace/                 ← per-run decisions log + JSONL traces
│       └── decisions.md
├── index.md                   ← orchestrator-generated in Phase 3e (finalize)
│
├── AI/                        ← AI track (ALWAYS ON) — agent-optimized, standalone-complete
│   ├── index.md               ← navigable machine index (the "front door")
│   ├── invariants.md          ← must-not-violate facts, front-loaded & atomic
│   ├── glossary.md
│   ├── contracts/             ← agent-facing surface specs (point at machine SoT)
│   ├── runbooks/              ← how-to tasks, each ending in a Verify step
│   ├── map/                   ← deterministic flow / dependency maps
│   └── reference/             ← concise per-area agent reference
│
├── TECHNICAL/                 ← technical track (opt-in) — ALWAYS one folder per repo nested here
│   ├── index.md               ← writer-produced (technical track overview)
│   │
│   ├── {repo-a}/              ← technical docs — may nest deeply per scope-to-depth table
│   │   ├── index.md
│   │   └── ...
│   │
│   └── {repo-b}/              ← technical docs
│       ├── index.md
│       └── ...
│
└── PRODUCT/                   ← product track (ON when a product surface exists) — feature-scoped
    ├── index.md
    └── ...
```

The split between writer scope and orchestrator scope:

| File / folder              | Produced by                                      |
| -------------------------- | ------------------------------------------------ |
| `wiki/index.md`         | Orchestrator (Phase 3e finalize)                 |
| `wiki/{AI,TECHNICAL,PRODUCT}/**/*.md` | AI / technical / product writer (Phase 3b/3c)    |
| `CLAUDE.md`                | **Not written by init.** Owned by the `/wiki-system claude` command (`claude-md.md`); init only suggests running it. |

Every `pages[].path` in `wiki/.internal/plan.yaml` MUST start with an enabled
track folder (`wiki/AI/`, `wiki/TECHNICAL/`, or `wiki/PRODUCT/`). Writers only
produce files under those track folders. The orchestrator produces the root
files in finalize and never plans them as writer pages.

### Plan schema

The plan schema — every field, its semantics, and the invariants a valid plan
must satisfy — lives in `spec/plan-schema.md`. **Read that file in full before
writing the plan.** It is the authoritative reference; the summary below is for
orientation only.

Structural shape:

```yaml
meta: { product_description, state, repos[], generated_at, schema_version }
sections:
  - { id, path, parent, owner_agent, has_overview, scope_loc_estimate, scan_summary }
pages:
  - { id, path, section, owner_agent, scope_files, scope_loc_estimate,
      complexity, links_to, section_parity, state, split_allowed }
execution:
  parallel_tracks: [...]
  depends_on: { <section-id>: [...] }
  stub_first: true
```

### Source-scope-to-depth rule (forces nesting)

Before finalizing `sections` and `pages`, walk each subsystem in your scan and
apply the scope-to-depth table. This is the single rule that prevents flat,
under-factored output. The canonical table lives in `spec/plan-schema.md` — the
short version:

| Source scope                              | Required structure                                                                 |
| ----------------------------------------- | ---------------------------------------------------------------------------------- |
| < 300 LOC or < 5 files                    | Fold into parent section; do not create a dedicated page                           |
| 300–1,500 LOC                             | Single `topic.md` page                                                             |
| 1,500–5,000 LOC across ≥2 concern areas   | Folder `topic/` with `index.md` + 2–5 child pages                               |
| 5,000+ LOC, or ≥3 distinct concern areas  | Folder `topic/` with `index.md` + children; children may themselves be folders  |

Apply it recursively. A 5,000-LOC subsystem split into children of 1,800 LOC
each that themselves cover multiple concern areas must split again. Depth is
not capped — structure matches the code.

Record `scope_loc_estimate` for every section and page. If a section exceeds
1,500 LOC and has `has_overview: false`, that is an error — split it.

### Planning rules

- The **ai** section (always enabled) is a single top-level section
  `wiki/AI/` (`owner_agent: ai`) with a **fixed standalone-complete
  shape**: `index.md`, `invariants.md`, `glossary.md`, and the folders `contracts/`,
  `runbooks/`, `map/`, `reference/` (each a sub-section with its own `index.md`). Plan the
  pages inside those folders from the project's agent-facing surfaces (endpoints, job/queue
  contracts, env/config, common change-tasks, control/data flows, and one concise reference
  page per major area). Size the folders with the scope-to-depth table. The `ai` track is
  always on and must stand alone — plan it so an agent can act without the technical or
  product tracks present. When the `technical` track is **also** enabled, the ai pages
  **link** to it for narrative depth (set `links_to`) rather than restating it; either way
  the ai track keeps its own reference pages. See `specialists/ai.md`.
- Technical sections are **repo-scoped** and live under `wiki/TECHNICAL/`.
  Each repo is a section under that track (e.g. `wiki/TECHNICAL/api/`,
  `wiki/TECHNICAL/client/`). The technical track **always** nests repos
  under `wiki/TECHNICAL/` — a single-repo project still produces
  `wiki/TECHNICAL/<repo>/`, never a repo folder directly under
  `wiki/`. Cross-repo concerns (auth, real-time, type sharing) are
  documented within each repo's section from that repo's perspective — not in
  separate shared pages; any genuinely cross-repo technical page lives directly
  under `wiki/TECHNICAL/`.
- Product sections are **feature-scoped** and live under `wiki/PRODUCT/`.
  Organized by product area, not by code.
- `wiki/index.md` is produced by the orchestrator's
  finalize phase (3e), not by writers. It is never planned as a `pages[]`
  entry in `wiki/.internal/plan.yaml` because it is derived from the rest of
  the wiki, not from `scope_files`. The writer-produced track overviews
  `wiki/AI/index.md` (the ai track machine index) and `wiki/TECHNICAL/index.md`
  (the technical track overview) ARE in the plan.
- Every planned page must be written. Do not plan pages you intend to skip.
- Every `sections[].path` and `pages[].path` MUST start with an enabled track
  folder (`wiki/AI/`, `wiki/TECHNICAL/`, or `wiki/PRODUCT/`). The orchestrator
  never plans pages at the wiki root.
- **Page sizing.** The specialist prompts contain PAGE SIZING guidance — read it
  before planning. Thin pages (< 150 LOC source for technical, < 150 words for
  product) must be merged. Large pages (> 2,000 LOC across unrelated subsystems)
  must be split per the scope-to-depth table. Never plan catch-all pages that group
  unrelated topics. (The ai track is the exception to merging — its `invariants`,
  `glossary`, and folder `index` pages are kept even when small, because they are the
  track's fixed navigational spine.)

### Feature parity check

After drafting sections and pages, cross-reference them. Every major feature area
documented in one section should have corresponding coverage in every other section
where a counterpart is meaningful — but not always. Tag each page's `section_parity`:

- **strict** — counterpart pages must exist in all siblings (e.g. authentication
  exists in api/, client/, and product/).
- **suggested** — counterpart usually makes sense but may not (e.g. a UI-only
  feature may have no api/ counterpart).
- **none** — intentionally one-sided (e.g. client-only accessibility page).

Flag and resolve `strict` gaps before finalizing.

### Scope-file existence check

After drafting `pages[]` but before the self-critique, validate that every
`scope_files` entry actually exists on disk. For glob patterns, expand and
confirm at least one match. Missing paths mean the scan was wrong or the
path is stale — past runs have shipped plans pointing at files that had been
renamed or inlined elsewhere, forcing writers to waste tool calls rediscovering
the real location. Fix the plan before writing it: either correct the path or
remove it. Do not ship a plan that points at nonexistent files.

A one-liner that flags misses:

```bash
for path in $(yq '.pages[].scope_files[]' wiki/.internal/plan.yaml); do
  [ ! -e "$path" ] && [ -z "$(compgen -G "$path" 2>/dev/null)" ] && echo "MISSING: $path"
done
```

### Plan self-critique

Before writing `wiki/.internal/plan.yaml` to disk, generate 6 critiques of the draft plan
answering: (a) what is under-factored (sections that should split), (b) what is
over-factored (pages that should merge), (c) which `strict` parity gaps exist,
(d) which cross-links are missing, (e) which sections exceed 1,500 LOC without a
folder, (f) **coverage**: every file in `wiki/.internal/plan-surface.md` must be assigned
to at least one page's `scope_files` (literal match or glob match). Revise the
plan to resolve each critique, then write it.

### Plan coverage gate (HARD HALT)

After resolving the six self-critiques and BEFORE writing `wiki/.internal/plan.yaml`, run an explicit coverage check against `wiki/.internal/plan-surface.md`:

1. Build the union of all `pages[].scope_files` (expanding globs to concrete file lists).
2. For each file in `wiki/.internal/plan-surface.md`, check whether it appears in that union.
3. Output a coverage report: `unassigned_files: [<list>]` and `coverage_ratio: <percentage>`.

**Halt and surface the unassigned list if any of the following:**

- Any file with LOC ≥ 100 is unassigned (substantial code with no documentation home)
- More than 10% of total surface LOC is unassigned
- Any file in a "high-signal kind" (route, model, screen, agent) is unassigned regardless of LOC

Past runs have shipped plans missing entire 600+ LOC components (e.g. `CourseShell` at 635 LOC) because no coverage gate existed. This gate is non-optional.

Surface the unassigned files to the user with three options per file:
1. **Extend** an existing page's `scope_files` to include this file
2. **Add a new page** for this file (or this file's logical group)
3. **Mark "intentionally undocumented"** with a reason (e.g., "pure config — covered in deployment doc")

Apply the user's decisions, then re-run the coverage check. Only proceed when the unassigned list is empty or fully accounted for.

Present the final plan and wait for confirmation before proceeding to execution.

---

## PHASE 3: EXECUTE

Execute in six ordered sub-phases (3d.5 fires only when Phase 3d produced queued `fail_hard` pages):

1. **3a — Stub-out** (sequential, fast): create `*TODO*` stubs for every planned page.
2. **3b — Technical writers** (parallel, per section).
3. **3c — Product writers** (parallel with 3b, per section).
4. **3d — Verify** (parallel, after all writers finish): run verifier sub-agents
   against every written page; auto-fix `fail_soft` verdicts; escalate
   surviving failures via tier-2 strong verifier; queue any remaining
   `fail_hard` pages for the user gate.
5. **3d.5 — User resolution gate** (sequential, conditional): if Phase 3d
   queued any `fail_hard` pages, halt for batched user resolution (regen /
   patch / shrink / accept / delete / defer) before finalizing. Skipped
   when the queue is empty.
6. **3e — Finalize** (sequential): generate `wiki/index.md`,
   run deterministic checks, then **suggest `/wiki-system
   claude`** (init does not write `CLAUDE.md`). The root
   file is produced from the now-complete reference tree — the
   orchestrator reads the enabled track folders under `wiki/` and
   `wiki/.internal/plan.yaml` to synthesize it. Hand-edit zone markers in the file are preserved
   verbatim.

The stub and verify phases are not optional. Stub-out is what makes parallel
writers safe from broken cross-links and what gives you on-disk resumability.
Verify is what turns "my writer said it" into "my verifier confirmed it."

### Phase 3a — Stub-out (sequential, fast)

Before spawning any writer sub-agents, create an empty file on disk for every page
and section overview listed in `wiki/.internal/plan.yaml`. Each stub OPENS with the
generated-header as its FIRST line (verbatim), then the stub body:

```markdown
> _Generated by wiki-system from source — do not edit here. Run `/wiki-system recheck` to refresh; put durable hand-written notes in an `AUTOREGEN_SKIP` block._

## Purpose

*TODO (scheduled for worker: <owner_agent>)*

## See Also

<relative-path link for each id in links_to>
```

Finalize and deterministic checks IGNORE this generated-header line (it is not a heading, not a link, not content to verify).

This gives every downstream writer three guarantees:

1. Every cross-link target **exists from minute one** — no writer has to worry about
   linking to a page that hasn't been created yet.
2. The folder structure planned in `wiki/.internal/plan.yaml` is materialized on disk; the
   scope-to-depth table is enforced before content is written, not after.
3. A crash mid-run leaves the plan + stubs + partial bodies intact. A resumed run
   re-reads `wiki/.internal/plan.yaml`, scans filesystem for which stubs are still
   `*TODO*`, and dispatches only those.

Stub-out is cheap (one Write per page) and must complete before any writer runs.

### Phase 3b — Technical documentation (parallel by section)

Dispatch writer sub-agents against `wiki/.internal/plan.yaml`. **Parallelism is per-section,
not per-repo.** For a 2-repo, ~15-section project this means ~15 workers, not 2.
See SCALING RULES below for pool sizing.

Each writer gets one section assignment (one top-level or nested section, plus its
direct child pages). Writers are independent — do not share state.

**overview ordering invariant.** A writer responsible for a section with
`has_overview: true` writes its `index.md` LAST, *after* every child page in
that section (and every nested sub-section the overview links to) exists on
disk. Before composing the overview the writer must **read each linked child
page's actual content**, not the plan's `scan_summary`. index.md summarizes
what the children actually say; the plan is orientation only. Past runs have
shipped overviews that contradict their own detail pages because the writer
paraphrased the plan instead of re-reading the children.

**How to delegate each writer:**

1. Read the technical specialist prompt file once (from Configuration) using Read.
2. For each section in `wiki/.internal/plan.yaml` with `owner_agent: technical`, invoke the
   Agent tool with the brief template in SUB-AGENT DELEGATION PRINCIPLES below.

### Phase 3c — Product documentation (parallel with 3b, parallel by section)

Product writers fan out the same way. A product section with `has_overview: true`
gets one writer; each leaf page in `wiki/.internal/plan.yaml` with `owner_agent: product`
and no child pages gets one writer.

Product and technical tracks are independent — dispatch them together at the start
of Phase 3b. The scheduler runs up to N workers from the combined queue (see SCALING
RULES).

### Dynamic splitting: the `split_request` protocol

A writer may discover during its deep scan that its assigned scope is significantly
larger or more heterogeneous than `scope_loc_estimate` implied. Instead of producing
a bloated page or inventing structure the orchestrator doesn't know about, the
writer returns a `split_request` in its final message and writes **nothing else**
for that page:

```yaml
split_request:
  parent_page: <id from plan.yaml>
  reason: "<why the planned scope exceeds limits — cite observed LOC/concern areas>"
  proposed_structure:
    parent_becomes: overview  # the original page converts to <section>/index.md
    children:
      - id: <new slug>
        path: wiki/<TRACK>/<slug>.md
        scope_files: [...]
        scope_loc_estimate: <integer>
        links_to: [...]
      - id: ...
```

The orchestrator's handling is deterministic:

1. Validate the request against the scope-to-depth table (reject if the parent is
   under 1,500 LOC — the writer should just write the page).
2. Patch `wiki/.internal/plan.yaml`: convert the parent page to a section with
   `has_overview: true`, append the children as new pages, cascade `section_parity`
   and `links_to` to children.
3. Stub the new children (Phase 3a repeated for just those files).
4. Re-dispatch the parent (now as an overview writer) plus one writer per child.
5. Continue; no re-plan of the broader wiki.

Writers may request splits recursively: a child writer can itself submit a
`split_request` if its scope turns out to warrant further nesting. Depth is
unbounded — the scope-to-depth table is the only gate.

Writers with `split_allowed: false` in the plan cannot split. Use this for pages
you specifically want kept flat (e.g. a cross-repo integration summary).

### Phase 3d — Verify (MANDATORY — never skipped)

After every writer in Phases 3b and 3c has finished — including any follow-up
writers spawned by `split_request` — dispatch a verifier sub-agent for each
written page. Verifiers are read-only, parallel, and cheap (single page +
its `scope_files`). They catch accuracy issues writers missed.

**Phase 3d is non-skippable on bootstrap runs.** Past runs that skipped 3d on the rationale that "writers self-cite file:line" shipped fabricated file paths (e.g. `rateLimit.ts`, `reviewService.ts`) that didn't exist on disk, plus invented behavioral claims. Writer self-citation is necessary but not sufficient — the verifier confronting prose with source is the only safeguard against confabulation. Do not invent reasons to skip 3d; if you find yourself considering it, that is the bug.

**Verifier specialist:** `specialists/verifier.md`. Read it once at the start of
this phase using the Read tool, then dispatch one verifier per page.

**Which pages get verified.** Every page in the plan, regardless of complexity. Past runs verified only M/L/XL and shipped uncaught fabrications in S-tier pages. The cost is linear in page count and verifiers are cheap relative to writers; verifying all is the right default. The only exception: if the user has explicitly opted out of cost via a runtime flag, verify only `complexity ≥ M` plus all `section_parity: strict` pages — but log a `decision` event recording the cost-driven scope reduction.

**How to dispatch each verifier:**

1. Determine the page's `mode` from its `owner_agent` in `wiki/.internal/plan.yaml`
   (`technical` → `technical` verifier mode; `product` → `product` verifier mode;
   `ai` → `ai` verifier mode — code references allowed, anchor-resolution + entailment
   checked, per `specialists/verifier.md` Step 4b).
2. Build the verifier brief (see SUB-AGENT DELEGATION PRINCIPLES below) and
   invoke the Agent tool.
3. The verifier writes its report to `wiki/.internal/verification/<page-id>.yaml` and
   returns a short message with the verdict.

**Parallelism.** Verifiers share the same worker pool cap (max 10 concurrent).
Dispatch the whole batch at once and collect verdicts as they return.

**Verdict handling.**

| Verdict      | Action                                                                          |
| ------------ | ------------------------------------------------------------------------------- |
| `pass`       | Page is accepted — but see the suspect-pass check below.                         |
| `fail_soft`  | Re-dispatch the original writer **once** with the verifier's `recommendations` list attached to the brief. If the re-run produces another `fail_soft` or worse, escalate to `fail_hard`. |
| `fail_hard`  | Run the tier-2 verifier escalation below (if configured). If still failing, append a structured entry to `wiki/.internal/verification/_failures.md` (see `spec/plan-schema.md` § `_failures.md` SCHEMA) and queue the page for the **Phase 3d.5 user resolution gate**. The run does not advance to Phase 3e until every queued page has a recorded resolution. |

**Suspect-pass check (calibration gate).** A `pass` whose report shows
`stats.resolved == 0` on a `complexity ≥ M` page is suspicious — the verifier
extracted no verifiable claims, which usually means a shallow audit rather than a
genuinely clean page. Re-dispatch the verifier **once**. If it still returns
`pass` with `resolved == 0`, accept the page but record it under a "Low-confidence
passes" heading in `_failures.md` for human spot-check. (S-tier pages legitimately
have few claims — do not gate them.)

**Writer–verifier disagreement (`skipped: true`).** A writer re-dispatched on
`fail_soft` may decline to rewrite and return `skipped: true` + `skip_reason`
(it judged the verifier wrong). Resolver: re-verify once; if the verdict is still
not `pass`, treat the page as `fail_hard` (flag for human review — do not loop),
and record the `skip_reason` in `_failures.md` under "Writer–verifier
disagreements." Repeated disagreements on the same rule/section are a
verifier-calibration signal, surfaced in the run summary.

**Auto-fix re-dispatch brief.** When re-dispatching on `fail_soft`, the writer's
brief gets an additional block:

```
### Previous verification failed (fail_soft)

The previous draft of this page had the following issues. Address each one
and rewrite the full page:

{Paste the `issues` array from wiki/.internal/verification/<page-id>.yaml.
Each issue has: status, severity, claim, page_location, evidence,
recommendation.}

The writer must address every issue in the rewrite. Subsequent verification
will check that each previously-flagged issue is resolved.
```

**No infinite loops.** A page gets at most one auto-fix retry. If the second
verification still fails, the page enters tier-2 escalation below; if tier-2
does not rescue it, mark `fail_hard` and queue it for Phase 3d.5.

**Tier-2 verifier escalation (before declaring `fail_hard`).** When a page is
about to be marked `fail_hard` (the retry's verifier verdict was `fail_soft`
or worse, OR the original verdict carried any `critical` issue), dispatch
**one** additional verifier pass using a stronger-model verifier — see the
`strong_verifier_model` slot in CONFIGURATION. The brief is identical to the
Phase 3d verifier brief; only the model differs. Write its report to
`wiki/.internal/verification/<page-id>.tier2.yaml`.

- If tier-2 returns `pass` → accept the page. Append a "rescued by tier-2
  verifier" line to `wiki/.internal/trace/decisions.md` (calibration signal —
  the base-model verifier was wrong, useful when reviewing verifier prompt
  drift).
- If tier-2 returns anything else → declare `fail_hard` and queue for
  Phase 3d.5.
- If no `strong_verifier_model` is configured (or it equals the base verifier
  model), skip tier-2 — there is no model gap to exploit. The published
  finding this rests on (Kang et al., NAACL 2024 — *Small LMs Need Strong
  Verifiers*) only holds when the verifier is *stronger* than the writer;
  same-model re-verification reproduces correlated errors.

Tier-2 runs at most once per page per run. It does not consume the writer's
retry budget; it is a verifier-only escalation. Pages rescued by tier-2 do
not enter `_failures.md`.

**Oscillation signal.** When recording the queued `fail_hard` entry, compute
whether the issue categories differed between the original verifier report
and the retry's report (status types overlap < 50%, or no overlap in
`issues[].evidence` file paths). If so, set `oscillation_signal: true` in the
entry — it informs the user's resolution choice (writer-flailing pages are
better candidates for `delete_page` or `patch_scope` than another regen).

### Phase 3d.5 — Resolve `fail_hard` pages (USER CHECKPOINT)

If Phase 3d (including tier-2) produced zero queued `fail_hard` pages, skip
this phase entirely and proceed to Phase 3e.

Otherwise, the run is **not complete** until every `fail_hard` page from this
run has a user-recorded resolution. Present the failures to the user in **one
batch** (not per-page interrupts as they occur — research on HITL agent
oversight finds inline prompts reduce reviewer trust and accuracy; batched
end-of-run review with structured choices is the consensus shape).

**Per page, surface to the user:**

- `page_id` and `page_path`
- A summary paragraph: top 1–3 issues from the base verifier report (the
  `claim` + `evidence` excerpts — do not dump the full YAML), the verdict
  reason, whether the page oscillated, whether tier-2 was attempted and what
  it returned
- The resolution menu — offer only the options that apply (see Availability
  column)

**Resolution menu** (per page):

| Option | Effect | Availability |
|---|---|---|
| `regen_with_context` | User provides extra hint or correction. Orchestrator re-dispatches the writer with the prior failure summary + the user's hint, then re-verifies. | Always. |
| `patch_scope` | User specifies files to add or remove from `scope_files`. Orchestrator patches `wiki/.internal/plan.yaml`, re-stubs the page, re-dispatches the writer, then re-verifies. | Always. |
| `scope_shrink_stub` | Orchestrator narrows the page's scope to the verified-clean sections. Dropped sections become a "needs human writeup" stub block fenced by `<!-- AUTOREGEN_SKIP_BEGIN/END -->` markers. | Available when the page has ≥2 distinct `page_location` headings AND ≥1 heading is issue-free. Hidden for atomic pages (no headings) and for pages where every heading carries an issue — those have no clean section to keep. |
| `accept_with_banner` | Page ships as-is. Orchestrator wraps the flagged sections (or the whole page if not localized) in `<!-- AUTOREGEN_SKIP_BEGIN -->` / `<!-- AUTOREGEN_SKIP_END -->` markers with a one-line banner: `> Human-accepted on YYYY-MM-DD despite verifier flag (run <id>).` Future verifiers ignore these blocks per the existing hand-edit-zone rule. | Always. |
| `delete_page` | Page removed from `wiki/.internal/plan.yaml`; file deleted; sibling pages with `links_to` containing this id are patched (link removed) and re-verified per the existing "every modified page re-verified" hard gate. | Always — surface the count of sibling pages that link to it as a ripple warning before the user confirms. |
| `defer` | Explicit defer. Entry stays in `_failures.md` with `resolution.status: deferred` and the date. Run completes; the page ships in its failing state. Next run's R1 surfaces deferred entries with priority. | Always. |

**Re-dispatch budget after user action.** For `regen_with_context` and
`patch_scope`, the writer + verifier run **once**. If the page still fails,
**do not re-prompt the user** — record the final verdict as
`fail_hard_post_user` in the entry's `resolution.outcome_verdict` and ship
the page in whatever state it's in. The original "no infinite loops" rule
applies to user-initiated rewrites too. The user can re-run the skill if
they want another attempt; gate-time looping is exactly what the cap forbids.

**`delete_page` ripples.** Patching sibling `links_to` may break the page
graph (a sibling losing its only outbound link becomes an orphan). The
orphan check runs in Phase 3e — it will surface any orphans created here.
Do not block the gate on this; orphans are a finalize-phase concern.

**`accept_with_banner` durability.** The banner block must be wrapped in
`<!-- AUTOREGEN_SKIP_BEGIN -->` / `<!-- AUTOREGEN_SKIP_END -->` markers so
(a) writers preserve it verbatim on future regens, (b) verifiers skip claim
checks inside it. Future runs will NOT re-flag accepted blocks.

- **Localized accept** (only the flagged sections wrapped): the rest of the
  page continues to be verified normally. Set `resolution.accepted_until:
  null` in the `_failures.md` entry.
- **Whole-page accept** (no localizable issues — the entire page wrapped):
  the page becomes effectively unverifiable. To prevent permanent dead
  zones, **require** `resolution.accepted_until: <ISO date>` (default
  prompt: today + 180 days). When the date passes, Phase R1 surfaces the
  entry as a re-review candidate alongside deferred entries. The user can
  re-accept (extending the date) or pick a different resolution.

**`delete_page` is a structural change.** A `delete_page` resolution must
force Phase 3e finalize to run even under the no-changes shortcut. Record
this in the run's structural-changes ledger so R5.2 (in recheck) does not
skip root-artifact regeneration. `index.md` is
regenerated from the now-current track folders under `wiki/`, which naturally
drops any link to the deleted page.

**`delete_page` ripple bound.** Sibling re-verification after a delete may
itself produce new `fail_hard` verdicts. Cap ripple re-verification at
**one round per gate sitting**: any new `fail_hard` produced is appended
to `_failures.md` with `verdict_reason: "ripple from delete_page <id>"`,
`resolution.status: deferred`, `resolution.user_note: "auto-deferred —
created mid-gate, not interactively triaged"`, and surfaced loudly in the
run summary. The user addresses ripple-deferred entries on the next run.
This avoids re-presenting an updated gate batch mid-sitting (UX trap) and
preserves the run-completion invariant.

**Bulk-defer warning.** If the user resolves ≥3 entries as `defer` OR
≥50% of the queue as `defer` (whichever fires first), emit a prominent
warning in the run summary: "N of M failures deferred — this is the
silent-accumulation risk the gate is designed to surface." Append a
`bulk_defer: N of M, run <id>` line to `wiki/.internal/trace/decisions.md`.
The run still completes (defer is terminal) but the bulk pattern is
visible. Repeated bulk-defer runs are a calibration signal — either the
verifier is over-strict or the documentation is genuinely under-resourced.

**Decision-log entries.** At the end of Phase 3d.5, for every entry
closed this gate, append one line to `wiki/.internal/trace/decisions.md`:
`<run_id>  <page_id>  resolution=<status>  outcome=<outcome_verdict>`.
This is the audit trail for what the user chose; the issue detail stays
in the `_failures.md` entry.

**`fail_hard_post_user` disk state.** When a `regen_with_context` or
`patch_scope` retry produces another `fail_hard`, the page on disk is the
**writer's last output** — the rewrite overwrote the prior content (full
rewrites only, by writer policy). Users who want to preserve the prior
content should choose `defer` (no re-dispatch) rather than
`regen_with_context`. Document this in the gate UI when offering the
menu.

**Tier-2 dispatch failure.** If `strong_verifier_model` is configured but
the dispatch errors out (model unavailable, rate limit, network), do not
silently swallow it. Treat as `tier2_verdict: not_run`, include the
failure reason in the `_failures.md` entry's `verdict_reason`, append a
line to `wiki/.internal/trace/decisions.md`, and proceed to the gate. The
user sees that tier-2 didn't run and why.

**Prior-deferred re-fail.** When this run's verifier produces a fresh
`fail_hard` for a page that has a prior `_failures.md` entry with
`resolution.status: deferred`, **append a new entry** for this run — do
not mutate the prior entry. The gate surfaces both side-by-side so the
user can see whether it's the same failure mode (defer again or escalate
to a different resolution) or a new one (failure has shifted, prior
deferral no longer applies).

**Updating `_failures.md`.** After every resolution decision, the
orchestrator updates the entry's `resolution.*` fields in place per the
`_failures.md` schema. This is the only mutation allowed on a closed entry.
The page-summary prose below the frontmatter is never rewritten.

**Skill-execution context.** "Present to the user" means an
`AskUserQuestion`-style structured prompt presented by the orchestrator at
gate time. The orchestrator is itself an agent running in Claude Code — the
gate is implemented as a synchronous pause in the orchestrator's reasoning,
not as a separate process or queue.

### Phase 3e — Finalize (after Phase 3d, and Phase 3d.5 if it ran)

**1. Generate `wiki/index.md`** — the human table of contents

Synthesize the wiki's entry point from the now-complete reference tree.
`wiki/index.md` is the human table of contents; it lists ONLY enabled tracks
(a track with no folder on disk is never mentioned). Its FIRST line is the
generated-header (verbatim):

```
> _Generated by wiki-system from source — do not edit here. Run `/wiki-system recheck` to refresh; put durable hand-written notes in an `AUTOREGEN_SKIP` block._
```

Read `wiki/.internal/plan.yaml` and the on-disk track folders under `wiki/`
(`wiki/AI/`, `wiki/TECHNICAL/`, `wiki/PRODUCT/` — only those present) to produce:

- One-paragraph product description (from CONFIGURATION or inferred from the scan)
- **Audience guidance** — a brief paragraph on who reads which enabled track
  (e.g., AI agents → the `ai` track at `wiki/AI/` — start at its
  `index.md`; developers → technical reference; product/leadership → product
  reference). Only mention tracks that are enabled.
- System architecture summary — how repos relate (brief; Mermaid diagram
  if helpful)
- Links to every enabled top-level track folder under `wiki/` (`wiki/AI/`,
  and `wiki/TECHNICAL/` / `wiki/PRODUCT/` if enabled)
- Quick reference table: build/run/test commands per repo (from CONFIGURATION)

If the existing `wiki/index.md` contains content between
`<!-- AUTOREGEN_SKIP_BEGIN -->` and `<!-- AUTOREGEN_SKIP_END -->` markers,
preserve those blocks verbatim — only the auto-generated sections are
rewritten. If the file is entirely wrapped in skip markers, leave it
untouched (the project has opted out of auto-generation for this file).

**2. Cross-link + structural verification**

Run four deterministic checks:

- **Link graph.** Walk every `.md` under `wiki/`, parse markdown links, assert each
  relative target resolves to an existing file. Report broken links; fix.
- **Orphan check.** Every page must link to at least one other page AND be linked
  from at least one other page (except `wiki/index.md`,
  which is the root entry point). Flag orphans; add links.
- **Parity check.** For every page with `section_parity: strict`, verify each
  sibling section contains a counterpart page. Report gaps; either add the missing
  page (via a dispatched writer) or downgrade the parity tag with justification.
- **Mandatory-heading check (completeness floor).** Every reference page has a
  `## Purpose` heading (`grep -L '^## Purpose' wiki/{AI,TECHNICAL,PRODUCT}/**/*.md`). A page
  missing it is incomplete — re-dispatch its writer. This is only the deterministic
  floor; the substantive, content-conditioned completeness audit (does the page
  cover its `scope_files`? does it have the sections its content warrants?) is the
  verifier's Step 3b (`specialists/verifier.md`), which emits `omission` issues.

**3. Suggest `/wiki-system claude` — do NOT write `CLAUDE.md` here**

`CLAUDE.md` is owned by the dedicated `/wiki-system claude` command
(`claude-md.md`), which is the **only** command that writes it. `init` does not
create or edit `CLAUDE.md` — keeping documentation an on-request act, and the
`CLAUDE.md` standard in one place.

When the wiki is finalized, tell the user:

> The wiki is generated. To create or refresh `CLAUDE.md` from it, run
> `/wiki-system claude`.

(See `claude-md.md` for the file's structure, the ≤200-line lean standard, and the
on-request docs policy it bakes in.)

**4. Maintain the decision log (`wiki/.internal/trace/decisions.md`)**

This is the append-only run history that keeps `CLAUDE.md` and the wiki pages
free of run narrative. It is referenced as the destination for run-level history
throughout this skill, so it must actually be written.

Start each run's entries with a **run header** that records the provenance:

```
## <mode> run <ISO-8601 timestamp> — generator: wiki-system v<N> · <model-id>
```

`generator_version` (skill version from the `VERSION` file + the model id) is load-bearing
for recheck: it lets a later run tell "the source drifted" apart from "this was
produced by an older skill/model." Then append one line per **material decision**,
as the decision is made across the run (not only at finalize). Format:

```
<ISO-8601 timestamp> · <phase> · <decision> · <one-line rationale>
```

Log at least: plan approved (Phase 2), each accepted `split_request` (3b/3c),
each `section_parity` downgrade, each coverage-gap deferral (R2.4 in recheck),
any cost-opt-out verify-scope reduction (3d), every `fail_hard` escalation, and
every writer `skipped: true` disagreement. Do not log routine passes. At finalize,
confirm the log covers this run's material decisions; it is append-only across
runs (never truncate prior history). The decision log is **orchestrator-written
only** — sub-agents return decisions in their result and the orchestrator appends
them; sub-agents never write the log concurrently (it is the one shared append
target, and concurrent appends would corrupt it).

**5. Run-level diagnostics (advisory — surface, don't gate)**

Two cheap meta-signals computed from this run's verifier reports, written to the
final run summary (and the notable ones appended to `decisions.md`). Neither
blocks the run.

- **Loop-friction per section.** Tally, per section, the pages that needed an
  auto-fix retry, ended `fail_hard`, or triggered a writer↔verifier disagreement
  (`skipped: true`). The sections with the most friction are the "hard" areas —
  surface the top few so the human knows where the docs (or the code) are
  thorniest and where to look first next run.
- **Rubric critique (framework-level).** Read across this run's verifier reports
  and ask the one question a per-page verifier cannot: *is there a systematic gap
  the rules don't catch?* — e.g. many pages share the same `omission` (a coverage
  rule may be too weak), one severity tier consistently over- or under-fires, or a
  whole section under-documents failure paths. If you find one, write a single
  grounded, advisory recommendation ("consider strengthening rule X for
  <page-type>") and cite the reports; if nothing systematic stands out, say so in
  one line. Keep this grounded in the on-disk reports — never free-form reflection.

---

## SCALING RULES

Parallelism is **per-section**, not per-repo. Each section in `wiki/.internal/plan.yaml`
maps to one writer; each leaf page under a section maps to one writer unless
the section writer produces them itself.

Worker pool sizing:

| Total sections in plan | Max concurrent writers |
| ---------------------- | ---------------------- |
| ≤ 6                    | All in parallel        |
| 7–15                   | 5                      |
| 16–30                  | 8                      |
| 31+                    | 10                     |

Do not exceed 10 concurrent writers. Above that, coordination overhead and
context-poisoning risk outweigh parallelism gain. Past this point, scale by
deepening the hierarchy (let section writers dispatch their own page writers),
not by widening the pool.

AI, technical, and product writers share the same pool — dispatch all enabled tracks at the
start of Phase 3b. The scheduler fills slots from the combined queue.

The same 10-concurrent cap applies to any parallel sub-agent batch, not just
writers — including the **Phase 1 scan agents** (one per repo/package) and the
Phase 3d verifiers. For a repo count at or below the cap, dispatch one scan agent
per repo at once; for a monorepo with more top-level packages than the cap, batch
them.

---

## SUB-AGENT DELEGATION PRINCIPLES

The orchestrator dispatches two kinds of sub-agents: **writers** (Phases 3b
and 3c) and **verifiers** (Phase 3d). Both kinds receive their specialist
prompt inline plus a short assignment block. Briefs are deliberately short —
the authoritative spec lives in `wiki/.internal/plan.yaml`, which agents read directly.

### Writer brief

```
[Full text of the <technical|product> specialist prompt]

---

## YOUR ASSIGNMENT

You are writing documentation for one section of a larger wiki. The orchestrator
has already scanned the project and produced a structured plan; read it first.

**Objective:** produce every page under your section id — complete, verified
against source, and cross-linked — so it passes verification on the first try.

**Plan file:** wiki/.internal/plan.yaml  — authoritative; read fully before doing anything else
**Your section id:** <section id>
**Your output paths:** write to the paths listed under your section's pages
**Do not touch `CLAUDE.md`** — `init` never writes it; it is owned by the separate `/wiki-system claude` command.

### Cross-repository context
{2–5 lines for OTHER repos — only what this section needs to document its
integration points. For each relevant repo give: the integration direction (who
calls whom), the shared contract (endpoint/event/type), and the sibling page id
to cross-link. Do not paste full scan summaries.}

### Your scope
- Read every file listed in scope_files for your section's pages.
- **Match effort to the page's `complexity` in the plan.** `S`: read the
  scope_files once, document what's non-obvious — don't over-produce. `M`: read
  fully, trace the main flows. `L`/`XL`: trace every flow function-by-function,
  enumerate every count from source, and apply the paste-the-line test to each
  behavioral claim — these pages carry the most fabrication risk, so spend the
  tool calls. Under-investing on an L/XL page is the #1 cause of fail_hard.
- Follow the PAGE SIZING guidance in the specialist prompt.
- If during your deep scan you find the scope warrants more structure than
  `wiki/.internal/plan.yaml` allocates, DO NOT freelance — return a `split_request` as
  described below. The orchestrator will patch the plan and re-dispatch.

### Cross-section links
Every id listed under `links_to` in your section already has a stub file at the
path given in `wiki/.internal/plan.yaml`. Use relative paths from the wiki root
(e.g., `../client/authentication.md`). Do not link to ids not in the plan.

For each `links_to` target, the brief includes a one-line hint — its page title
and what it documents (drawn from the plan: the target's title + the gist of its
`scope_files`). Use these to describe integration points accurately ("auth is
handled by [Authentication](../api/authentication.md), which covers the JWT
middleware") **without reading the target's source** — that source is out of your
scope. This is what keeps each writer's reading confined to its own `scope_files`
while still letting it describe how its section connects to others. If a hint is
insufficient to state an integration claim precisely, link to the target and keep
the claim general rather than guessing at the other page's internals.

{Orchestrator: when building this brief, emit one line per `links_to` id —
`<page-id> — "<title>": documents <1-line scope gist>` — from the plan. Do not
paste the target pages' bodies.}

### If your scope exceeds the plan — `split_request`
If your page's true scope exceeds 1,500 LOC across distinct concern areas,
STOP writing and return a final message containing ONLY this YAML block:

    split_request:
      parent_page: <your page id>
      reason: "<observed LOC / concern areas>"
      proposed_structure:
        parent_becomes: overview
        children:
          - id: <slug>
            path: wiki/<TRACK>/<slug>.md
            scope_files: [...]
            scope_loc_estimate: <integer>
            links_to: [...]

Do not write the parent page when requesting a split. The orchestrator will
re-dispatch you as the parent overview writer after children are done.

### Definition of done (self-check before returning)
- [ ] Every page under your section id is written (no stubs left), OR a `split_request` was returned instead.
- [ ] Every file in your pages' `scope_files` was read.
- [ ] Every count/number was enumerated from source, not estimated or taken from `scan_summary`.
- [ ] Every `links_to` target is cross-linked with a working relative path.
- [ ] Product pages only: zero code references.

### Output summary
At the end of successful writing, return a brief summary listing pages written,
any `split_request` issued, integration points documented, and any
`cross_section_ripples` (sibling pages your changes may affect).
```

### Verifier brief

Dispatched in Phase 3d, one per page that requires verification.

```
[Full text of the verifier specialist prompt — specialists/verifier.md]

---

## YOUR ASSIGNMENT

You are verifying a single drafted wiki page against the source files the writer
was given. Read the verifier prompt above for your process, rules, and output
format.

**page_id:** <slug from wiki/.internal/plan.yaml>
**page_path:** <absolute path to the draft .md file>
**mode:** technical | product | ai   (from the page's owner_agent)
**scope_files:** <array of absolute or repo-relative paths>
**plan_path:** wiki/.internal/plan.yaml
**report_path:** wiki/.internal/verification/<page-id>.yaml

### If this is a re-verification after fail_soft
{Include the previous verification report's issue list here so you can confirm
each previously-flagged issue has been addressed in the rewritten page.}

### Reminder of verdicts (severity tiers: consideration | improvement | critical)
- pass       — 0 critical AND 0 improvement issues (any number of consideration tolerated)
- fail_soft  — 1–3 improvement issues, 0 critical; orchestrator will auto-fix once
- fail_hard  — 4+ improvement issues OR any critical issue; orchestrator escalates to a tier-2 verifier (if configured), then queues for the Phase 3d.5 user resolution gate if not rescued

Emit your YAML report to report_path, then return a final message (≤10 lines)
with the verdict and top issues.
```

**Re-verification after an auto-fix.** When a writer is re-dispatched on
`fail_soft`, the verifier that checks the rewrite gets the prior
verification report in its brief. This lets it confirm each flagged issue
is resolved, not just check the page fresh.

### Principles behind the briefs

- **Plan-first**: the plan file is the single source of truth. Do not inline page
  lists or scan summaries into briefs — point agents at `wiki/.internal/plan.yaml`.
- **Minimal context**: writers need their own section scope + short cross-repo
  summary + the plan. Verifiers need just the page, its source files, and the
  plan. Nothing else.
- **Explicit split protocol**: writers have one well-defined escape hatch
  (`split_request`), not vague "adjust the structure as needed" permission.
- **No duplicate scanning**: orchestrator scanned in Phase 1; writers scan their
  assigned `scope_files` deeply; verifiers re-read the same `scope_files` but
  nothing broader. Nobody re-does anyone else's work.
- **Separation of concerns**: writers produce content; verifiers produce
  reports. A verifier that rewrites is broken. A writer that auto-verifies is
  compromised by the conflict of interest — that's why the split exists.
- **Independent output**: each writer produces complete pages. Each verifier
  produces one YAML report. No merging step at either layer.

---

## QUALITY GATES

Run these checks before marking a phase complete. The first five are
deterministic (a script, not a judgment call) — do not skip them. Verification
results come from Phase 3d's verifier sub-agents.

- [ ] **Plan validation.** `wiki/.internal/plan.yaml` parses as YAML, matches the schema
      in `spec/plan-schema.md`, and every page's `path` resolves to a real file
      under an enabled track folder (`wiki/AI/`, `wiki/TECHNICAL/`, or `wiki/PRODUCT/`).
- [ ] **Plan scope invariant.** Every `sections[].path` and `pages[].path` starts
      with an enabled track folder (`wiki/AI/`, `wiki/TECHNICAL/`, or
      `wiki/PRODUCT/`). No planned entry references the wiki root.
- [ ] **Track coverage.** `meta.tracks` is non-empty (and always contains `ai`),
      and for **every** enabled
      track `pages[]`/`sections[]` contain at least one entry with that
      `owner_agent` and the track's folder appears in `sections[].path`
      (`wiki/AI/`, `wiki/TECHNICAL/`, `wiki/PRODUCT/`).
      Conversely, no page has an `owner_agent` that is **not** in `meta.tracks`. A
      plan with zero entries for an enabled track — or entries for a disabled one —
      is a planning bug: halt before stub-out and re-plan. Confirm e.g.
      `grep -c "owner_agent: ai" wiki/.internal/plan.yaml` ≥ 1 when `ai` is enabled.
- [ ] **Link graph.** Every relative link in every `.md` resolves to an
      existing target. Report in `wiki/.internal/link-report.md`.
- [ ] **Orphan check.** Every page (except `wiki/index.md`)
      is both outbound-linked and inbound-linked at least once.
- [ ] **Product code-reference linter.** No file under `wiki/PRODUCT/`
      contains backticked PascalCase identifiers, `.ts`/`.tsx`/`.js`/`.py`
      path patterns, `/api/...` URL shapes, or HTTP verb keywords
      (GET/POST/PUT/DELETE/PATCH). (Applies to `PRODUCT/` only — the `ai` and
      `technical` tracks allow code references.)
- [ ] **AI-track integrity** (always — `ai` is always enabled). `wiki/AI/index.md` exists
      and every other `AI/` page is reachable from it (directly or via a folder
      `index.md`) — it is the agent's front door. Every `AI/` page has a
      `## Provenance` line. **Cross-track dedup (advisory, not a hard gate):**
      surface any `AI/` page whose prose substantially overlaps a `TECHNICAL/` page
      it should instead link to — near-duplicate content is a retrieval distractor.
      Anchor accuracy (every `(path:line)` resolves and entails) is the verifier's
      Step 4b, not a deterministic gate here.
- [ ] **Numeric consistency.** For every integer that appears followed by the
      same domain noun in multiple pages, all occurrences must use the same
      value. Mismatches indicate numeric drift between writers and must be
      reconciled before finalize completes. Past runs have shipped `33 endpoints`
      on the overview and `32 endpoints` on the routes page. Derive the noun set
      from this project's own wiki rather than a fixed list — surface every
      "<number> <noun>" pair and group by noun:
      `grep -rnhoE '\b[0-9]+\s+[a-z][a-z-]+' wiki/AI/ wiki/TECHNICAL/ wiki/PRODUCT/ | sort | uniq -c | sort -rn`
      then check pages that cite the same noun agree. (Tune the pattern to the
      project's vocabulary; the earlier fixed noun list was Strive-specific.)
- [ ] **Plan coverage.** Every page in `wiki/.internal/plan.yaml` was written (no
      skipped pages; no pages outside the plan unless recorded via a resolved
      `split_request`).
- [ ] **Completeness floor.** Every reference page has its mandatory `## Purpose`
      heading (deterministic check, Phase 3e step 2). Substantive completeness —
      whether each page covered its `scope_files` and has the sections its content
      warrants — is enforced by the verifier's Step 3b `omission` issues flowing
      through the verdict (no separate gate needed).
- [ ] **Verification coverage.** Every page has a report at
      `wiki/.internal/verification/<id>.yaml` (per Phase 3d, all pages are
      verified by default). If the run used the cost-opt-out scope, every page
      with `complexity` ≥ M plus every `section_parity: strict` page has a report.
- [ ] **Verification verdicts.** No page carries a `fail_soft` verdict that
      was not auto-fixed and re-verified. Every `fail_hard` page from this
      run has a recorded user resolution (`regen_with_context` / `patch_scope` /
      `scope_shrink_stub` / `accept_with_banner` / `delete_page` / `defer`)
      in its `_failures.md` entry. Entries with `resolution.status: pending`
      block this gate. `fail_hard_post_user` (a user-initiated re-attempt
      that also failed) is a valid terminal state and does **not** block the
      gate.
- [ ] **Parity.** Every page with `section_parity: strict` has existing
      counterparts in all sibling sections.
- [ ] **Technical grounding.** Technical docs reference specific files,
      functions, and code patterns. Counts and thresholds are source-verified
      (the verifier confirms this in Phase 3d).
- [ ] **Root artifacts.** `wiki/index.md` was generated (or refreshed) by
      Phase 3e finalize. It exists, opens with the generated-header, and links to
      every enabled top-level track folder under `wiki/`. (`CLAUDE.md` is **not** part of
      init — suggest `/wiki-system claude` to (re)generate it.)

---

## CONSTRAINTS

- **CWD discipline.** Capture the orchestrator's starting working directory at run start (`pwd`) and treat it as the immutable project root for the entire run. Never `cd` in shell commands the orchestrator itself runs — use absolute paths or paths relative to the captured root. Sub-agents (Explore, writers, verifiers) MUST also receive absolute paths in their briefs and must not rely on shell `cd` state. Past runs ended up with the orchestrator's CWD drifted into `client/` mid-run, after which `ls api/src/` returned "No such file or directory" because the relative path no longer matched. If you find a sub-agent's bash output suggests CWD has changed, stop and re-establish from the captured root before continuing.
- The orchestrator plans, stubs, writes, and verifies pages **only under the
  enabled track folders** (`wiki/AI/`, `wiki/TECHNICAL/`, `wiki/PRODUCT/`).
- In the finalize phase (3e), the orchestrator additionally produces
  `wiki/index.md` from the completed reference tree.
  (It does **not** write `CLAUDE.md` — that is the `/wiki-system claude`
  command.) This is NOT a writer
  page and does not appear in `wiki/.internal/plan.yaml`. The root file honors the
  hand-edit zone protocol — content between `<!-- AUTOREGEN_SKIP_BEGIN -->`
  and `<!-- AUTOREGEN_SKIP_END -->` markers is preserved verbatim. A file
  entirely wrapped in skip markers is left untouched.
- Writers must preserve content between `<!-- AUTOREGEN_SKIP_BEGIN -->` and
  `<!-- AUTOREGEN_SKIP_END -->` markers verbatim. The orchestrator instructs
  writers to never modify content inside these markers; verifiers treat the
  content inside as authoritative and skip claim verification there.
- The verifier is the first-line quality gate. There is no per-page
  human-confirm step inside Phase 3d; the human checkpoint is the batched
  Phase 3d.5 gate, which fires only when at least one page reaches
  `fail_hard` after tier-2 escalation. Verdict semantics:
  - `pass` — page is accepted as-is.
  - `fail_soft` — orchestrator re-dispatches the writer once with the issue
    list. Re-verify. If still `fail_soft` or worse, run the tier-2 verifier
    (if configured); if tier-2 does not return `pass`, escalate to
    `fail_hard`.
  - `fail_hard` — page enters the Phase 3d.5 user resolution gate. The run
    does not complete until the user records a resolution (regen / patch /
    shrink / accept / delete / defer) for every `fail_hard` page from this
    run.
- `wiki/.internal/plan.yaml` must exist on disk and be approved before Phase 3 begins
- The plan must match the schema in `spec/plan-schema.md` and satisfy every
  invariant listed there
- No writer runs before stubs exist for every page it links to
- No parent section index.md is written until all its child pages are done
- No verifier runs before its assigned page's writer has finished
- No page receives more than one auto-fix retry after a `fail_soft` verdict. User-initiated rewrites at the Phase 3d.5 gate are likewise bounded to one — a `regen_with_context` or `patch_scope` that still fails terminates as `fail_hard_post_user` and is not re-prompted in the same run
- Tier-2 verifier escalation runs at most once per page per run; it is a verifier-only escalation and does not count against the writer's retry budget
- Sub-agents follow their specialist prompt fully — the orchestrator does not override
  the specialist prompt's process, quality criteria, or writing standards
- Writers that discover their scope exceeds the plan return a `split_request` and
  write nothing else for that page; they do not freelance structural changes
- Verifiers never rewrite, edit, or add content — they only produce YAML reports
- When updating existing documentation, always rewrite full pages — never append
- If something is unclear from the codebase, note it as unknown rather than guessing
- The orchestrator prompt (this file) never needs project-specific changes beyond the
  Configuration section at the top
