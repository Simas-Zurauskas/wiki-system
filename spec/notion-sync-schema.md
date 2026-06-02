The canonical schema for `wiki/.internal/notion-sync.yaml` — the structured
artifact that maps the on-disk `wiki/library/` tree to its mirror in Notion.
It is produced and maintained by `../notion.md` (the `notion sync` command) and
by `../notion-recheck.md` (the `notion recheck` command), which also **rebuilds
it from Notion's own structure** when it is missing or stale.

This file is a reference, not a prompt. Agents read it when they need to
understand a field's meaning or the invariants the mapping must satisfy.

---

## WHY THIS ARTIFACT EXISTS

Notion page ids are assigned by Notion at creation time. Without a persisted
`wiki path → Notion page id` map, a second `notion sync` run cannot tell
"this page already exists, update it" from "this is new, create it" — so it
would duplicate the entire tree. This artifact is what makes the sync
**idempotent** and **resumable**, and it is the prerequisite for any future
diff-against-Notion ("notion recheck") work.

The mapping is the single source of truth for the local↔Notion correspondence.
`wiki/library/` on disk is authoritative for *content*; Notion is a render
target; this file is the *correspondence* between them.

---

## WHO READS / WRITES THIS

| Agent | When | Mode |
| --- | --- | --- |
| `../notion.md` (`notion sync`) | Every run: reads to decide create-vs-update; writes incrementally as pages are created/updated; **seeds `scope_files`/`owner_agent` per node from `plan.yaml`** so the map can later anchor a no-local audit | read + write |
| `../notion.md` preflight | First run: file absent → first-sync path. Present → re-sync path | read |
| `../notion-recheck.md` (`notion recheck`) | Audits live Notion content against the **source code** and fixes drift **in Notion only** (never reads or writes `wiki/library/` / `wiki/index.md`); resolves each page's `scope_files`/`owner_agent` from **this map** (the code anchor); **rebuilds the map from Notion's structure** when it is absent/stale; refreshes `notion_content_hash` | read + write |

If this file conflicts with any inline description elsewhere, this file wins.
Update this file first, then update references.

---

## SCHEMA

