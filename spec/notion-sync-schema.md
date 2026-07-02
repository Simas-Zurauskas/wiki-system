The canonical schema for `wiki/.internal/notion-sync.yaml` — the structured
artifact that maps the on-disk `wiki/PRODUCT` tree to its mirror in Notion.
It is produced and maintained by `../notion.md` (the `notion sync` command),
which also **rebuilds it from Notion's own structure** on its first run against
a pre-redesign Notion tree (a mapping with `schema_version < 2.0`, or one still
carrying the old Library/Notes nodes, is treated as absent and rebuilt).

This file is a reference, not a prompt. Agents read it when they need to
understand a field's meaning or the invariants the mapping must satisfy.

---

## WHY THIS ARTIFACT EXISTS

Notion page ids are assigned by Notion at creation time. Without a persisted
`wiki path → Notion page id` map, a second `notion sync` run cannot tell
"this page already exists, update it" from "this is new, create it" — so it
would duplicate the entire tree. This artifact is what makes the sync
**idempotent** and **resumable**.

The mapping is the single source of truth for the local↔Notion correspondence.
`wiki/PRODUCT` on disk is authoritative for *content*; Notion is a render
target; this file is the *correspondence* between them.

---

## WHO READS / WRITES THIS

| Agent | When | Mode |
| --- | --- | --- |
| `../notion.md` (`notion sync`) | Every run: reads to decide create-vs-update; writes incrementally as pages are created/updated | read + write |
| `../notion.md` preflight | First run: file absent → first-sync path. Present → re-sync path. A pre-2.0 map (or one carrying old Library/Notes nodes) is treated as absent and rebuilt from Notion's structure | read |

If this file conflicts with any inline description elsewhere, this file wins.
Update this file first, then update references.

---

## SCHEMA

```yaml
meta:
  root_page_id: <uuid>          # the human-chosen per-project "Product Wiki" Notion page the
                                # PRODUCT tree lives under. Captured + validated on first run;
                                # reused thereafter.
  root_page_url: <url>          # human-readable; for the report and for re-validation
  schema_version: "2.0"         # bump on breaking changes to this schema
                                # 1.1: topics.md split out of the root body into its own
                                #      "Topics" leaf page; root has no extra_sources.
                                # 1.2: folder index file renamed OVERVIEW.md -> index.md.
                                # 1.3: topics.md dropped entirely (no "Topics" page).
                                # 2.0: PRODUCT-rooted. The published tree is the wiki/PRODUCT
                                #      subtree ONLY. The "Library" container page and the
                                #      human-owned "Notes" working node are removed. Any map
                                #      written before 2.0 (schema_version < 2.0, or one still
                                #      carrying Library/Notes nodes) is treated as ABSENT and
                                #      rebuilt from Notion's own structure on the next sync.
  generator_version: "wiki-system v<N> · <model-id>"  # skill version + model of the last sync.
  synced_at: <ISO-8601>         # timestamp of the last fully-completed sync
  folder_icon: "📁"             # icon applied to every node with children.
                                # Configurable; leaf and childless pages never get an icon.
  set_root_title: false         # if true, set the root page title from the PRODUCT root's H1;
                                # default false leaves the user's root page title untouched.

# One entry per node in the published tree. A "node" is one of:
#   - root    (kind: root   — the user's Notion "Product Wiki" page. Body = wiki/PRODUCT/index.md.
#                             Its children are the PRODUCT subtree folders/leaves. node key = wiki/PRODUCT/ .)
#   - folder  (kind: folder — any directory under wiki/PRODUCT/ that contains index.md;
#                             body from that index.md)
#   - leaf    (kind: leaf   — a standalone .md file under wiki/PRODUCT/ (e.g. onboarding.md).)
# Node key = the directory path (root/folder, trailing slash) or the file path (leaf).
# Always relative to project root. The root keys on wiki/PRODUCT/ ; every node keys under it.
pages:
  - node: wiki/PRODUCT/                          # root node → the user's "Product Wiki" Notion page
    kind: root
    body_source: wiki/PRODUCT/index.md           # overview only
    notion_page_id: <uuid>                       # equals meta.root_page_id
    parent: null                                 # root has no parent
    title: null                                  # left untouched unless meta.set_root_title
    has_children: true
    content_hash: <sha256>                       # hash of the rendered Notion markdown last pushed
    synced_at: <ISO-8601>

  - node: wiki/PRODUCT/onboarding/               # folder node (a product area under the root)
    kind: folder
    body_source: wiki/PRODUCT/onboarding/index.md
    notion_page_id: <uuid>
    parent: wiki/PRODUCT/
    title: "<H1 of body_source>"
    has_children: true
    content_hash: <sha256>
    synced_at: <ISO-8601>

  - node: wiki/PRODUCT/onboarding/signup.md      # leaf node
    kind: leaf
    body_source: wiki/PRODUCT/onboarding/signup.md
    notion_page_id: <uuid>
    parent: wiki/PRODUCT/onboarding/
    title: "<H1 of body_source>"
    has_children: false
    content_hash: <sha256>                        # of the rendered LOCAL markdown last pushed
    synced_at: <ISO-8601>

# Nodes that were synced in a prior run but no longer exist on disk.
# Populated when the source file/folder is deleted or renamed. NEVER acted on
# automatically — the sync command surfaces these and asks the user whether to
# archive the corresponding Notion page. Until then they remain recorded so the
# Notion page is not orphaned silently.
orphans:
  - node: wiki/PRODUCT/onboarding/old-page.md
    notion_page_id: <uuid>
    detected_at: <ISO-8601>
```

