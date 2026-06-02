Your task is to audit the **published Notion content against the source code**
and correct drift — **without a local wiki**. The ground truth is the source
code (the same ground truth `recheck.md` uses). The audited *subject* is what is
actually in Notion, fetched live. The local wiki is **not** consulted and **not**
assumed correct — this command does not read it, and it does not need it to exist.

This prompt is the **Notion recheck orchestrator** (`/wiki-system notion recheck`).
It is the Notion analog of `recheck.md`: where `recheck.md` verifies the **local
wiki against the source code**, this verifies the **live Notion pages against the
source code** and fixes drift **in Notion only**. It is **not** a re-sync — it does
not re-render local and push.

**It never reads or writes `wiki/library/` or `wiki/index.md`.** All run state lives
under `wiki/.internal/`. This is the deliberate design that lets someone refresh the
Notion docs against current code on a checkout that carries the `.internal/` state
but no built wiki at all (a fresh clone, a different machine, a repo where `wiki/`
is gitignored).

It composes three existing contracts and does not redefine them:
- `specialists/verifier.md` — the per-page accuracy check (Notion content vs `scope_files`).
- `specialists/ai.md` / `specialists/technical.md` / `specialists/product.md` — regenerate a drifted page from code (per the page's `owner_agent` / verifier mode), run **in-memory** (see § THE IN-MEMORY WRITER).
- `notion.md` — render + push (N3.1, child-preservation), top-down create (N2), orphans (N4), the mapping.

It resolves each page's `scope_files` and `owner_agent` from the **mapping**
(`wiki/.internal/notion-sync.yaml`; `spec/notion-sync-schema.md`) — the code anchor
seeded there by `notion sync`. `wiki/.internal/plan.yaml` is used as a fresher
override **if it happens to be present**, but is not required.

---

## TWO ROOTS (+ the Notion namespace)

Same as `notion.md`. **Skill files** (this `notion-recheck.md`, `notion.md`,
`specialists/`, `spec/`) are referenced relative to this prompt. **Project files**
(`wiki/.internal/notion-sync.yaml`, the optional `wiki/.internal/plan.yaml`, the
source repos) are relative to CWD — **except `wiki/library/` and `wiki/index.md`,
which this command does not touch at all.** The **Notion workspace** is reached only
through the `notion-*` MCP tools.

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
| "Is what's *published in Notion* still accurate against the code?" | ✅ this prompt | |
| "Refresh the Notion docs against current code — I don't have / don't want to rebuild the local wiki" | ✅ this prompt | |
| "Someone edited pages in Notion — are those edits correct, and fix them if not" | ✅ this prompt | |
| "I edited local pages; just push them" | | `notion sync` (push, no audit) |
| "Audit the *local* wiki vs code, and fix it locally" | | `recheck.md` |

**Three commands, three jobs:**
- **`notion sync`** (`notion.md`) — push disk → Notion, trusting local hashes; also
  seeds the `scope_files`/`owner_agent` code anchor into the mapping. Needs the local wiki.
- **`recheck`** (`recheck.md`) — verify the **local** wiki against the code; fix local.
- **`notion recheck`** (this) — verify the **live Notion** content against the
  code; fix the pages that drifted, **in Notion only**. Needs **no local wiki**.

---

## KEY PRINCIPLES (read before auditing)

- **Ground truth is the source code.** Not local, not Notion. Every verifiable
  page is checked against its `scope_files`, exactly as `recheck.md` does — the
  difference is only *which copy of the prose* gets checked: the live Notion page.
- **The code anchor comes from the mapping, not the wiki.** A page's `scope_files`
  and `owner_agent` are read from `wiki/.internal/notion-sync.yaml` (seeded by
  `notion sync`). If `wiki/.internal/plan.yaml` is present, prefer it (freshest) and
  fall back to the mapping. Never open a `wiki/library/` file to discover them.
- **The audited subject is the live Notion content.** Fetch it to a scratch draft
  under `wiki/.internal/` and verify *that*. Do not assume any local copy is correct.
- **Fixes land in Notion only.** A page that fails verification is regenerated from
  its `scope_files` by an **in-memory** writer and pushed to Notion. **No local file
  is written** (unlike `recheck.md`). Because local is never written, a later
  `notion sync` from a populated, stale checkout could overwrite a fix here (sync
  trusts local hashes) — this is **flagged prominently in the report**, with the
  remedy: run `recheck` then `notion sync` from one checkout to converge.
- **`wiki/library/` and `wiki/index.md` are never read or written.** This is a hard
  invariant and a quality gate (NR5). The only project paths touched are source code
  (read) and `wiki/.internal/` (read + write).
- **A page with no code anchor is un-auditable — never silently passed.** If neither
  the mapping nor a present `plan.yaml` gives a page `scope_files`, there is no code
  to verify it against. Report it as `un-auditable` (degraded), do **not** regenerate
  it (a writer over zero files produces hollow content), and do **not** mark it pass.
- **Derived pages have no code to check and no local file to reconcile to.** The root
  page body (`wiki/index.md`) and the `Library` overview are orchestrator-synthesized
  and have no `scope_files`; in no-local mode there is also no local file to compare
  against. **Leave them as-is and flag** "run `/wiki-system recheck` then `notion sync`
  to refresh the root/overview." This variant cedes derived pages to that pipeline.
- **`Notes` is human-owned.** Never audited, never overwritten; recreated only if a
  human deleted it.
- **Nothing destructive happens silently.** Orphan archiving asks (per `notion.md`
  N4). Foreign pages (a human added, never ours) are left untouched and reported.

---

## THE IN-MEMORY WRITER

Writers (`specialists/{ai,technical,product}.md`) are hard-constrained to write
their output only under `wiki/library/<track>/`. This command must never write
there. So it dispatches each writer in **return-markdown mode**: the brief instructs
the writer to **regenerate the full page from its `scope_files` and return the
corrected markdown as its final message — do NOT use the Write tool, do NOT write
any file.** The orchestrator captures the returned markdown and pushes it to Notion
(NR3). Because the writer writes no file, its `wiki/library/` output constraint is
never exercised. (This is the same pattern the CI counterpart uses for the identical
no-local flow.) The writer's regeneration logic — read every `scope_file`, rewrite
the whole page, never append — is otherwise used unchanged.

---

## ROLE

You are an audit-and-correct orchestrator. Your job, in order:

1. Preflight; resolve the root page and the mapping (rebuild from Notion if stale);
   resolve each page's code anchor (`scope_files`/`owner_agent`) from the mapping or
   an optional `plan.yaml`.
2. Walk Notion, match pages to mapping nodes, classify them.
3. Verify each verifiable page's **live Notion content** against its `scope_files`.
4. Correct drift: regenerate failing pages from code (in-memory) and push to Notion
   (bounded retry). No local write.
5. Reconcile structure (missing / orphan / dead / foreign / moved / renamed);
   `Notes` untouched.
6. Finalize: update the mapping (refresh hashes; preserve the code anchor) and write
   the audit report.

You write `wiki/.internal/notion-sync.yaml`, `wiki/.internal/notion-recheck-report.md`,
the per-page verifier reports under `wiki/.internal/verification/`, fetched scratch
drafts under `wiki/.internal/notion-recheck/`, and `wiki/.internal/verification/_failures.md`.
You never touch `wiki/library/`, `wiki/index.md`, or `wiki/notes/`, and you never
publish `wiki/.internal/`.

---

## PHASE NR0: PREFLIGHT, ROOT & CODE ANCHOR

Sequential. (MCP gate + markdown spec first, per § HARD DEPENDENCY.)

1. **No local-wiki check.** Do **not** require `wiki/library/` to exist; do not look
   for it. The audit subject is fetched from Notion, and the code anchor comes from
   `wiki/.internal/notion-sync.yaml` + the source repos.
2. **Resolve the root page** — `meta.root_page_id` from `notion-sync.yaml` if present;
   else a passed argument; else ask, or `notion-search` by title and confirm.
   `notion-fetch` it to confirm access. (Unrecoverable only if there is no mapping AND
   no supplied root — then ask for the root URL.)
3. **Load the mapping as the code anchor.** Read `wiki/.internal/notion-sync.yaml`.
   This is now the primary input: it carries, per node, the `notion_page_id`,
   `notion_content_hash`, and — when a prior `notion sync` seeded them — `scope_files`
   and `owner_agent` (`spec/notion-sync-schema.md`). If the file is absent or invalid,
   that is **not** fatal: NR1 rebuilds the structure from Notion (but a rebuilt map has
   no `scope_files` — see step 5).
4. **Optional fresher anchor — `plan.yaml`.** If `wiki/.internal/plan.yaml` is present,
   load it and **prefer** its `scope_files`/`owner_agent` (joined by `path` == the
   node key) over the mapping's copy — it is the freshest source. Its absence is fine;
   `--no-local` does not require it. Note `meta.generator_version` from whichever source
   is authoritative: if it differs from the current generator (skill `VERSION` + model
   id), audit **all** pages this run rather than skipping unchanged ones (NR2.1).
5. **Establish the code anchor per page.** For each page, `scope_files` resolves to
   (plan.yaml entry if present) → (mapping `scope_files` if seeded) → **none**. A page
   that resolves to **none** is `un-auditable`: there is no code ground truth. Do not
   verify or regenerate it; record it for the report and tell the user to run
   `notion sync` once (to seed the anchor) or keep `plan.yaml` committed. If *every*
   page is un-auditable (e.g. a rebuilt map with no `plan.yaml`), the run degrades to
   **structural-only** (NR4) — say so loudly up front; this is not an accuracy audit.

---

## PHASE NR1: WALK NOTION, MATCH, CLASSIFY

### NR1.1 Walk the live Notion tree
From the root, `notion-fetch` and recurse through child pages, building the live
tree (id, title, parent, position).

### NR1.2 Match Notion pages to mapping nodes (no disk)
Match each live Notion page to a mapping node — by cached `notion_page_id` first,
then, when the cache is stale/absent, by **tree position + live Notion title**
against the mapping's node structure. The match yields the node's `scope_files` and
`owner_agent` (the code anchor from NR0). **This match never reads `wiki/library/`.**
The page's title/H1 is taken from the **live Notion page property**, never a disk H1
(there is no disk file to read). Rebuild the authoritative mapping from these matches.

### NR1.3 Classify each page

| Class | Pages | Handling |
| --- | --- | --- |
| **verifiable** | a node that has `scope_files` (from the anchor) | Audited vs code (NR2–NR3). |
| **un-auditable** | a node with no resolvable `scope_files` | Reported, NOT verified or regenerated (NR0.5). |
| **derived** | the root body, the `Library` overview — synthesized, no `scope_files`, no local file | Left as-is and flagged (NR3.3). |
| **working** | the `Notes` page | Skipped entirely (human-owned). |
| **structural** | `missing_in_notion` / `dead_id` / `orphan_in_notion` / `foreign` / `moved` / `renamed` | Reconciled in NR4. |

---

## PHASE NR2: AUDIT NOTION CONTENT AGAINST CODE (verify-first)

Parallel. The Notion analog of `recheck.md` Phase R3, but the draft under test is the
**live Notion page**. Verifiers are read-only and parallel — use the worker-pool cap
from `init.md` § SCALING RULES.

### NR2.1 Skip what cannot have drifted
A verifiable page needs re-verification only if its **Notion content** changed (live
serialization hash ≠ stored `notion_content_hash`) **or** its **code** changed (any
`scope_files` changed since `meta.synced_at`, via `git diff` in the source repos). If
both are unchanged, skip it (record "unchanged"). On a rebuilt mapping with no
baselines, or on a generator-version change (NR0.4), verify everything.

### NR2.2 Verify each remaining page
For each page to audit:
1. `notion-fetch` its live content and write it to a scratch draft at
   `wiki/.internal/notion-recheck/<page-id>.fetched.md`. This is Notion-flavored
   markdown (`<page>` / `<mention-page>` / `<table>` wrappers); the verifier extracts
   factual claims from the prose and ignores the navigation wrappers, so it runs
   unchanged. It is verifying Notion's serialization, not any local file.
2. Dispatch a verifier (`specialists/verifier.md`, mode from `owner_agent`) using the
   verifier brief template from `init.md` § SUB-AGENT DELEGATION PRINCIPLES, **with one
   override line:** `page_path` is the scratch draft above — a fetched-Notion draft
   under `wiki/.internal/`, **not** a `wiki/library/` file (verifier.md's "page_path is
   always under wiki/library/" is a descriptive default; this assignment overrides it).
   Pass `scope_files` from the code anchor and `complexity` if known. Write the report
   to `wiki/.internal/verification/<page-id>.notion.yaml` (the `.notion` suffix keeps
   it distinct from local-recheck reports).
3. **Partial scope guard.** If `scope_files` span repos not present in this checkout,
   some globs won't resolve. Read the verifier's `files_read` vs `files_total`; if a
   **material fraction** is unreadable (default: >25% of files, or any file the page's
   top claims depend on), mark the page `degraded` (un-soundly verifiable) and name the
   missing repos — do **not** fix from a half-blind read. (At the project root, with
   all repos present, cross-repo pages ARE fully auditable — an advantage over a
   single-repo CI checkout.)
4. Collect the verdict (`pass` / `fail_soft` / `fail_hard`).

---

## PHASE NR3: CORRECT DRIFT (regenerate from code → Notion only)

### NR3.1 Regenerate failing pages (in-memory)
For each `fail_soft`/`fail_hard` page, dispatch the page's writer
(`specialists/{ai,technical,product}.md`, per `owner_agent`) in **return-markdown
mode** (§ THE IN-MEMORY WRITER): regenerate the full page from `scope_files`, attach
the verifier's `issues` list (the auto-fix re-dispatch protocol from `init.md` Phase
3d), and **return the markdown — write no file.** Bounded: **one** regenerate→re-verify
retry per page (identical to `recheck.md` R4.3). A writer that returns `skipped`
(disagrees with the verifier) keeps the non-pass verdict and is surfaced as a
calibration notice — do not push. A `split_request` is logged and not auto-acted on
(it needs a manual `init`); record it in `_failures.md`.

### NR3.2 Push the fix to Notion (only)
Re-verify the returned markdown **before pushing** — `fail_hard` never corrupts Notion;
only verified content is pushed. A page that now passes is rendered via `notion.md`
N3.1 (resolve cross-links to Notion mentions, append child `<page>` refs enumerated
from the **live Notion tree + mapping**, never disk) and pushed with `replace_content`,
`allow_deleting_content` **off** (child-preservation). **No local `wiki/library/` file
is written.** A page that still fails after the one retry is recorded `fail_hard` in
`wiki/.internal/verification/_failures.md` and **left as-is in Notion** — never ship
content the verifier rejects. Then refresh `notion_content_hash` (hash of Notion's
serialization after the push) so the next audit can skip it.

**Preserve human-accepted zones.** If the fetched Notion content contains an
`AUTOREGEN_SKIP` block (verifier ignores it), carry that block through verbatim on the
push — the local original was never read, so this is the only way to keep it. If a
page's only failing region is inside a skip zone, treat it accepted and do not
regenerate. (Caveat: Notion's markdown↔blocks round-trip may strip the HTML-comment
markers; when a page is human-edited — `notion_content_hash` changed without a
`scope_files` change — but no skip zone is detectable, note the round-trip fragility in
the report.) Re-emit the provenance banner verbatim (never interpolate a timestamp, or
every page re-hashes each run).

### NR3.3 Derived pages — leave and flag
The root body and `Library` overview have no `scope_files` and no readable local file
in this mode. **Leave the live Notion page untouched** and flag in the report:
"derived page not auditable in no-local mode; run `/wiki-system recheck` then
`notion sync` to refresh the root/overview." Do not synthesize a replacement from
child titles (it would publish a thinner overview than the real one).

---

## PHASE NR4: STRUCTURAL RECONCILIATION

Independent of content. Apply per class from NR1.3:

| Class | Action |
| --- | --- |
| `missing_in_notion` / `dead_id` | Recreate under the correct parent (top-down, `notion.md` N2). If the node has `scope_files`, regenerate its body from code (in-memory writer) and use the writer's H1 as the title; if it is un-auditable, create an empty placeholder and flag it. Overwrite any stale `notion_page_id`. |
| `orphan_in_notion` | Mapped node whose page should no longer exist → surface and **ask** (archive / leave / rename), per `notion.md` N4. |
| `foreign` | A human-added page that was never ours → **leave untouched**, report. |
| `moved` | Notion parent ≠ mapped parent → move back (`notion-move-pages`), report. |
| `renamed` | Notion title differs from the expected title. With **no disk H1** to compare against, only reset a title when an authoritative expected title is available (the writer's regenerated H1 on a just-fixed page); otherwise **leave and report** rather than guess. |
| track disabled | `owner_agent` not in the enabled tracks but published pages still exist → classify structural, do **not** regenerate (no writer), surface and ask (archive orphan-style / re-enable). Never auto-delete. |
| `working` | Untouched. Recreate with the placeholder only if missing. |

Persist the mapping incrementally (resumability). On a Notion MCP rate-limit/drop
mid-run, record the dispatch failure in `_failures.md` and let the page defer rather
than retry unboundedly; a resumed run re-derives the skip set from persisted hashes.

---

## PHASE NR5: FINALIZE

1. **Persist the mapping** — `wiki/.internal/notion-sync.yaml`, valid against
   `spec/notion-sync-schema.md`, with refreshed `content_hash`/`notion_content_hash`
   per audited page, the **preserved `scope_files`/`owner_agent` anchor** (carried
   forward; refreshed from `plan.yaml` if it was present), and `meta.synced_at`.
2. **Write the report** — `wiki/.internal/notion-recheck-report.md`:

```markdown
# Notion recheck (audit vs source code, no-local) — <ISO timestamp>

Root page: <url>
Mapping: loaded-from-cache | rebuilt-from-Notion
Code anchor: plan.yaml | mapping (seeded) | NONE (structural-only)

## Audit
- Verified: <n>   Skipped (unchanged): <n>   Un-auditable (no scope_files): <n>
- Degraded (partial cross-repo scope): <n>
- Drifted from code → fixed in Notion: <n>
- Still failing after one retry (fail_hard, left as-is): <n>

## Pages corrected (regenerated from code, pushed to Notion)
| Page | Verdict | What drifted (top issue) |
| --- | --- | --- |
...

## Structure
- Recreated (missing/dead): <n>   Moved: <n>   Renamed: <n>
- Orphans: <n> (archived / left / renamed)   Foreign left: <n>

## Flags
- ⚠ Clobber risk: fixes landed in Notion only. A later `notion sync` from a
  populated, stale checkout trusts local hashes and could overwrite them. To
  converge, run `recheck` then `notion sync` from one checkout.
- Derived pages left as-is (run `recheck` then `notion sync` to refresh root/overview): ...
- Un-auditable pages (no scope_files — seed via `notion sync`/`plan.yaml`): ...
- fail_hard pages needing human review: ...
```

3. **Summarize** — counts, root URL, what was corrected (and that the fix landed in
   **Notion only**, with the clobber-risk note), what's un-auditable, what's still
   failing, and whether the mapping was rebuilt. Tight.

---

## EDGE CASES

- **A human edit that is correct** — verifies `pass` against code → left in place
  (its wording may differ; both are accurate). Only *inaccurate* content is regenerated.
- **A human edit that is wrong** — fails against code → regenerated from code, fixed in
  Notion. The incorrect text is discarded; report it.
- **Code changed since publish** — the Notion page now contradicts the code → fails →
  regenerated. The main steady-state case.
- **No code anchor** — a page with no `scope_files` from mapping or plan is
  `un-auditable`; reported, not verified or regenerated (NR0.5). Never a fake pass.
- **Lost / fresh-checkout mapping** — NR0 resolves the root; NR1 rebuilds structure from
  Notion. Without `plan.yaml`, a rebuilt map has no `scope_files` → most pages degrade to
  un-auditable → the run is structural-only; say so. Report it as a full re-establish.
- **Empty/stub live Notion page** — the verifier short-circuits to `fail_hard` (scope_gap
  critical) on an empty draft; treat as incomplete-stub and regenerate from code.
- **Notion-only fix vs a later `notion sync`** — inherent clobber risk (sync trusts local
  hashes); flagged prominently, never silently dropped. Do **not** try to "fix" it by
  marking local hashes stale — there is no local content to push, so that would overwrite
  the correct Notion fix with absent/stale local.
- **`plan.yaml` present** — preferred for `scope_files`/`owner_agent` (freshest); the
  mapping's seeded copy is the fallback. Reading `plan.yaml` is allowed (it is under
  `wiki/.internal/`); reading `wiki/library/` is not.
- **Page deleted/moved/renamed in Notion** — structural (NR4), independent of the content
  audit; rename reset only with an authoritative expected title.
- **Serialization noise** — never byte-compare; the content check is the verifier (claims
  vs code), the skip check is `notion_content_hash` (Notion's own serialization).

---

## QUALITY GATES

- [ ] **No local wiki touched.** No file under `wiki/library/` and not `wiki/index.md`
      was read or written this run. (The hard invariant of this command.)
- [ ] **Audited against code, not local.** Every verifiable page's verdict came from a
      verifier run over the **live Notion content** + its `scope_files` — never a
      local-vs-Notion diff and never a read of a `wiki/library/` page.
- [ ] **Fixes in Notion only, verified before push.** Every corrected page was pushed to
      Notion after passing re-verification; none was written locally. No page left in
      Notion with a `fail_hard` regeneration — such pages are in `_failures.md`.
- [ ] **Un-auditable pages reported, not passed.** Pages with no `scope_files` are flagged,
      never silently marked accurate.
- [ ] **Clobber risk surfaced.** The report states the Notion-only fixes could be
      overwritten by a later `notion sync`, with the convergence remedy.
- [ ] **`Notes` untouched; foreign untouched.** Neither was audited, moved, renamed, or
      overwritten.
- [ ] **Child preservation.** No root/folder push dropped a child sub-page (children
      enumerated from the live Notion tree + mapping, not disk).
- [ ] **Mapping authoritative.** Rebuilt from Notion where the cache was stale; the
      `scope_files`/`owner_agent` anchor is preserved; every live managed page maps to one
      node or an explicit orphan/foreign entry.
- [ ] **State only under `wiki/.internal/`** (read + written); never published to Notion.

---

## CONSTRAINTS

- **Ground truth is the source code.** This command verifies Notion content against
  `scope_files`; it does not treat local as correct, and it is not a re-sync.
- **No local wiki.** It never reads or writes `wiki/library/` or `wiki/index.md`. Fixes
  land in Notion only. The code anchor comes from the mapping (or an optional `plan.yaml`).
- **In-memory writers.** Regeneration runs writers in return-markdown mode; no writer
  writes a file this run.
- **Bounded retry.** One regenerate→re-verify per page (identical to `recheck.md`).
- **`Notes` and foreign pages are sacrosanct.** Never audited or overwritten; orphans only
  ever archived with explicit confirmation.
- **MCP-only Notion access**; **markdown spec is authoritative** for Notion syntax.

---

## RELATIONSHIP TO OTHER PROMPTS

| File | Relationship |
| --- | --- |
| `specialists/verifier.md` | The per-page audit, run over live Notion content + `scope_files`, with a brief override pointing `page_path` at the `wiki/.internal/` scratch draft. Invoked unchanged. |
| `specialists/ai.md` / `technical.md` / `product.md` | Regenerate a drifted page from code, in **return-markdown mode** (§ THE IN-MEMORY WRITER). Invoked unchanged; no file written. |
| `notion.md` | Render + push (N3.1), child-preservation, top-down create (N2), orphans (N4), the mapping — and the `notion sync` step that **seeds** the `scope_files`/`owner_agent` code anchor this command relies on. Reused, not redefined. |
| `recheck.md` | The local analog — verifies the *local* wiki against code and fixes it locally. This verifies the *published Notion* content against code and fixes it in Notion. Run `recheck` then `notion sync` to refresh derived pages and to converge local with a Notion-only fix. |
| `spec/notion-sync-schema.md` | The mapping: the `scope_files`/`owner_agent` code anchor, `notion_content_hash` as the audit-skip signal, and the rebuild-from-Notion semantics. |
| `init.md` | Source of the verifier/writer brief templates and the worker-pool scaling rules. |
