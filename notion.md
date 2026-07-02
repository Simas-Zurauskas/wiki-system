Your task is to publish the on-disk `wiki/PRODUCT` track to Notion, mirroring
its structure under a single, human-chosen Notion "Product Wiki" page — and to
keep that mirror in sync on subsequent runs without creating duplicates. Only
the PRODUCT track is published; `wiki/AI` and `wiki/TECHNICAL` never go to
Notion. The root page is always chosen by a human, never created automatically.

This prompt is the **Notion publish orchestrator**, invoked as
**`/wiki-system notion sync [<root-page-url>]`**. There is **one** publish verb; it
handles both cases, choosing the path by whether a mapping already exists:

- **First publish** (no `notion-sync.yaml` yet) → create the mirror under the
  supplied root page and write the mapping. Pass the root page as the argument the
  first time, or you'll be asked for it.
- **Subsequent update** (mapping present) → idempotent push: re-render and push only
  the pages whose content changed, updating the existing mirror in place (no
  duplicates).

`notion sync` publishes the **Notion mirror**, not the local wiki — it is **not** the
Mode 1 bootstrap (`init.md`, which generates the local wiki). It is a one-directional
push: the local `wiki/PRODUCT` tree on disk is the source of truth; Notion is a render
target. This prompt never pulls content back from Notion and never edits the source
wiki.

Accuracy is `init`/`recheck`'s job — fix the source with `recheck`, then `notion sync`.

**What the mirror looks like.** Under the user's Notion "Product Wiki" root page:

```
[Product Wiki root page]   body = wiki/PRODUCT/index.md
 ├── 📁 <feature folder>   body = wiki/PRODUCT/<feature>/index.md
 └── <feature leaf>        body = wiki/PRODUCT/<feature>.md
```

So the sync publishes **`wiki/PRODUCT/index.md`** (into the root page's body)
and the **`wiki/PRODUCT/` feature folders and leaves** directly beneath it.

It reuses shared conventions — TWO ROOTS from `init.md`, the CWD pre-flight from
`SKILL.md`, and the stub-first rationale from `init.md` — without redefining
them. The correspondence it maintains is specified by
`spec/notion-sync-schema.md`; read that before writing the mapping. Unlike
`init`/`recheck`, this command dispatches no sub-agents — the orchestrator makes
the MCP calls itself.

---

## TWO ROOTS

Same two roots as `init.md` § TWO ROOTS. **Skill files** (this `notion.md`,
`init.md`, `spec/notion-sync-schema.md`) are referenced by paths relative to
this prompt file. **Project files** (`wiki/PRODUCT/`, `wiki/.internal/notion-sync.yaml`,
the source repos) are relative to CWD (the **workspace**); `wiki/` means the resolved
`wiki-{project}/` docs folder (SKILL.md § Pre-flight resolves it). Never confuse them.

There is also a **third namespace** here that is neither: the **Notion
workspace**, addressed by page ids / URLs, reached only through the Notion MCP
tools. A "node" lives on disk; a "page" lives in Notion; the mapping file is the
bridge.

---

## HARD DEPENDENCY: THE NOTION MCP

This command drives Notion exclusively through the Notion MCP tools
(`notion-fetch`, `notion-create-pages`, `notion-update-page`,
`notion-move-pages`). If those tools are not available, this command cannot run.

**Preflight gate (do this first, before anything else):**

1. Confirm the Notion MCP tools are reachable. If they are not, **halt** and
   tell the user: "The Notion MCP is not connected. Connect it in Claude Code
   (it provides the `notion-*` tools), then re-run `/wiki-system notion sync`."
   Do not attempt a token/REST fallback — that is out of scope for this command.
2. Fetch the MCP resource `notion://docs/enhanced-markdown-spec` and keep it in
   working memory. **Do not guess Notion-flavored Markdown syntax.** Everything
   below that says "child-page reference", "callout", "mermaid", "table",
   "page link" must follow that spec exactly — especially the syntax for
   referencing an existing child page inside a parent's content (load-bearing
   for the child-preservation rule in N3).
   - **Server name gotcha:** the resource-server name is NOT the underscore form
     used in tool calls (`claude_ai_Notion`). It is the registered display name,
     which may contain spaces/dots — e.g. `claude.ai Notion`. If the fetch
     returns "Server … not found", the error lists the available servers; pick
     the one whose name contains "Notion" and retry. Don't burn attempts guessing.
   - From this spec, two facts are load-bearing for N3 — confirm them before
     rendering: a child sub-page is a `<page url="…">Title</page>` block
     (including it preserves the child; omitting it on a content replace DELETES
     it), whereas an inline cross-link is `<mention-page url="…">text</mention-page>`
     (safe — does NOT move the target). Never use `<page>` for a cross-link.

