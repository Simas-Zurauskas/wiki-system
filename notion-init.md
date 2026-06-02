Your task is to **bootstrap the documentation directly in Notion from the source
code — without building a local wiki.** This does the same *work* as `init.md`
(scan → plan → generate → verify) but its output target is **Notion**, not
`wiki/library/`. The ground truth is the source code. It writes only
`wiki/.internal/` state (the plan + the Notion mapping) and the live Notion
workspace; it **never writes `wiki/library/` or `wiki/index.md`.**

This prompt is the **Notion-native bootstrap orchestrator** (`/wiki-system notion init`).
It is the create-counterpart of `notion-recheck.md` (which *maintains* Notion vs
code): this one *creates* the published docs from scratch, straight into Notion. It
is **not** "build the local wiki, then `notion sync`" — there is no local wiki here.

It composes existing contracts and does not redefine them:
- `init.md` — **Phase 1 (SCAN)** and **Phase 2 (PLAN)** are reused verbatim to produce
  `wiki/.internal/plan.yaml`; plus its `§ SCALING RULES` and `§ SUB-AGENT DELEGATION
  PRINCIPLES` (the writer/verifier brief templates) and `§ CONFIGURATION` (tracks,
  product description). **Phase 3 (stub → write local → finalize local) is NOT used** —
  it is replaced by the Notion-native build below.
- `specialists/ai.md` / `technical.md` / `product.md` — generate each page from code,
  run **in-memory** (return markdown, no Write tool — see § THE IN-MEMORY WRITER).
- `specialists/verifier.md` — the per-page accuracy check (generated content vs `scope_files`).
- `notion.md` — top-down create (N2), render + push (N3.1), child-preservation, the
  mapping, orphans (N4).

---

## TWO ROOTS (+ the Notion namespace)

Same as `notion.md`. **Skill files** (this `notion-init.md`, `init.md`, `notion.md`,
`specialists/`, `spec/`) are referenced relative to this prompt. **Project files**
(`wiki/.internal/plan.yaml`, `wiki/.internal/notion-sync.yaml`, the source repos) are
relative to CWD — **but never `wiki/library/` or `wiki/index.md`, which this command
does not create.** The **Notion workspace** is reached only through the `notion-*`
MCP tools.

---

## HARD DEPENDENCY: THE NOTION MCP

Same preflight gate as `notion.md` § HARD DEPENDENCY — run it first: confirm the
`notion-*` tools are reachable (halt with the same message if not) and fetch
`notion://docs/enhanced-markdown-spec` (same server-name gotcha; same `<page>`
vs `<mention-page>` facts).

---

## WHAT THIS IS, AND WHEN TO USE IT

| Situation | Use this | Use something else |
| --- | --- | --- |
| "Create the docs in Notion from the code — I don't want a local wiki" | ✅ this prompt | |
| "Bootstrap the documentation, and Notion is our doc home" | ✅ this prompt | |
| "I already have a built local `wiki/`; publish it to Notion" | | `notion sync` (`notion.md`) |
| "Bootstrap the docs **locally** (a `wiki/` folder on disk)" | | `init.md` |
| "The Notion docs already exist; check them against the code" | | `notion recheck` (`notion-recheck.md`) |

**The `notion *` family, and where the local wiki fits:**
- **`notion init`** (this) — **create** docs directly in Notion from code. No local wiki.
- **`notion recheck`** (`notion-recheck.md`) — **maintain** Notion vs code. No local wiki.
- **`notion sync`** (`notion.md`) — **publish** an existing local `wiki/` → Notion. This
  is the one Notion command that needs a local wiki; it is the bridge for projects that
  build locally first.

---

## KEY PRINCIPLES (read before building)

- **Source code is the source of truth.** Every page is generated from its
  `scope_files` and verified against them before it is published — the same accuracy
  guarantee as `init.md`, just published to Notion instead of disk.
- **Build into Notion, not onto disk.** Page content is generated in-memory and pushed
  to Notion. **No `wiki/library/` file and no `wiki/index.md` is ever written.** The
  only on-disk outputs are under `wiki/.internal/` (the plan + the mapping + run state).
- **`wiki/.internal/plan.yaml` is written and required.** Planning (which pages exist,
  their `scope_files`, `owner_agent`, links, structure) is the coordination spec that
  writers and verifiers consume — and the **code anchor** a later `notion recheck` reuses.
  It lives under `wiki/.internal/`, which is machinery, not the local wiki.
- **Verify before publish.** A page is pushed to Notion only after it passes
  verification. A `fail_hard` page is left as an empty/stub Notion page and queued for
  the user gate — never published as if finished.
