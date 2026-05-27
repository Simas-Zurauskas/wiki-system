# wiki-system — CLAUDE.md (`/wiki-system claude` · `/wiki-system notion claude`)

Create or update the project-root `CLAUDE.md` to a lean, high-signal **agent-context
file**. This is the **only** wiki-system prompt that writes `CLAUDE.md`. `init`,
`recheck`, and the Notion sync/recheck commands never touch it — they only suggest
running this one.

**Two invocations, one prompt — they differ only in where the Documentation section
links:**
- `/wiki-system claude` — links to the **local `wiki/`** files. The default; needs no
  Notion mirror.
- `/wiki-system notion claude` — links to the **published Notion pages** (URLs resolved
  from the `notion-sync.yaml` mapping). For teams whose doc home is Notion. See
  § NOTION VARIANT. It still writes a **local** `CLAUDE.md`.

Everything else — the lean standard, sections, prohibitions, on-request policy — is
identical across both.

`CLAUDE.md` is the first file an agent or developer reads to gain initial knowledge of
the project. Treat it as a crystal-clear, terse reference — **not** a changelog, a
journal, or a second copy of the wiki overview.

---

## TWO ROOTS — IMPORTANT

This skill operates with two unrelated roots. Never confuse them.

| Root | What lives there | How to reference |
| --- | --- | --- |
| **Skill files** (this `claude-md.md`, `SKILL.md`, `init.md`, `spec/`, …) | Prompt files | Paths inside this prompt are relative to *this file*; the skill machinery resolves them. |
| **Project files** (`CLAUDE.md`, `wiki/`, target repos, `wiki/.internal/plan.yaml`) | The user's actual project | Paths are relative to the user's **current working directory**. |

The file you write — `CLAUDE.md` — is a **project file** at the root of CWD.

---

## PHILOSOPHY — DOCS ARE REFRESHED ON REQUEST, NOT ON THE FLY

This is the stance this command bakes into the `CLAUDE.md` it writes, and it governs
this command's own behavior:

- The wiki and `CLAUDE.md` are refreshed **only when a human explicitly asks**, by
  running a wiki-system command. They are **not** updated automatically as a side
  effect of shipping features, fixing bugs, or refactoring.
- Out-of-band doc edits during feature work drift, duplicate, and conflict with the
  next regeneration. Keeping documentation a deliberate, on-demand act is what keeps
  it trustworthy.
- Therefore the `CLAUDE.md` you generate must **instruct future agents not to update
  `wiki/` or `CLAUDE.md` as part of unrelated work** — and point them at the
  wiki-system commands for when a refresh is actually wanted.

Do not reintroduce "update the docs whenever you change the code" guidance. That is the
exact behavior this command exists to remove.

---

## PHASE C0: PREFLIGHT

1. `pwd` to confirm CWD; `ls -la` to confirm it looks like a project root (code/repos,
   not `~` or `/`). If wrong, halt and ask where the project lives.
2. Note whether `CLAUDE.md` exists → **update** vs **create**.
3. Note whether a wiki exists (`wiki/OVERVIEW.md` and/or `wiki/.internal/plan.yaml`).
   This decides how you gather facts in C1.

## PHASE C1: GATHER FACTS (cheapest source first — do NOT do a full init-style scan)

Synthesize the project's identity, layout, conventions, and commands from the cheapest
sufficient source. Stop as soon as you have enough to fill the C2 sections.

1. **Existing `CLAUDE.md`** — read it. Preserve everything still accurate; you are
   refining, not discarding. Keep any `<!-- AUTOREGEN_SKIP_BEGIN -->…<!-- AUTOREGEN_SKIP_END -->`
   hand-edit zones **verbatim**.
2. **The wiki, if present** — `wiki/OVERVIEW.md` (product description, layout,
   architecture) and `wiki/.internal/plan.yaml` (`meta` block: repos, tracks, product
   description). This is already-synthesized, authoritative project knowledge — prefer
   it over re-deriving from source.
3. **Repo metadata** — the root `README.md` / `package.json` `description`, and each
   target repo's `README.md` + `package.json` `description` + scripts (for the
   build/run/test table).
4. **Light structural scan, only if 1–3 are insufficient** — list top-level
   directories and identify entry points. Do **not** read source files broadly; that is
   `init`'s job, not this command's.

If nothing yields a clear product description, **ask the user** — do not invent
positioning.

## PHASE C2: WRITE `CLAUDE.md`

Write **only** these sections, in this order. Omit any that doesn't apply. **Aim for
≤200 lines total.**

| Section | Content |
| --- | --- |
| One-paragraph product description | What the project **is** — one tight paragraph. |
| Layout | A table of top-level directories: stack + one-line purpose. |
| Inter-repo communication | 2–4 bullets **if multi-repo**; else omit. |
| Key conventions | 5–10 bullets max — load-bearing rules a new agent would otherwise violate (package manager, auth/gate stack, type-generation flow, deployment shape, …). Terse. |
| Build · run · test | Per-repo command table. |
| Documentation | One short pointer subsection — see the required template below. |