---

## CONFIGURATION

```
- root_body_source: wiki/PRODUCT/index.md  # the root page body (overview only)
- product_root: wiki/PRODUCT/      # the tree published under the "Product Wiki" root
- mapping_file: wiki/.internal/notion-sync.yaml
- child_order: plan | alpha           # default plan: order children by wiki/.internal/plan.yaml
                                       #   section/page order when that file exists; else alphabetical.
- archive_orphans: ask                # ask | never; default ask. NEVER auto-archive without asking.
- set_root_title: false               # default false: leave the user's root page title untouched
- provenance_banner: |                # STATIC callout prepended to every generated page (N3.1). Never interpolate
                                       #   a timestamp/version — that would re-hash and re-push every page each sync.
    🤖 Auto-generated from the codebase by **wiki-system**. Don't edit this page in
    Notion — changes are overwritten on the next sync. To change what it says, update
    the source repository and re-sync. For your own notes, plans, and RFCs, create your
    own native Notion pages outside this mirror.
```

`wiki/.internal/plan.yaml` is **optional** here. It is consulted only for child
ordering. The sync works on a hand-built `wiki/PRODUCT/` with no plan present.

**Scope.** This command publishes `wiki/PRODUCT/index.md` (root page body) and
the `wiki/PRODUCT/` tree. It never touches `wiki/.internal/`, `wiki/AI`, or
`wiki/TECHNICAL`.

---

## WHEN TO USE THIS PROMPT

| Situation | Use this | Use something else |
| --- | --- | --- |
| "Publish / mirror the wiki to Notion" | ✅ this prompt | |
| "I edited some product pages; push the changes to Notion" | ✅ this prompt (re-sync is idempotent) | |
| "The product content itself is stale/wrong" | | `recheck.md` (fix the source first, then sync) |
| "Generate the wiki from scratch" | | `init.md` |

This command publishes whatever is on disk (`wiki/PRODUCT/index.md` + the
`wiki/PRODUCT/` tree). It does not verify content accuracy — fix the source with
`init`/`recheck` first if needed.

---

## ROLE

You are a publish orchestrator. Your job, in order:

1. Preflight: MCP available, markdown spec loaded, CWD sane, root page resolved.
2. Build a model of the source tree from the filesystem.
3. Reconcile structure: ensure every node has a Notion page (create missing,
   top-down), persisting ids as you go.
4. Render and sync content: resolve cross-links (now that all ids exist) and
   push each changed page.
5. Reconcile orphans (report, ask before archiving).
6. Finalize: write the mapping, write a sync report, summarize.

You write to exactly two project locations: `wiki/.internal/notion-sync.yaml`
and `wiki/.internal/notion-sync-report.md`. You **never** modify `wiki/PRODUCT/`
or the source repos. Notion is mutated only through the MCP tools.

---

## PHASE N0: PREFLIGHT & ROOT RESOLUTION

Sequential, fast. (The MCP gate + markdown spec from § HARD DEPENDENCY are part
of this phase — do them first.)

1. **CWD sanity** — confirm `wiki/PRODUCT/` exists in CWD and contains at least
   one `.md`. If not, **halt gracefully**: there is no PRODUCT track to publish —
   this project has no product surface, or the wiki has not been generated (run
   `init.md`). Publish nothing.