- **Derived overviews are synthesized in-memory and pushed.** The root page body and
  the `Library`/folder overviews (the `init.md` finalize artifacts) are synthesized from
  the plan + the generated pages and pushed to their Notion pages — **not written to
  `wiki/index.md` / `wiki/library/index.md`.** (This is where `notion init` can do what
  `notion recheck` cannot: it has the full plan and freshly generated content, so it can
  build the derived pages without a local file.)
- **Idempotent and resumable.** The mapping is written incrementally as pages are
  created, so an interrupted run resumes without duplicating the tree (same property as
  `notion sync`).
- **`Notes` is human-owned.** Created once as a placeholder; never overwritten.
- **The root page is human-created.** This command never creates the root; the user
  supplies it (same as `notion.md` N0).

---

## THE IN-MEMORY WRITER

Writers (`specialists/{ai,technical,product}.md`) are hard-constrained to write their
output only under `wiki/library/<track>/`. This command must never write there. So it
dispatches each writer in **return-markdown mode**: the brief instructs the writer to
**generate the full page from its `scope_files` and return the markdown as its final
message — do NOT use the Write tool, do NOT write any file.** The orchestrator captures
the returned markdown, verifies it, and pushes it to Notion. Because the writer writes
no file, its `wiki/library/` output constraint is never exercised. The writer's
generation logic — read every `scope_file`, write the whole page — is used unchanged.

---

## ROLE

You are a build-into-Notion orchestrator. Your job, in order:

1. Preflight; resolve the human-created root page; confirm the track set.
2. Scan + plan (reuse `init.md` Phase 1 + Phase 2) → write `wiki/.internal/plan.yaml`.
3. Create the Notion page tree top-down (structure first), recording ids into the mapping.
4. Generate each page from code (in-memory), verify it, and push the passing ones to Notion.
5. Synthesize the derived overviews (root body, `Library`/folder indexes) and push them.
6. Finalize: write the mapping (with the `scope_files`/`owner_agent` code anchor) + the report.

You write `wiki/.internal/plan.yaml`, `wiki/.internal/notion-sync.yaml`, the per-page
verifier reports under `wiki/.internal/verification/`, scratch generation drafts under
`wiki/.internal/notion-init/`, `wiki/.internal/verification/_failures.md`, and the
`wiki/.internal/notion-init-report.md`. You **never** write `wiki/library/`,
`wiki/index.md`, or `wiki/notes/`, and you never publish `wiki/.internal/`.

---

## PHASE NI0: PREFLIGHT, ROOT & CONFIG

Sequential. (MCP gate + markdown spec first, per § HARD DEPENDENCY.)

1. **No local-wiki output.** Do not create `wiki/library/` or `wiki/index.md`. (A
   `wiki/.internal/` directory will be created for the plan + mapping; that is fine.)
2. **Resolve the root page** — the human-created "Wiki" root. This command **never
   creates it.** Accept its id/URL as an argument (`/wiki-system notion init <url-or-id>`)
   or ask. `notion-fetch` it to validate access and capture its id. Enumerate its direct
   children and classify ours vs foreign (`notion.md` N0 step 4); foreign children are
   re-discovered every run, preserved, never persisted.
3. **First-build vs resume** — by the mapping: if `wiki/.internal/notion-sync.yaml`
   already exists with this root, this is a **resume** (continue creating/updating only
   missing or changed pages — do not duplicate). If a *full, healthy* mapping already
   exists, the docs are already built: tell the user to use `notion recheck` (audit) or
   `notion sync` (push local edits) instead, and proceed only on explicit confirmation.
4. **Confirm the track set** — per `init.md § CONFIGURATION` → Documentation Tracks
   (`ai` + `product` default; `technical` opt-in). Record in `meta.tracks`.

---

## PHASE NI1: SCAN + PLAN (reuse init.md)

Run **`init.md` Phase 1 (SCAN)** and **Phase 2 (PLAN)** exactly as written — per-repo
scan sub-agents, cross-repo synthesis, then write `wiki/.internal/plan.yaml` per
`spec/plan-schema.md` (honoring the confirmed `meta.tracks`), including the coverage
gate. These phases write only `wiki/.internal/` artifacts (the per-repo surface tables
and `plan.yaml`) — no `wiki/library/` files.

**Then STOP — do not run `init.md` Phase 3.** Its Phase 3a stubs and 3b–3e write local
`wiki/library/*.md` and `wiki/index.md`; those are replaced by NI2–NI4 below, which
build the same structure and content **in Notion**. Use `init.md`'s `§ SCALING RULES`
for pool sizing and `§ SUB-AGENT DELEGATION PRINCIPLES` for the writer/verifier briefs
throughout.

---

## PHASE NI2: CREATE THE NOTION TREE (structure first)

