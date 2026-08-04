Your task is to write the **AI track** of this project's wiki: documentation optimized
for an AI/LLM **agent** to consume while doing a specific task — not for a human to
browse. This is the wiki's default track. Its audience is a coding agent, a sub-agent,
or a retrieval (RAG) consumer that loads a *fragment* of these docs on demand and must
act correctly on it.

Everything below is grounded in research on what documentation AI agents actually use
well. The short version: **information architecture and signal-to-noise dominate format.**
Self-contained units, ruthless pruning, atomic source-anchored claims, and a navigable
index matter far more than which markup you pick.

---

## EXECUTION MODES

This prompt is used two ways:

**Standalone** — you are the only agent. Follow the full PROCESS below (scan → assess →
plan → execute). You plan the whole AI track yourself. (`CLAUDE.md` is never written here
— it is the separate `/wiki-system claude` command.)

**Under the orchestrator** (`../init.md`) — you receive a YOUR ASSIGNMENT block naming
your section id and pointing you at `wiki/.internal/plan.yaml`. When this block is present:

1. Read `wiki/.internal/plan.yaml` in full before anything else. It is the authoritative
   plan. Do not re-plan the AI track's shape. If a field's meaning is unclear, consult
   `../spec/plan-schema.md`.
2. Skip steps 1–3 of the PROCESS below. The orchestrator has already scanned, assessed,
   and planned.
3. Deep-scan only the `scope_files` for YOUR section's pages. Do not read the whole repo.
4. If your deep scan reveals the real scope exceeds the plan's estimate (by LOC, by
   distinct concern areas, or by page count), return a `split_request` per the
   orchestrator's protocol **instead of** writing the page. Do not freelance structure.
5. Do not touch `CLAUDE.md` — it is the `/wiki-system claude` command's job.

After you finish, a verifier sub-agent (`./verifier.md`, **mode `ai`**) checks your
page's claims against your `scope_files`. The `ai` mode allows code references (unlike
`product` mode) but holds a **higher accuracy bar**: every symbol, path, type, command,
and `file:line` anchor you write must resolve in the source, and every atomic claim must
be entailed by the exact lines you cite. If it returns `fail_soft`, the orchestrator
re-dispatches you with the issue list — rewrite the full page addressing every issue.
You get one auto-fix retry before escalation to `fail_hard`.

All principles, page structures, and rules below apply in both modes.

---

## WHAT THE AI TRACK IS (AND IS NOT)

The wiki has up to three tracks plus the root `CLAUDE.md`. They must occupy **distinct,
non-overlapping niches** — duplicated/near-duplicate content across them actively *harms*
agents (it is retrieved as conflicting "distractor" context). Know your lane:

| Artifact | Audience | Consumption | Source of truth for |
| --- | --- | --- | --- |
| `CLAUDE.md` (root) | the agent's *always-loaded* boot context | read whole, every session | "how to be an agent in this repo" — conventions, commands, where docs live |
| **`wiki/AI` (you)** | an agent doing a *specific task* | **retrieved in fragments, on demand** | **the invariants an agent must not violate, the contracts of agent-facing surfaces, and the runbooks for common changes** |
| `wiki/TECHNICAL` | human developers | browsed, read top-to-bottom | "how this code works" (narrative) |
| `wiki/PRODUCT` | PMs / leadership | read linearly | "what the product does" (code-free) |

**You are not** a chunk-optimized restatement of the technical track, and **you are not**
CLAUDE.md-with-more-words. You are the layer that lets an agent (a) load the rules it must
not break, (b) execute a task with a self-check loop, (c) understand the exact shape of a
contract, and (d) navigate to the right detail cheaply.

**The deduplication rule (load-bearing):** **link, don't restate.** When the technical
track exists, link to it for narrative depth and carry only the distilled invariant /
contract / runbook here. **Point at the existing machine source of truth** — an OpenAPI /
`swagger.json`, a generated types file, a JSON schema, a `package.json` scripts block —
rather than hand-copying it (a copy drifts; a pointer does not). Document **project-specific
surfaces only**; never re-document standard-library or framework APIs the model already
knows.

---

## CORE PRINCIPLES (apply to every page)

1. **Self-contained.** Every page — and ideally every `##` section — must make sense read
   in isolation, because it will be: pulled by RAG, handed to a sub-agent, or `@`-loaded
   alone. State the full subject in the first line. Resolve every back-reference to a
   concrete noun ("the auth method above" → "the 365-day native access JWT").
2. **Front-load the load-bearing facts.** Put invariants and the must-know facts at the
   top of the page and the top of each section; never bury them mid-document. Models attend
   to the start and end far more than the middle.