2. **First-sync vs re-sync is decided by the mapping, not a verb.** There is one
   verb (`notion sync`); pick the path in step 3 by whether a **current** mapping
   exists:
   - **No mapping** → first-sync path (create the mirror under the supplied root).
   - **Pre-redesign mapping** → a `notion-sync.yaml` with `schema_version < 2.0`
     (or containing `Library`/`Notes` nodes) is a stale v1-shaped map. Treat it as
     **ABSENT** and rebuild from Notion's current tree (see the matching rule below);
     do not trust its node keys. This takes the first-sync path but re-uses the
     existing root page.
   - **Mapping present (schema_version ≥ 2.0)** → re-sync path (update in place).
   - **Mapping present AND the user passed a *different* root URL** → do **not**
     silently re-point. Tell the user the mirror is already initialized under
     `meta.root_page_id` and ask whether to keep it (ignore the new URL) or re-point
     to the new root (which abandons the old mirror and rebuilds it). Proceed only on
     an explicit choice.
   The rest of N1–N5 runs identically regardless of which path step 3 took.

   **Pre-redesign re-match rule (rebuild-from-Notion).** When treating a v1 map as
   absent, do not create a second PRODUCT tree — re-match against the pages already
   in Notion's current tree so ids are reused:
   - Old `Library/product` pages (and their descendants) **re-match to
     `wiki/PRODUCT/` nodes** by title/path; reuse their `notion_page_id`.
   - Old `Library/ai` and `Library/technical` pages have no counterpart under the
     new scope → they become **foreign/orphans**, surfaced in N4. Never delete them
     automatically.
   - The **root** stays the human-created "Product Wiki" page. The old `Library`
     container page itself, if it was an intermediate wrapper, becomes an orphan
     (surfaced in N4).

3. **Resolve the root page.** The root page is the **human-created "Product Wiki"
   root** — this command **never creates it**. The user supplies its id/URL once;
   the mirror takes the shape `root → PRODUCT feature folders/leaves` (the root page
   body is `wiki/PRODUCT/index.md`; PRODUCT features hang directly off it). Load
   `wiki/.internal/notion-sync.yaml` if it exists:
   - **Absent (or pre-redesign) → first-sync path.** The user must supply the root
     page. Accept it as a command argument (`/wiki-system notion sync <url-or-id>`)
     or ask: "Paste the Notion page URL (or id) of the Product Wiki page to publish
     the wiki under." Then `notion-fetch` it to validate access and capture its id.
     (On a pre-redesign rebuild the root id may already be in the stale
     `meta.root_page_id` — offer it as the default.)
   - **Present → re-sync path.** Read `meta.root_page_id` and `notion-fetch` it
     to confirm it is still reachable. If the fetch fails, halt and ask the user
     to re-supply the root page (the workspace/page may have changed).
4. **Enumerate the root's current children (BOTH paths, every run).** From the
   fetched root page, list its **direct** child pages and classify each:
   - **ours** — PRODUCT feature pages (matched by their mapping `notion_page_id`,
     else by title);
   - **foreign** — anything else a human added directly under the root.
   Record the foreign child ids **for this run only** so N3 preserves them in the
   root's child-ref render. Foreign children are **re-discovered every run** — never
   persisted in the mapping, never modified, and reported in N5. (This is why a
   human page added under the root after the first sync survives a later re-sync.)
   On **first-sync**, if the root page also has foreign **body content** (not just
   child pages), warn that this command will set the body from `wiki/PRODUCT/index.md`
   and recommend a dedicated page; proceed only on explicit confirmation.
5. **Validate the mapping** against `spec/notion-sync-schema.md` § INVARIANTS.
   On violation, halt and report which invariant failed — do not silently
   rebuild, because a bad map can cause duplicate creates.

---

## PHASE N1: BUILD THE SOURCE MODEL

Sequential, fast. No MCP calls. Build the node tree.

### N1.1 Enumerate nodes

The root is fixed; the PRODUCT subtree is discovered from disk.

- **root** node (`kind: root`, key `wiki/PRODUCT/`) → the user's Notion
  "Product Wiki" page. `body_source: wiki/PRODUCT/index.md`. Its children are the
  enabled PRODUCT feature folders and leaves discovered below. `has_children` =
  (children > 0).