Build the page tree top-down so cross-links resolve and ids exist before content
(`notion.md` N2). Derive the tree from the plan (not from disk — there is no disk tree):
- **root** → the user's root page (exists). Children: `Library` + `Notes`, in that order.
- **`Library`** page (child of root) → holds the enabled track folders.
- For every plan **section** (a folder with `has_overview`) → create a folder page under
  its parent; for every plan **page** (leaf) → create a childless page under its section.
- **`Notes`** → the human-owned placeholder, created once (`notion.md` working-node rules).

Create top-down, ordering children by the plan (`child_order: plan`). Record each
created `notion_page_id` into `wiki/.internal/notion-sync.yaml` **as it is created**
(resumability — a re-run skips existing ids). Pages are created empty here (or as
short placeholders); their bodies are filled in NI3/NI4. Apply the folder icon to nodes
with children only (`notion.md` icon rule).

---

## PHASE NI3: GENERATE + VERIFY + PUSH (per page, the core)

Parallel within the `§ SCALING RULES` pool. For each plan **page** (leaf), in plan order:

1. **Generate (in-memory).** Dispatch the page's writer (`specialists/{ai,technical,product}.md`,
   per `owner_agent`) in **return-markdown mode** (§ THE IN-MEMORY WRITER), using the
   writer brief from `init.md § SUB-AGENT DELEGATION PRINCIPLES`: read the page's
   `scope_files`, write the full page, **return the markdown — write no file.** Save the
   returned markdown to a scratch draft at `wiki/.internal/notion-init/<page-id>.draft.md`.
2. **Verify.** Dispatch a verifier (`specialists/verifier.md`, mode from `owner_agent`)
   with `page_path` = that scratch draft and `scope_files` from the plan — the same
   brief-override note as `notion-recheck.md` NR2.2 (the draft is under `wiki/.internal/`,
   not `wiki/library/`). Write the report to `wiki/.internal/verification/<page-id>.notion.yaml`.
   Auto-fix `fail_soft` once (re-dispatch the writer with the verifier's `issues`, then
   re-verify) — identical to `init.md` Phase 3d.
3. **Push (on pass).** Render the passing markdown via `notion.md` N3.1 (resolve relative
   cross-links to Notion page mentions using the ids from NI2; append child `<page>` refs
   from the tree) and `replace_content` into the page created in NI2, `allow_deleting_content`
   **off** (child-preservation). Capture `content_hash` + `notion_content_hash` and the
   `scope_files`/`owner_agent` **code anchor** into the mapping (`spec/notion-sync-schema.md`).
4. **fail_hard.** Do not publish. Leave the NI2 page empty/stub, record the page in
   `wiki/.internal/verification/_failures.md`, and queue it for the user gate. Never push
   content the verifier rejects.

After all pages: if any `fail_hard` pages remain, run the **batched user-resolution gate**
(identical to `init.md` Phase 3d.5: regen-with-context / patch-scope / scope-shrink-stub /
accept-with-banner / delete-page / defer). Nothing destructive happens silently.

---

## PHASE NI4: DERIVED OVERVIEWS (synthesized in-memory)

The root body and the `Library` / section-folder overviews are not code-verified pages —
they are synthesized navigation, the `init.md` Phase 3e finalize artifacts. Synthesize
each **in-memory** from the plan + the generated pages (NOT written to disk), and push:
- **Root page body** = the project overview (the `wiki/index.md` equivalent) → push to the
  root page body (leave the root *title* untouched unless `meta.set_root_title`).
- **`Library` overview** (the `wiki/library/index.md` equivalent) and any **folder/section
  overview** with `has_overview: true` → synthesize and push to that folder page's body.
- Run the same finalize checks `init.md` Phase 3e does on the synthesized text (links
  resolve to Notion mentions; numeric-consistency across pages) before pushing.

None of these are written to `wiki/index.md` or `wiki/library/`. (A later `recheck` +
`notion sync` is the path if the project ever wants a local copy of these.)

---

## PHASE NI5: FINALIZE

1. **Persist the mapping** — `wiki/.internal/notion-sync.yaml`, valid against
   `spec/notion-sync-schema.md`, with every node's `notion_page_id`, `content_hash`,
   `notion_content_hash`, and the seeded `scope_files`/`owner_agent` **code anchor**
   (so a later `notion recheck` audits with no local wiki). Set `meta.root_page_id`,
   `meta.tracks`, `meta.generator_version` (`wiki-system v<VERSION> · <model-id>`), and
   `meta.synced_at` (only on a fully completed run). Re-check INVARIANTS 1–5 and 7.
2. **Write the report** — `wiki/.internal/notion-init-report.md`:

```markdown
# Notion init (built into Notion from code) — <ISO timestamp>

Root page: <url>
Tracks: <enabled tracks>

## Build
- Pages planned: <n>   Created: <n>   Published (verified): <n>
- fail_hard (left as stubs, queued): <n>
- Derived overviews synthesized + pushed: <n>

## fail_hard pages needing attention
| Page | Verdict | Top issue |
| --- | --- | --- |
...

## Flags
- No local wiki was written (this command builds into Notion only). To get a local
  copy, run `/wiki-system init` (or `recheck` + `notion sync`).
- Foreign root children preserved: <n>
```

3. **Summarize** — counts, the root URL, what was published, what's still `fail_hard`,
   and that **no local `wiki/` was written**. Tight.

---

## EDGE CASES

- **A full healthy mapping already exists** — the docs are already built; route the user
  to `notion recheck` (audit) or `notion sync` (push local edits). Proceed only on
  explicit confirmation (treat as a resume/rebuild).
- **Interrupted run** — the mapping persisted each created id; a re-run resumes, creating
  only missing pages and generating only unfilled/unverified ones. No duplicate tree.
- **`scope_files` span repos not checked out** — same partial-scope guard as
  `notion-recheck.md`: if a material fraction (>25%, or any file the page's top claims
  depend on) is unreadable, don't publish from a half-blind generation — leave the page a
  stub and flag the missing repos. At the project root with all repos present, every page
  is fully buildable.
- **Coverage gate fails (init Phase 2)** — halt exactly as `init.md` does; a bad plan must
  not be built into Notion.
- **Root has foreign body content** — warn before setting the root body (per `notion.md`
  N0 step 4); proceed only on confirmation.
- **fail_hard at the gate → delete-page** — if the user chooses delete, the NI2-created
  empty page is archived (orphan path, `notion.md` N4), with confirmation.
- **`Notes`** — created once with the placeholder; never overwritten.
- **Serialization noise** — never byte-compare; verification is claims-vs-code, the
  skip/idempotency signal is the hashes.

---

## QUALITY GATES

- [ ] **No local wiki written.** No file under `wiki/library/` and not `wiki/index.md`
      was created or written this run. (The hard invariant of this command.)
- [ ] **Built from code, verified before publish.** Every published page was generated
      from its `scope_files` and passed verification before its push. No page was
      published in `fail_hard`; such pages are empty stubs recorded in `_failures.md`.
- [ ] **Mapping authoritative + anchored.** Every created page maps to one node with its
      `notion_page_id`; the `scope_files`/`owner_agent` code anchor is seeded so
      `notion recheck` can audit with no local wiki.
- [ ] **Derived overviews pushed, not written.** Root/Library/folder overviews were
      synthesized in-memory and pushed; none was written to disk.
- [ ] **Child preservation.** No parent push dropped a child sub-page (children enumerated
      from the tree + mapping).
- [ ] **`Notes` untouched; foreign untouched.** Created once / left as-is; never overwritten.
- [ ] **State only under `wiki/.internal/`** (plan, mapping, verification, drafts, report);
      never published to Notion.

---

## CONSTRAINTS

- **Source code is the source of truth.** Pages are generated from `scope_files` and
  verified against them before publish.
- **No local wiki.** It writes `wiki/.internal/plan.yaml` + the mapping but never
  `wiki/library/` or `wiki/index.md`. The build target is Notion.
- **In-memory writers.** Generation runs writers in return-markdown mode; no writer writes
  a file this run.
- **The root page is human-created** and never created by this command.
- **`Notes` and foreign pages are sacrosanct.** Never overwritten; orphans archived only
  with explicit confirmation.
- **MCP-only Notion access**; **markdown spec is authoritative** for Notion syntax.

---

## RELATIONSHIP TO OTHER PROMPTS

| File | Relationship |
| --- | --- |
| `init.md` | Phase 1 (SCAN) + Phase 2 (PLAN) reused verbatim to produce `plan.yaml`; plus `§ SCALING RULES`, `§ SUB-AGENT DELEGATION PRINCIPLES`, `§ CONFIGURATION`. Its Phase 3 (local stub/write/finalize) is replaced by NI2–NI4. |
| `specialists/{ai,technical,product}.md` | Generate each page from code, in **return-markdown mode** (§ THE IN-MEMORY WRITER). Invoked unchanged; no file written. |
| `specialists/verifier.md` | The per-page audit, run over the in-memory draft + `scope_files`, with the brief override pointing `page_path` at the `wiki/.internal/` scratch draft. Invoked unchanged. |
| `notion.md` | Top-down create (N2), render + push (N3.1), child-preservation, icons, orphans (N4), the mapping, the human-created-root rule. Reused, not redefined. |
| `notion-recheck.md` | The maintain-counterpart — audits Notion vs code after this command has built it. Same no-local, code-grounded, in-memory model. |
| `spec/plan-schema.md` / `spec/notion-sync-schema.md` | The plan, and the mapping incl. the `scope_files`/`owner_agent` code anchor this command seeds. |