```yaml
meta:
  root_page_id: <uuid>          # the Notion page the whole tree lives under.
                                # Captured + validated on first run; reused thereafter.
  root_page_url: <url>          # human-readable; for the report and for re-validation
  schema_version: "1.3"         # bump on breaking changes to this schema
                                # 1.1: topics.md split out of the root body into its own
                                #      "Topics" leaf page (parent wiki/); root has no extra_sources.
                                # 1.2: folder index file renamed OVERVIEW.md -> index.md (root body =
                                #      wiki/index.md, Library body = wiki/library/index.md); the
                                #      technical track is always nested under wiki/library/technical/
                                #      (repos live at wiki/library/technical/<repo>/, never directly
                                #      under wiki/library/). Product track unchanged.
                                # 1.3: topics.md dropped entirely (no "Topics" page). The root page's
                                #      only children are Library + Notes. No topics leaf node.
  generator_version: "wiki-system v<N> · <model-id>"  # skill version + model of the last sync/recheck;
                                # notion recheck compares it to the current generator to decide whether
                                # a generator change (not just code change) warrants a fuller re-audit.
  synced_at: <ISO-8601>         # timestamp of the last fully-completed sync
  folder_icon: "📁"             # icon applied to every node with children.
                                # Configurable; leaf and childless pages never get an icon.
  set_root_title: false         # if true, set the root page title from wiki/index.md's H1;
                                # default false leaves the user's root page title untouched.
  notes_placeholder: |        # body text written ONCE to the Notes page, then never touched.
    This space is maintained by hand in Notion — it is not generated or
    overwritten by the wiki sync. Add plans, notes, and RFCs here directly.

# One entry per node in the published tree. A "node" is one of:
#   - root      (kind: root    — the user's Notion root page. Body = wiki/index.md.
#                                 Children: the reference and working nodes, in that
#                                 order. node key = wiki/ .)
#   - reference (kind: folder  — the "Library" container page. Body = wiki/library/index.md.
#                                 Holds the enabled track subtrees (ai/, technical/, product/). parent = wiki/ .)
#   - working   (kind: working — a human-owned placeholder page. Created ONCE with placeholder
#                                 text, then NEVER overwritten on re-sync. Does NOT mirror
#                                 wiki/notes/ disk content. parent = wiki/ .)
#   - folder    (kind: folder  — any directory under library/ that contains index.md;
#                                 body from that index.md)
#   - leaf      (kind: leaf    — a standalone .md file under library/ (e.g. architecture.md).)
# Node key = the directory path (root/folder/working, trailing slash) or the file path (leaf).
# Always relative to project root. The root keys on wiki/ ; everything reference and
# below keys under wiki/library/.
pages:
  - node: wiki/                                 # root node → the user's Notion root page
    kind: root
    body_source: wiki/index.md                # overview only
    notion_page_id: <uuid>                       # equals meta.root_page_id
    parent: null                                 # root has no parent
    title: null                                  # left untouched unless meta.set_root_title
    has_children: true                           # children: reference + working
    content_hash: <sha256>                       # hash of the rendered Notion markdown last pushed
    synced_at: <ISO-8601>

  - node: wiki/library/                        # the "Library" container page
    kind: folder
    body_source: wiki/library/index.md
    notion_page_id: <uuid>
    parent: wiki/
    title: "<H1 of body_source>"
    has_children: true
    content_hash: <sha256>
    synced_at: <ISO-8601>

  - node: wiki/notes/                          # the "Notes" human-owned placeholder
    kind: working
    body_source: null                            # synthetic; body is meta.notes_placeholder
    notion_page_id: <uuid>
    parent: wiki/
    title: "Notes"
    has_children: false                          # no AI children; humans may add their own
    content_hash: null                           # never hashed/diffed — create-once, never overwrite
    synced_at: <ISO-8601>

  - node: wiki/library/technical/              # the "Technical" track folder under Library
    kind: folder
    body_source: wiki/library/technical/index.md
    notion_page_id: <uuid>
    parent: wiki/library/
    title: "<H1 of body_source>"
    has_children: true
    content_hash: <sha256>
    synced_at: <ISO-8601>

  - node: wiki/library/technical/api/          # folder node (a repo, ALWAYS nested under technical/)
    kind: folder
    body_source: wiki/library/technical/api/index.md
    notion_page_id: <uuid>
    parent: wiki/library/technical/             # the containing track folder
    title: "<H1 of body_source>"
    has_children: true
    content_hash: <sha256>
    synced_at: <ISO-8601>

  - node: wiki/library/technical/api/architecture.md     # leaf node
    kind: leaf
    body_source: wiki/library/technical/api/architecture.md
    notion_page_id: <uuid>
    parent: wiki/library/technical/api/
    title: "<H1 of body_source>"
    has_children: false
    content_hash: <sha256>                        # of the rendered LOCAL markdown last pushed
    notion_content_hash: <sha256>                 # optional: of NOTION's own serialization after that
                                                  #   push. notion recheck compares the live page to
                                                  #   this to detect human edits. Absent until a
                                                  #   recheck establishes it.
    owner_agent: technical                        # optional: the page's writer/verifier mode
                                                  #   (ai | technical | product), copied from plan.yaml
                                                  #   at sync time. Lets `notion recheck` pick the
                                                  #   verifier mode + writer WITHOUT reading plan.yaml.
    scope_files: [api/src/index.ts, api/src/db/*] # optional: the source paths this page documents,
                                                  #   copied from plan.yaml at sync time. THE code anchor
                                                  #   `notion recheck` verifies the live page against —
                                                  #   it is what lets the audit run with no local wiki and
                                                  #   no plan.yaml. Absent → that page is un-auditable
                                                  #   (no code ground truth) until a sync/plan seeds it.
    synced_at: <ISO-8601>

# Nodes that were synced in a prior run but no longer exist on disk.
# Populated when the source file/folder is deleted or renamed. NEVER acted on
# automatically — the sync command surfaces these and asks the user whether to
# archive the corresponding Notion page. Until then they remain recorded so the
# Notion page is not orphaned silently.
orphans:
  - node: wiki/library/technical/api/old-page.md
    notion_page_id: <uuid>
    detected_at: <ISO-8601>
```

Field order is free. Every field is required unless noted.

---

## FIELD SEMANTICS

### `meta`

- **root_page_id** — the Notion page that holds the whole mirror. Its body is
  `wiki/index.md`; its direct children are the `Library` and `Notes` pages.
  Captured on first run from the user-supplied
  URL/id, validated via `notion-fetch`, and persisted. Never re-prompted once set.