Field order is free. Every field is required unless noted.

---

## FIELD SEMANTICS

### `meta`

- **root_page_id** — the human-chosen per-project "Product Wiki" Notion page
  that holds the mirror. Its body is `wiki/PRODUCT/index.md`; its direct
  children are the PRODUCT subtree's top-level folders/leaves. Captured on
  first run from the user-supplied URL/id, validated via `notion-fetch`, and
  persisted. Never re-prompted once set.
- **folder_icon** — emoji set on every node with `has_children: true`. The
  icon rule is binary and structural: a node gets the icon iff it has
  children. Leaf and childless pages are never given an icon. The root page's
  icon is left untouched (it is the user's page).
- **set_root_title** — default false. The root is the user's page, so its title
  is left alone; set true only if the project wants the root titled from the
  PRODUCT root's H1.
- **synced_at** — only updated when a full run completes. A run that halts
  mid-way leaves the previous `meta.synced_at` but still persists per-node
  `notion_page_id`s as they are created (resumability).

### `pages[]`

- **node** — the structural key. root/folder nodes key on the directory
  path (trailing slash); leaf nodes key on the `.md` file path. Always relative
  to project root. The root keys on `wiki/PRODUCT/`; every node keys under it.
- **kind** — `root` | `folder` | `leaf`. Exactly one `root` node
  (keyed `wiki/PRODUCT/`, `notion_page_id` == `meta.root_page_id`). All
  `folder` and `leaf` nodes live under `wiki/PRODUCT/`.
- **body_source** — the markdown file whose content (minus its H1) becomes the
  Notion page body.
  - `root` → `wiki/PRODUCT/index.md` (overview only).
  - `folder` → the `index.md` inside the directory, or `null` if it has none
    (its body becomes an auto-generated child list).
  - `leaf` → the file itself.
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
  gaining/changing its Notion id.

### Rebuilding the mapping from Notion (the mapping is a cache)

This file is a **cache/optimization**, not the sole source of truth for the
local↔Notion correspondence. Notion is self-describing: its page tree mirrors the
disk `wiki/PRODUCT/` tree (root → product areas → leaves), so the mapping can be
reconstructed by walking Notion from the root page and matching each page to a
disk node by tree position + title. `notion sync` does exactly this on its first
run against a pre-redesign Notion tree — a mapping with `schema_version < 2.0`
(or one still carrying the old Library/Notes nodes) is treated as absent and
rebuilt this way, so the PRODUCT tree is re-matched in place rather than
duplicated. The only piece of bridge state that is genuinely unrecoverable from
disk is `meta.root_page_id` — and even that is recoverable by re-supplying the
root URL or finding it with `notion-search`. Everything else (`notion_page_id`s,
hashes, titles, child lists) can be rebuilt from Notion + disk.

This is what lets "Notion live its own world": the local wiki and the Notion
mirror each stand alone, joined only by the root page id and a rebuildable cache.
`wiki/.internal/` content (plan, verification, traces) is **never published to
Notion** — it is local generation machinery, not documentation.

### `orphans[]`

Recorded, never auto-resolved. Deleting Notion content is hard to reverse, and
a delete-then-create on disk is indistinguishable from a rename — so the sync
command lists orphans and asks the user (archive / leave / it's-a-rename)
rather than guessing.

---

## INVARIANTS

A valid `wiki/.internal/notion-sync.yaml` must satisfy all of:

1. Exactly one `pages[]` entry has `kind: root` (keyed `wiki/PRODUCT/`), and its
   `notion_page_id` equals `meta.root_page_id`.
2. Foreign pages a human adds under the root are NOT in `pages[]` — `notion sync`
   re-discovers and preserves them each run (see `../notion.md` N0 step 4); they
   are never persisted here.
3. Every non-root node's `parent` refers to an existing node key in `pages[]`.
4. Every `node` path starts with `wiki/PRODUCT/`. root/folder keys end with
   `/`; leaf keys end with `.md`.
5. No two nodes share the same `node` key or the same `notion_page_id`.
6. A node's `body_source` exists on disk at sync time, EXCEPT any `folder` node
   whose directory has no `index.md` (`body_source: null` → auto child-list
   body). A node whose `body_source` *vanished* (it had one and the file was
   deleted) belongs in `orphans[]`, not `pages[]`.
7. `has_children: true` ⇒ the node is `root` or `folder`. `leaf` nodes always
   have `has_children: false`.
8. `meta.schema_version` matches the version this file documents (`2.0`).

The sync command validates 1–5 and 7 before writing, and reconciles 6 (moving
vanished nodes to `orphans[]`) during its reconcile phase. On its first run
against a pre-redesign Notion tree (a map with `schema_version < 2.0` or carrying
old Library/Notes nodes), `notion sync` treats the map as absent and rebuilds a
conforming 2.0 mapping from Notion's structure (see § Rebuilding the mapping).

---

## EVOLUTION

Bump `meta.schema_version` on breaking changes; non-breaking additions (new
optional fields) do not require a bump. The current `2.0` publishes the
`wiki/PRODUCT` subtree only — the tree is rooted at the user's "Product Wiki"
page. Keep the artifact minimal — it is a correspondence cache, not a content
store. Anything derivable at run time (titles, child lists, `notion_page_id`s)
is recomputable from disk + Notion's structure — see § Rebuilding the mapping
from Notion — so a lost or stale file is recoverable, not catastrophic. The
only state not on disk is `meta.root_page_id`, and that is re-suppliable.