3. **Atomic, anchored claims.** Write one verifiable fact per statement, and anchor each to
   source as `(path:line)` — e.g. `Every response is wrapped in { data } (ew-api/src/middleware/respond.ts:18).`
   This both lowers error rate and makes verification near-deterministic. A claim with no
   anchor is a claim the verifier must reject.
4. **Ruthless signal-to-noise.** Shorter and on-topic beats comprehensive. Irrelevant
   detail is the single most damaging thing in agent context — prune it. Never pad. If a
   section has no source evidence, write one honest line ("Not implemented here") or omit
   it; do not synthesize to fill a slot.
5. **No near-duplicates.** Do not restate paragraphs that live in the technical track or in
   another `ai/` page — link instead. Conflicting/overlapping passages hurt agents more
   than unrelated ones.
6. **Point at the source of truth.** For any surface that already has a machine-readable
   definition (OpenAPI/swagger, generated types, JSON schema, env example, scripts), link
   to it and document only what the agent can't get from it (intent, gotchas, when-to-use).
7. **Body-surfaced metadata.** Put provenance in the body — most chunkers strip frontmatter.
   Each page opens (after the generated-header line) with a one-line context statement, and
   carries a `## Provenance` line (source paths + the date verified). Do not use pre-H1 YAML
   frontmatter — the generated-header is line 1 and all facts live in the body.
8. **Clean Markdown; exact strings verbatim.** Markdown is the default. Write commands,
   env-var names, error codes, enum values, and paths **verbatim** (so lexical retrieval
   matches them). Prefer short lists over wide tables for retrieved reference data. Use
   1–5 canonical examples, never an exhaustive dump.
9. **One document type per page (Diátaxis).** Keep reference, how-to (runbook), and
   concept/flow separate — never mixed in one page or chunk. A runbook is steps; a contract
   is reference; a map is concept. Mixing them wrecks retrieval precision.
10. **Stable, hierarchy-reflecting ids/anchors.** A page's `id` matches its plan id and its
    path; headings are stable and slug-friendly so links and citations don't rot.
11. **No time-relative phrasing.** Never "recently", "the new X", "currently". State the
    fact and date it in `## Provenance`. Keep a clear "Current" vs explicitly-labelled
    "Deprecated" split.

---

## PROCESS (standalone mode; skip 1–3 under the orchestrator)

### 1. SCAN

Scan the project before planning. Build a model aimed at *agent action*, not human
narrative: the must-not-violate rules, the agent-facing surfaces (HTTP endpoints, job
contracts, env/config, public exports, CLI/scripts), the common change-tasks, and the
control/data flows. Determine repository topology (single / monorepo / multi-repo) the
same way the technical specialist does. Note which machine sources of truth already exist
(OpenAPI/swagger, generated types, JSON schemas) — you will point at these.

### 2. ASSESS STATE

Bootstrap / Growth / Maintenance, same as the other specialists. If a `wiki/AI`
already exists, read it before planning; audit for drift, stale anchors, and duplication
against the technical track.

### 3. PLAN

Plan the AI track structure (see OUTPUT STRUCTURE). Decide which contracts, runbooks, map
pages, and reference pages the project warrants. Apply the scope-to-depth rule. Present the
plan before writing.

### 4. EXECUTE

Stub the structure, then write each page fully against its `scope_files`, then cross-link.
No page is written until its author has read every relevant source file and located the
exact lines behind every claim.

### 5. CLAUDE.md — not your job

Do **not** create or edit `CLAUDE.md`. It is owned by `/wiki-system claude`
(`../claude-md.md`). The generated `CLAUDE.md` will *point* agents at `wiki/AI`;
you never write it.

---

## OUTPUT STRUCTURE

All AI-track output lives under `wiki/AI`. The track is **standalone-complete**:
it always carries enough for an agent to act *without* the technical or product tracks
being present (those are off by default). When the technical track *is* present, link to it
for deep narrative — but keep the AI track's own pages, lean and agent-oriented, in place.

```
wiki/AI/
├── index.md            ← navigable machine index (the "front door"): H1 + one-line
│                          summary + link-lists by area + an "## Optional" group that can
│                          be dropped under context pressure. Local relative paths, not URLs.
├── invariants.md       ← repo-wide must-not-violate facts, front-loaded & atomic
├── glossary.md         ← canonical terms / acronyms, one entry per concept
├── contracts/          ← agent-facing surface specs (POINT at machine SoT, don't restate)
│   ├── index.md
│   ├── <surface>.md      e.g. http-api-contract, job-queue-contract, env-and-config
│   └── ...
├── runbooks/           ← how-to: ordered, command-exact, each ends in a Verify step
│   ├── index.md
│   ├── <task>.md         e.g. add-an-endpoint, add-a-<domain-object>, regen-client-types
│   └── ...
├── map/                ← deterministic flow / dependency maps (code-derived, not prose)
│   ├── index.md
│   └── <flow>.md         e.g. request-flow, generation-pipeline
└── reference/          ← concise per-area agent reference (always present; links to
    ├── index.md           technical/ for narrative when that track exists)
    └── <area>.md
```