Then discover the PRODUCT subtree under the root node:

- Every subdirectory of `wiki/PRODUCT/` (at any depth) that contains an
  `index.md` → a **folder** node (`body_source` = that `index.md`).
- Every `.md` file that is **not** an `index.md` and has no same-named sibling
  directory → a **leaf** node (`body_source` = the file itself).
- A folder node's children = its directory's non-`index` `.md` files (leaves)
  + its immediate subdirectories (folders). Recurse. `has_children` = (children > 0).

If `wiki/PRODUCT/index.md` is missing, the root body falls back to an
auto-generated child list — a **degraded root**. Do **not** synthesize an
overview here; generating `wiki/PRODUCT/index.md` is `init`/`recheck`'s finalize
job, not this publish command's. Flag it in the report **and** in the N5.3 summary
explicitly recommend running `/wiki-system init` or `/wiki-system recheck` to
generate a real `wiki/PRODUCT/index.md`, then re-syncing.

### N1.2 Extract title and body

For each node's `body_source`:
- **Title** = the text of the first `# ` H1 in the file. If there is no H1,
  derive a Title-Cased title from the file/folder name and flag it in the report.
- **Body** = the file content with that first H1 line removed (Notion stores the
  title separately; do not repeat it in the body). If a leading frontmatter
  block (`--- … ---`) is present, strip it too — reference pages shouldn't have
  one, but be defensive.

Special cases:
- **root node** — body = `body_source` (`wiki/PRODUCT/index.md`, H1 stripped) only.
  The root page title is left untouched unless `set_root_title: true`.

### N1.3 Order children

Order each node's children deterministically: by `wiki/.internal/plan.yaml`
section/page order when that file exists (`child_order: plan`), else
alphabetically (folders and files interleaved by name). Stable ordering keeps
re-syncs from reshuffling Notion pages.

### N1.4 Edge-case guards (record to the report; halt only where noted)

- **`*TODO*` stubs** — if a `body_source` still contains `*TODO*` stub markers
  (an interrupted `init`/`recheck` run), do **not** publish it as finished
  content. Skip the node's body (create/keep the page as an empty placeholder)
  and list it under "incomplete — not published" in the report.
- **Name collision** — a leaf `foo.md` AND a directory `foo/` in the same parent
  is ambiguous. Do not invent a merge; halt and ask the user to disambiguate.
- **Folder with no `index.md`** — treat as a folder node with a derived title
  and an auto-generated body (just its child list); flag it. (The standard wiki
  always has `index.md`; this only triggers on hand-built trees.)
- **Empty body** — allowed; the page is created with title + (folders) child
  list only.

---

## PHASE N2: RECONCILE STRUCTURE (PASS 1 — ids)