- **folder_icon** — emoji set on every node with `has_children: true`. The
  icon rule is binary and structural: a node gets the icon iff it has
  children. Leaf and childless pages (including `Notes`) are never given an
  icon. The root page's icon is left untouched (it is the user's page).
- **set_root_title** — default false. The root is the user's page, so its title
  is left alone; set true only if the project wants the root titled from
  `wiki/index.md`'s H1.
- **notes_placeholder** — the body written to the `Notes` page the first
  time it is created. The page is human-owned thereafter: re-syncs never
  overwrite it (see `pages[].kind: working`).
- **synced_at** — only updated when a full run completes. A run that halts
  mid-way leaves the previous `meta.synced_at` but still persists per-node
  `notion_page_id`s as they are created (resumability).

### `pages[]`

- **node** — the structural key. root/folder/working nodes key on the directory
  path (trailing slash); leaf nodes key on the `.md` file path. Always relative
  to project root. The root keys on `wiki/`; reference and below key under
  `wiki/library/`; the working placeholder keys on `wiki/notes/`.
- **kind** — `root` | `folder` | `leaf` | `working`. Exactly one `root` node
  (keyed `wiki/`, `notion_page_id` == `meta.root_page_id`), exactly one
  `working` node, and the `Library` container is the `folder` node keyed
  `wiki/library/`. All `leaf` nodes live under `wiki/library/`.
- **body_source** — the markdown file whose content (minus its H1) becomes the
  Notion page body.
  - `root` → `wiki/index.md` (overview only).
  - `folder` → the `index.md` inside the directory, or `null` if it has none
    (its body becomes an auto-generated child list). The `Library` container is
    a folder node and commonly has no `wiki/library/index.md`.
  - `leaf` → the file itself.
  - `working` → `null`; its body is `meta.notes_placeholder`, not a disk file.
- **notion_page_id** — the live Notion page. Absent/null until the page is
  created. If a `notion-fetch` on this id later fails (page deleted/archived in
  Notion by a human), the sync treats the node as missing and recreates it,
  overwriting this field.
- **parent** — the `node` key of the containing folder/root. Used to create the
  page under the correct Notion parent (creation is strictly top-down).
- **has_children** — drives the icon rule and the child-preservation rule
  during updates (see `../notion.md` § N3). Recomputed every run; a leaf that
  gains a sibling `index.md`/subdir, or a folder that loses its children,
  flips and the icon is added/removed accordingly.
- **content_hash** — sha256 of the **rendered Notion markdown that was actually
  pushed** (after cross-link resolution and after appending child-page
  references), normalized for trailing whitespace. Re-sync recomputes the
  rendered output with the current id map and compares; equal → skip the write,
  differ → update. Hashing the *rendered* output (not the raw source) is
  deliberate: it catches both source edits AND changes caused by a link target
  gaining/changing its Notion id. **The `working` node is the exception:** its
  `content_hash` is `null` and it is never diffed — once created it is never
  pushed again, so human edits in Notion survive every re-sync.
- **notion_content_hash** — *optional; written/used by `notion recheck`.* The
  sha256 of **Notion's own serialization** of the page captured right after a
  push, normalized. It is the **audit-skip signal**: `notion recheck` re-verifies a
  page (live Notion content vs source code) only when the page's Notion content has
  changed (live serialization hash ≠ this baseline) OR its `scope_files` changed
  since `meta.synced_at`. If both are unchanged, the page can't have drifted and is
  skipped — the same economy as `recheck.md`'s `state: unchanged`. It is NOT a
  diff-against-local: `notion recheck`'s ground truth is the source code, never this
  hash. Absent until a recheck establishes it; `notion sync` need not maintain it.
- **owner_agent** / **scope_files** — *optional; written by `notion sync`, read by
  `notion recheck`.* Copied verbatim from the matching `plan.yaml` entry at sync time
  (joined by `node` == the plan page/section `path`): `owner_agent` from the page,
  `scope_files` from the page. They make the mapping a **self-sufficient code anchor**:
  `notion recheck` resolves a live Notion page → its `scope_files` (what code to verify
  against) and `owner_agent` (which verifier mode / writer) from the mapping ALONE — no
  `wiki/library/` file and no `plan.yaml` required. `scope_files` is the same glob/path
  list the local verifier uses; `owner_agent` is one of `ai` | `technical` | `product`.
  A leaf node with no `scope_files` (an overview/derived page, or one synced before this
  field existed) is **un-auditable** by `notion recheck` — there is no code to verify it
  against — and is reported as such rather than passed. When `plan.yaml` IS present at
  audit time, `notion recheck` prefers it (freshest) and falls back to these fields.
  `notion sync` omits both when no `plan.yaml` is available to copy from.