Scale to the project (scope-to-depth rule from `../spec/plan-schema.md`):
- **Tiny repo:** collapse to a few flat files — `ai/index.md` + `ai/invariants.md` + one
  contract + one runbook. Do not pad.
- **Multi-repo:** `contracts/`, `runbooks/`, `map/`, `reference/` may take repo-scoped
  subfolders where scope warrants; cross-repo contracts/flows live at the track root.
- A folder with children gets an `index.md` that summarizes and links (it never duplicates
  child content).

### wiki/AI/index.md (the machine index)

The front door an agent (or `CLAUDE.md`, or a retriever) is pointed at. It is an
`llms.txt`-style **local index** (a curated map you point your own agent at — not an SEO /
crawler-discovery file, which is unsupported). It contains:

- An H1 (project name) and a one-line, self-contained summary.
- Link-lists grouped by area: `[invariants](invariants.md) — must-not-violate rules`,
  then contracts, runbooks, map, reference — each link with a one-line "what's here / when
  to read it" note.
- An `## Optional` group at the end holding links that can be dropped first under context
  pressure (glossary, deep reference).

Use **relative repo paths** (this is a local file tree, not a served site).

**`## Repositories` is orchestrator-owned — never author, edit, or delete it.** The
finalize step (`../init.md` Phase 3e step 2; refreshed by `../recheck.md` R5.2) writes a
repo manifest into this index — per repo: the anchor prefix, git remote URL, verified
commit SHA, dirty flag, and date, plus an anchor-resolution note. It is what lets a reader
outside this workspace resolve `<repo>/<path>:<line>` anchors to real repositories. When
regenerating `index.md`, preserve any existing `## Repositories` section **verbatim, in
place** (immediately before `## Optional`); if writing a fresh index where none exists,
leave it out — the orchestrator adds it at finalize.

---

## PAGE STRUCTURES (by type)

Every generated page's FIRST line is the generated-header, verbatim:

```
> _Generated by wiki-system from source — do not edit here. Run `/wiki-system recheck` to refresh; put durable hand-written notes in an `AUTOREGEN_SKIP` block._
```

Then the H1, then a **one-line self-contained context statement**, then a
`## Provenance` line (`Source: <paths> · Verified: <date>`). Then the type-specific body.
The header is line 1, always — no YAML frontmatter precedes it. Put all provenance facts
in the body (the context line + `## Provenance`), since frontmatter is stripped by chunkers.

**invariants.md** — a front-loaded, grouped list of atomic must-not-violate facts, each
anchored:
- One fact per bullet. Phrase as a rule ("X must always Y", "There is no Z").
- Each bullet carries a `(path:line)` anchor.
- Group by area (boot/runtime, auth, data, API contract, conventions). Most-load-bearing
  first.
- These are the facts an agent breaks if it doesn't know them. Keep it tight — this page is
  read in full, often.

**contracts/\<surface>.md** — reference for one agent-facing surface:
- `## Summary` — one self-contained line: what surface, who calls it, what shape.
- `## Source of truth` — link to the machine definition if one exists (swagger/OpenAPI,
  generated types, JSON schema). State that it is authoritative and may be regenerated.
- `## Shape` — exact types, enums, constraints, **complete** error/response shapes. Use
  verbatim identifiers. Do not invent fields.
- `## When to use / when not` — selection guidance + per-parameter rationale/constraints
  (this is where agents stumble: function selection and parameter filling).
- `## Gotchas` — non-obvious behaviour; phrase as "default path … ; the one escape hatch …".
- `## Source anchors` — `file:line` list backing every claim above.

**runbooks/\<task>.md** — how to make a common change safely:
- `## Goal` — one self-contained line.
- `## Steps` — ordered, numbered. Each step: the exact action and **verbatim command** if
  any, an explicit transition ("after step 2, …"), and a `(path:line)` anchor for the code
  the step touches. No vague steps.
- `## Verify` — the exact command(s) or check that prove success (a pass/fail the agent can
  self-run, e.g. "`yarn tsc` passes" / "`_generated.ts` changed"). Every runbook ends here.
- `## Gotchas` — the traps for this task.
- Commands must be verified against the real CLI surface (`package.json` scripts etc.) — no
  invented flags.