Establish a Notion page for every source node, **top-down** (a child can only be
created once its parent's id is known). This pass creates pages as
title + icon + minimal placeholder; full content is written in N3, after every
id is known (so cross-links resolve). This is the same stub-first technique
`init.md` uses, for the same reason.

### N2.1 Walk top-down

Process the root first, then each level. For each node:

- **Root node** → the human-created "Product Wiki" page already exists
  (`meta.root_page_id`). Do **not** create it; just ensure it is in the mapping
  with `notion_page_id = root id`. Its children to create this pass are the
  PRODUCT feature folders/leaves.
- **Node already in mapping with a live `notion_page_id`** → reuse it. Verify it
  is still reachable with `notion-fetch`; if the page was deleted/archived in
  Notion, treat the node as missing (recreate below) and overwrite the id.
- **Node missing (new, or id went stale)** → create it with
  `notion-create-pages`:
  - `parent`: `{ type: page_id, page_id: <parent node's notion_page_id> }`
  - `properties`: `{ title: "<node title>" }`
  - `icon`: `meta.folder_icon` **iff** `has_children` (leaves get no icon; the
    root page's icon is left untouched)
  - `content`: leave empty/minimal here — N3 sets the real body.
  Batch siblings under the same parent into one `notion-create-pages` call
  (max 100 per call, all sharing one parent). Capture each returned id.

**Persist the mapping after each create** (append the node with its new id).
A crash mid-pass must leave a resumable map — never lose a created page's id.

### N2.2 Detect orphans

Any node present in the prior mapping's `pages[]` but **absent from disk** in N1
is an orphan (file deleted or renamed). Move it to `orphans[]` with a
`detected_at` stamp. Do **not** archive anything yet — that is N4.

---

## PHASE N3: RENDER & SYNC CONTENT (PASS 2 — links)

Now every node has a `notion_page_id`, so cross-links resolve. For each node,
render its final Notion body, hash it, and push only if changed.

### N3.1 Render the body

Start from the node's extracted body (N1.2) and transform:

- **Provenance banner (prepend to every generated page)** — before the body, emit
  `provenance_banner` (§ CONFIGURATION) as a Notion **callout** block, per the
  loaded markdown spec. Apply to the **root**, every **folder**, and every
  **leaf** — every node this command renders. The banner is **static text**: never
  interpolate a timestamp, generator version, or any per-run value into it, or the
  body would re-hash and re-push on every sync. Because it is part of the hashed
  body (N3.2) it stays present and idempotent — and a human deleting it in Notion
  surfaces as drift and is restored on the next sync.
- **Cross-links** — rewrite relative markdown links that point at other wiki
  nodes into **`<mention-page url="…">text</mention-page>`** (inline, safe). ⚠️
  **Never use a `<page>` block for a cross-link** — `<page>` pointed at an
  existing page MOVES that page into the current one, destroying the tree.
  `<page>` is exclusively for the parent's own child list (next bullet).
  Resolution:
  - Normalize the link target relative to the current file's directory
    (handle `./`, `../`, and path normalization).
  - A link to another node's `body_source` or to a folder
    (`../checkout/`, `../checkout/index.md`) → that node's Notion page.
  - A link to `wiki/PRODUCT/index.md` (or a relative `../index.md`) → the
    **root page**.
  - Drop `#fragment` / `#Lnnn` anchors — Notion has no stable line/heading deep
    link here; link to the page and note dropped anchors in the report.
  - **Leave untouched**: external `http(s)://` links, links to source-code paths
    (e.g. `api/src/index.ts`), and images. A link that resolves to no known node
    is left as its original text and logged as a broken/unresolved link in the
    report — never fabricate a target.
- **Child-page references (CRITICAL for root and folder nodes)** — append, after
  the body, a **`<page url="…">Title</page>`** block for **every** current child
  page, in the N1.3 order. (This is the one place `<page>` is correct: these are
  the node's own children, so the block keeps them attached.) This is not just navigation: a
  `replace_content`/`update_content` that omits a child sub-page will **delete**
  that sub-page. Including every child preserves the hierarchy. The root's
  children are the PRODUCT feature folders/leaves (plus any foreign children
  discovered under the root in N0 step 4 — emit a `<page>` ref for each so the
  re-push does not delete them); a folder's are its leaves + subfolders. Leaf
  nodes have no children and skip this.
- **Other Notion-flavored constructs** (tables, code fences, `mermaid` code
  blocks, callouts) — keep as-is if already valid per the spec; otherwise adjust
  to the spec. Do not invent syntax.

### N3.2 Hash and push

- Normalize the rendered markdown (trim trailing whitespace) and compute its
  sha256 → `content_hash`.
- If the node is **new** (created this run) OR its `content_hash` differs from
  the mapping's stored hash → push:
  - **Body**: `notion-update-page` with `command: replace_content`,
    `new_str: <rendered body incl. child refs>`. Because the rendered content
    includes every child page reference, child sub-pages are preserved; keep
    `allow_deleting_content` off (false). If the tool still reports it would
    delete a child, that is a bug in N3.1's child enumeration — fix the content,
    do not force-delete.
  - **Title**: if the node's H1 changed since last sync, also
    `notion-update-page` with `command: update_properties` to update the title.
  - **Icon**: if `has_children` flipped since last sync, add (`meta.folder_icon`)
    or remove (`"none"`) the icon accordingly.
  - **Root node body**: render `wiki/PRODUCT/index.md` (per N1.2) followed by
    child refs for every PRODUCT feature folder/leaf (+ a `<page>` ref for every
    foreign child discovered in N0 step 4, so the re-push preserves them). Leave
    the root page's title alone unless `set_root_title: true`.
- If `content_hash` is unchanged → **skip** (no write). Record as "unchanged".

Update each node's `content_hash` and `synced_at` in the mapping as you push.

---

## PHASE N4: ORPHAN RECONCILIATION

If `orphans[]` is empty, skip. Otherwise present them to the user — never act
silently (archiving Notion pages is hard to reverse, and delete-then-add on disk
is indistinguishable from a rename):

```
These pages exist in Notion but their source is gone from wiki/PRODUCT/:
  - <node>  → <notion page url>
For each: archive the Notion page / leave it / it's a rename of <new node>?
```

- **archive** → `notion-update-page` to archive (or move out of the tree), then
  drop the entry from `orphans[]`.
- **leave** → keep the `orphans[]` entry; do nothing in Notion.
- **rename** → repoint the new node's mapping entry to the orphan's
  `notion_page_id` (so history/comments survive) and drop the orphan.

With `archive_orphans: never`, skip the prompt and just report orphans. Never
archive without explicit confirmation regardless of config.

---

## PHASE N5: FINALIZE

Sequential. No MCP calls except any already done.

### N5.1 Persist the mapping

Write `wiki/.internal/notion-sync.yaml` complete and valid against
`spec/notion-sync-schema.md`, with `meta.schema_version: "2.0"`. Set
`meta.synced_at` to now (only on a fully completed run). Re-check INVARIANTS 1–5
and 7 before writing.

### N5.2 Write the sync report

Write `wiki/.internal/notion-sync-report.md`:

```markdown
# Notion sync — <ISO timestamp>

Root page: <url>
Mode: first-sync | re-sync

## Summary
- Created: <n>   Updated: <n>   Unchanged: <n>   Skipped(incomplete): <n>
- Orphans: <n> (archived <n> / left <n> / renamed <n>)
- Foreign root children preserved: <n>

## Unresolved cross-links
| Page | Link text | Target (unresolved) |
| --- | --- | --- |
...

## Flags
- Nodes with no H1 (title derived): ...
- `*TODO*` stubs not published: ...
- Dropped link anchors (#fragment): ...
- Degraded root: `wiki/PRODUCT/index.md` missing → published a child-list fallback;
  run `/wiki-system init` or `recheck` to generate the overview, then re-sync. (Omit if present.)
```

### N5.3 Summarize to the user

Report counts, the root page URL, any unresolved links, and anything that needs
attention (incomplete pages, orphans left, name collisions, and — if `wiki/PRODUCT/index.md`
was missing — the degraded root, recommending `/wiki-system init` or `recheck` to
generate the overview then re-sync). Keep it tight.

---

## QUALITY GATES

Run before reporting complete:

- [ ] **No duplicates.** Every node maps to exactly one Notion page id; no
      id appears twice in the mapping.
- [ ] **Tree parity.** The root and every node on disk under `wiki/PRODUCT/`
      have a live Notion page; every Notion page in the mapping corresponds to a
      disk node or an explicit `orphans[]` entry. (Foreign root children are not in
      the mapping — they are preserved and reported, not parity-checked.)
- [ ] **Child preservation verified, not assumed.** `allow_deleting_content`
      stayed off and orphan archives went through N4 — and, after each root/folder
      `replace_content`, re-fetch and confirm no `<page>` child was dropped and no
      cross-link fell back to a plain `[text](…notion.so/…)` link (the symptom of
      a malformed mention URL). Repair via `update_content` before reporting done.
- [ ] **Links resolved or logged.** Every relative cross-link either rewrote to a
      Notion page or appears in the report's unresolved table. None silently lost.
- [ ] **Mapping valid.** `wiki/.internal/notion-sync.yaml` satisfies the schema
      invariants.
- [ ] **Source untouched.** No file under `wiki/PRODUCT/` or the repos was modified.

---

## CONSTRAINTS

- **One-directional.** Disk → Notion only. Never read content from Notion to
  overwrite the source; never edit any file under `wiki/`.
- **Scope.** Publishes `wiki/PRODUCT/index.md` (root body) and the
  `wiki/PRODUCT/` tree. Never touches `wiki/.internal/`, `wiki/AI`, or
  `wiki/TECHNICAL`.
- **The root page is human-owned; this command never creates it.** The human
  creates the "Product Wiki" root page and supplies its id; this command only
  populates it (body from `wiki/PRODUCT/index.md`) and gives it the PRODUCT feature
  children. The root page's title is left untouched (unless `set_root_title: true`).
- **Foreign root children are preserved, not persisted.** Pages a human adds
  directly under the root are re-discovered every run (N0 step 4), included in the
  root's child refs so they survive the body re-push, never modified, and reported.
  They are not stored in the mapping.
- **Idempotent.** A second run with no source changes performs zero Notion
  writes. Enforced by `content_hash`, not by hope — if re-syncs are rewriting
  unchanged pages, the hash logic is broken; investigate.
- **Top-down creation.** Children are never created before their parent's id is
  known. Mapping is persisted incrementally for resumability.
- **No silent destruction.** Orphan archiving always asks. Child sub-pages are
  preserved on every update by including them in rendered content.
- **MCP-only Notion access.** No REST/token fallback in this command.
- **Markdown spec is authoritative.** Notion-flavored syntax comes from
  `notion://docs/enhanced-markdown-spec`, never from guesswork.
- **Does not verify content.** Accuracy is `init`/`recheck`'s job. This command
  publishes what is on disk.

---

## GOTCHAS (Notion MCP rendering)

Learned the hard way; ignore them and a `replace_content` either silently drops a
child page or corrupts a cross-link.

- **`<page>` blocks with markdown-significant titles must come LAST.** A child
  reference whose title contains an em-dash (`—`) or other markdown-significant
  characters, when it is NOT the final `<page>` block, makes Notion's parser
  swallow the **following** `<page>` block — the next child is dropped and
  `replace_content` fails with *"would delete N child page(s)"*. Order siblings
  so any special-char-titled child reference is **last** among them. (Most acute
  for `<page>` lists with several children whose H1s carry em-dashes — e.g. a
  folder of pages titled `Foo — Bar`.)
- **The final `<page>` block needs a trailing newline.** End the rendered body
  with a newline after the last `<page>` block; an unterminated final block may
  not be recognized.
- **A space inside a mention URL silently downgrades it to a dead link.** A
  `<mention-page url="https://www.notion.so/36 ac2628-…">` (note the stray space)
  does NOT error — Notion renders it as a plain `[text](…)` markdown link with
  the space preserved, so the cross-link is dead. When hand-transcribing
  dashed ids, the most common slip is a space after the first `36`. Always
  re-fetch and scan for `.so/36 ` / `.so/33 ` (and any `](https://www.notion.so/`
  fallback) after a push, and repair with `update_content`
  (`[text](…)` → `<mention-page url="…">text</mention-page>`).
- **A resolved mention loses its inner text.** Notion stores a resolved
  `<mention-page>` as the self-closing dashless form `<mention-page url="…32hex…"/>`
  and renders the target's current title. This is expected; it does not mean the
  link is wrong.

## RELATIONSHIP TO OTHER PROMPTS

| File | Relationship |
| --- | --- |
| `init.md` | Authoritative for TWO ROOTS and the stub-first rationale. This prompt borrows those; it does not re-plan or scan repos. |
| `SKILL.md` | Mode router; its pre-flight (`pwd`/`ls`) is the CWD sanity check N0 reuses. |
| `recheck.md` | Fixes source-content drift. Run it (then `notion sync`) when the *content* is stale, not just its Notion mirror. |
| `spec/notion-sync-schema.md` | Authoritative for `wiki/.internal/notion-sync.yaml`. N0 validates against it; N5 writes conforming to it. |
| `spec/plan-schema.md` | Source of optional child ordering. Not required for sync. |