### Rebuilding the mapping from Notion (the mapping is a cache)

This file is a **cache/optimization**, not the sole source of truth for the
local↔Notion correspondence. Notion is self-describing: its page tree mirrors the
disk tree (root → `Library` → `ai`/`technical`/`product` → repos → …), so the mapping can
be reconstructed by walking Notion from the root page and matching each page to a
disk node by tree position + title. `notion recheck` does exactly this when the
file is missing or stale (e.g. a fresh checkout, a different machine, or a lost
file). The only piece of bridge state that is genuinely unrecoverable from disk is
`meta.root_page_id` — and even that is recoverable by re-supplying the root URL or
finding it with `notion-search`. Everything else (`notion_page_id`s, hashes,
titles, child lists) can be rebuilt from Notion + disk.

This is what lets "Notion live its own world": the local wiki and the Notion
mirror each stand alone, joined only by the root page id and a rebuildable cache.
`wiki/.internal/` content (plan, verification, traces) is **never published to
Notion** — it is local generation machinery, not documentation.

### The `working` node (human-owned)

`Notes` is created once, with `meta.notes_placeholder` as its body, and is
**never updated thereafter** — not its body, not its title. It is a hand-edited
space inside Notion, the Notion analogue of `wiki/notes/` (which the sync does
NOT mirror). The only thing the sync guarantees about it on later runs is that
it keeps existing as a child of the root (so the root's content update preserves
it). If a human deletes it in Notion, the next sync recreates it with the
placeholder.

### `orphans[]`

Recorded, never auto-resolved. Deleting Notion content is hard to reverse, and
a delete-then-create on disk is indistinguishable from a rename — so the sync
command lists orphans and asks the user (archive / leave / it's-a-rename)
rather than guessing.

---

## INVARIANTS

A valid `wiki/.internal/notion-sync.yaml` must satisfy all of:

1. Exactly one `pages[]` entry has `kind: root` (keyed `wiki/`), and its
   `notion_page_id` equals `meta.root_page_id`.
2. Exactly one `pages[]` entry has `kind: working` (keyed `wiki/notes/`,
   `parent: wiki/`), and exactly one `folder` node is keyed `wiki/library/`
   (the Library container, `parent: wiki/`). The only `pages[]` children of the
   root are these two (Library + Notes). Foreign pages a human adds under the root
   are NOT in `pages[]` — `notion sync` re-discovers and preserves them each run
   (see `../notion.md` N0 step 4); they are never persisted here.
3. Every non-root node's `parent` refers to an existing node key in `pages[]`.
4. Every `node` path starts with `wiki/`. root/folder/working keys end with
   `/`; leaf keys end with `.md` and live under `wiki/library/`.
5. No two nodes share the same `node` key or the same `notion_page_id`.
6. A node's `body_source` exists on disk at sync time, EXCEPT: the `working` node
   (always `body_source: null`), and any `folder` node whose directory has no
   `index.md` (`body_source: null` → auto child-list body). A node whose
   `body_source` *vanished* (it had one and the file was deleted) belongs in
   `orphans[]`, not `pages[]`.
7. `has_children: true` ⇒ the node is `root` or `folder`. `leaf` and `working`
   nodes always have `has_children: false`.
8. `meta.schema_version` matches the version this file documents (`1.3`).

The sync command validates 1–5 and 7 before writing, and reconciles 6 (moving
vanished nodes to `orphans[]`) during its reconcile phase. `notion recheck`,
unlike `notion sync`, does **not** halt on an absent or invalid file — it rebuilds
a conforming mapping from Notion's structure (see § Rebuilding the mapping).

---

## EVOLUTION

Bump `meta.schema_version` on breaking changes; non-breaking additions (new
optional fields, e.g. `notion_content_hash`) do not require a bump. Keep the
artifact minimal — it is a correspondence cache, not a content store. Anything
derivable at run time (titles, child lists, `notion_page_id`s) is recomputable
from disk + Notion's structure — see § Rebuilding the mapping from Notion — so a
lost or stale file is recoverable, not catastrophic. The only state not on disk
is `meta.root_page_id`, and that is re-suppliable.