### The Documentation section (required template, on-request philosophy)

Adapt wording to the project, but it must say all of this and **no more**:

```markdown
## Documentation

All project documentation lives in `wiki/` and is the authoritative reference:
- <link to wiki/OVERVIEW.md> — entry point and system architecture
- <link to wiki/topics.md> — cross-cutting topic index
- <links to the main reference roots, e.g. wiki/library/...>

**Maintenance policy — on request only.** The wiki and this file are refreshed
*only* when explicitly asked, by running the `wiki-system` skill. Do **not** edit
`wiki/` or `CLAUDE.md` as a side effect of feature work, bug fixes, or refactors —
out-of-band edits drift and conflict with regeneration.

When a refresh is wanted, run:
- `/wiki-system recheck` — audit & refresh the local wiki against current code
- `/wiki-system claude` — refresh this file
- `/wiki-system notion sync` — push the wiki to Notion (if mirrored)

For a full rebuild after a major architectural change: `/wiki-system init`.
```

If no wiki exists yet, keep the policy paragraph and the command list, and note that
the wiki has not been generated (suggest `/wiki-system init`) instead of linking pages.

**Notion variant (`notion claude`):** replace the local `wiki/…` links above with the
corresponding **Notion page URLs** (§ NOTION VARIANT), and open the section with "All
project documentation is published to Notion and is the authoritative reference:". Keep
the same maintenance policy and command list — Notion readers still refresh via the same
on-request commands (`notion sync` re-publishes).

### HARD PROHIBITIONS — never put these in `CLAUDE.md`

- **No per-run history** — no `### This run (YYYY-MM-DD)` / `### Prior …` sections. Run
  narrative belongs in `wiki/.internal/trace/decisions.md`, not here.
- **No drifting counts** — never "97 leaf pages", "16 auth controllers". Counts live in
  the wiki; keep `CLAUDE.md` count-free.
- **No deep feature descriptions** — that is what `wiki/library/` is for. `CLAUDE.md`
  points; the wiki explains.
- **No restating `wiki/OVERVIEW.md`** — pointer + link only.
- **No documentation writing-standards / quality-bar / page-structure essays** — those
  belong in this skill, not in every project's `CLAUDE.md`.
- **No "update docs when you change code" guidance** — see § PHILOSOPHY.

If a section in the existing `CLAUDE.md` violates these rules, **remove it** as part of
this update (outside hand-edit zones). `CLAUDE.md` is a living file, not an append-only
journal.

## NOTION VARIANT (`/wiki-system notion claude`)

Run this branch when the invocation is `notion claude`. It produces the same `CLAUDE.md`
as the default, except the Documentation section links to the **published Notion pages**
instead of local files. It still writes a **local** `CLAUDE.md` — Notion is read-only here.

**Additional preflight (before C1):**

1. **Notion MCP must be connected** (the `notion-*` tools). If not, halt: "Connect the
   Notion MCP, then re-run `/wiki-system notion claude`."
2. **The mapping must exist** — `wiki/.internal/notion-sync.yaml`. If it is absent, **halt**
   and point the user at publishing first: "No Notion mapping yet. Run `/wiki-system notion
   sync` (or `notion recheck`) to establish it, then re-run `notion claude`." Do **not**
   crawl Notion to rebuild the mapping — that is `notion recheck`'s job.

**Resolve entry-point URLs (this replaces the local links — nothing else changes):**

3. `CLAUDE.md` links only to **entry points** — the root/OVERVIEW page, the `Library`
   page, the api/client/product section pages, and `Topics`. Find each one's
   `notion_page_id` in the mapping (`pages[].node` → its `notion_page_id`; the root is
   `meta.root_page_id`). Do **not** enumerate leaf pages.
4. For each entry-point id, get its URL. Prefer the **canonical URL** from the MCP
   (`notion-fetch` the id → use the returned page `url`). If a lookup fails, fall back to
   the derivable form `https://www.notion.so/<id-with-dashes-removed>` (the form stored as
   `meta.root_page_url`). These are a handful of targeted lookups — **never a full crawl**.
5. If a mapped entry-point page is missing or unreachable in Notion, link the nearest
   available ancestor (e.g. the `Library` page) rather than emit a dead link; flag it and
   suggest `notion sync`.

Then write `CLAUDE.md` per C2/C3 with the Notion-flavored Documentation section.

## PHASE C3: CONFIRM & FINALIZE

1. **If `CLAUDE.md` already exists**, do not silently overwrite. Show the user a short
   summary of what you'll change (sections added/removed/trimmed, approx line delta) and
   confirm before writing. On a fresh create, just write it.
2. Write `CLAUDE.md` at the project root. Preserve hand-edit zones verbatim.
3. If a wiki exists, append one line to `wiki/.internal/trace/decisions.md` recording
   that `CLAUDE.md` was regenerated (with the run header per `init.md` Phase 3e — the
   `generator_version` from the `VERSION` file + model id). If no wiki/trace exists,
   skip this. **Never** stamp a version or timestamp into `CLAUDE.md` itself.
4. Report the final line count and the sections written.