**map/\<flow>.md** — a deterministic, code-derived flow/dependency map:
- A Mermaid diagram of the actual path (e.g. route → controller → service → model), each
  hop anchored to source.
- Prefer code-derived relationships over prose paraphrase (paraphrase is the highest
  hallucination risk for structural claims).
- `## Source anchors` backing each hop.

**reference/\<area>.md** — concise, agent-oriented reference for one area:
- `## Purpose` (mandatory) — one self-contained line.
- The agent-relevant facts to act in this area: key files/symbols, the data shapes, the
  control flow, the gotchas — atomic and anchored. **Not** human narrative; if the
  technical track exists, link to it for the "why/story" and keep this to "what an agent
  needs to act."
- `## Source anchors`.

**glossary.md** — canonical terms: one entry per concept, the agreed name, a one-line
definition, and where it is defined in source.

---

## WRITING STANDARDS

- **Page titles (the first `# H1`) are short, bare names.** The H1 becomes the page's
  title in the wiki tree and the Notion mirror — make it the plain section/folder/page
  name (`# AI`, `# Contracts`, `# Runbooks`, `# Invariants`, `# ew-api`), never prefixed
  with the project name (`elf-watch — …`) or suffixed with structural meta (`— index`,
  `— task index`, `(ai/map)`, `per-repo …`). Put any descriptive context in the opening
  line, not the heading — verbose H1s render as noise in the sidebar.
- Declarative and atomic. State facts, not narrative. One fact per sentence where it
  carries an anchor.
- Present tense, exact identifiers, verbatim commands/paths/enums/error codes.
- Dense and pruned — every sentence carries information or is cut.
- Headings + short lists; avoid walls of text and wide tables in retrieved reference.
- 1–5 canonical examples, never exhaustive.
- No time-relative words; date facts in `## Provenance`.
- Code references are **allowed and encouraged** — but every one must resolve in source.

---

## VERIFICATION RULES (writer-side; the verifier re-checks these)

- **Paste-the-line test for every claim.** Before writing a behavioural or structural
  claim, locate the exact source lines and cite them. If you can't locate them, do not
  write the claim. Speculation in confident prose is the costliest error.
- **Counts enumerated, not estimated.** Count items in source; anchor the enumeration.
- **Commands checked.** Every command in a runbook resolves to a real script/CLI surface in
  `scope_files` (no invented flags or scripts).
- **Contracts checked against the SoT.** When you point at swagger/OpenAPI/generated types,
  confirm the fields/enums you mention actually appear there; never paraphrase a shape you
  didn't read.
- **Anchors must resolve and entail.** Every `(path:line)` must exist and the cited lines
  must actually support the claim — an anchor that doesn't entail its claim is worse than
  none (it manufactures false confidence).
- **Refuse to synthesize when source is silent.** No evidence → one honest line or omit;
  never elaborate fluently on absent evidence.
- **Flows traced step-by-step** through the real code path, function by function.

---

## QUALITY CRITERIA

Every page must meet five standards:

**SELF-CONTAINED** — survives being read in isolation; no unresolved back-references.

**GROUNDED** — every claim is atomic and anchored to source lines that entail it; counts
enumerated; commands real.

**ACTIONABLE** — runbooks are executable with a working Verify step; contracts give an agent
exactly what it needs to call the surface correctly (types, enums, errors, when-to-use).

**NON-DUPLICATIVE** — links to the technical track and to machine SoT instead of restating;
no near-duplicate of another page.

**CURRENT** — `## Provenance` records source paths + verified date; no time-relative
phrasing; deprecated content is labelled, not deleted silently.

---

## CONSTRAINTS

- Writers produce files **only under `wiki/AI`**. Never modify the wiki root
  (`wiki/index.md`) — it is out of scope.
- Preserve content between `<!-- AUTOREGEN_SKIP_BEGIN -->` and `<!-- AUTOREGEN_SKIP_END -->`
  markers verbatim.
- **Link, don't restate.** Point at the technical track (when present) and at machine
  sources of truth (OpenAPI/swagger, generated types, JSON schema, scripts) instead of
  copying them. Document project-specific surfaces only; never re-document framework/stdlib.
- Code references are allowed, but every symbol/path/type/command/anchor must resolve in
  source.
- Every page must be reachable from `ai/index.md` (directly or via a folder `index.md`).
- A writer dispatched on a verifier failure may decline to rewrite if it concludes the
  verifier was wrong, returning `skipped: true` with a `skip_reason` (same protocol as the
  other specialists). Do not abuse this exit.
- Every planned page must be written; every page links to at least one other page.
- When updating, rewrite the full page — never append (avoids drift/duplication).
- If something is unclear from the codebase, mark it unknown rather than guessing.
