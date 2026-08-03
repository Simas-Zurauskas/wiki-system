The canonical schema for `wiki/.internal/plan.yaml` — the structured artifact produced
by the orchestrator in Phase 2 and consumed by every writer and verifier
downstream.

This file is a reference, not a prompt. Agents read it when they need to
understand a field's meaning or the invariants a plan must satisfy. The
orchestrator uses it when writing the plan; writers and verifiers use it
when reading the plan.

---

## WHO READS THIS

| Agent                                    | When                                                        |
| ---------------------------------------- | ----------------------------------------------------------- |
| Orchestrator (`../init.md`)            | Phase 2, when writing `wiki/.internal/plan.yaml`                     |
| Writer (`../specialists/technical.md` under orch.) | At the start of each section's writing phase                |
| Writer (`../specialists/product.md` under orch.)   | Same                                                        |
| Verifier (`../specialists/verifier.md`)            | Phase 3d, when checking a draft's claims against the plan   |

If the schema below conflicts with any inline description elsewhere, this
file wins. Update this file first, then update references.

---

## SCHEMA

```yaml
meta:
  product_description: "<one paragraph — from Configuration or inferred>"
  state: bootstrap | growth | maintenance
  tracks: [ai]                # enabled tracks, a non-empty subset of {ai, technical, product}.
                              # DEFAULT [ai] (ai is always on; product and technical
                              # are opt-in). The orchestrator only plans sections/pages whose
                              # owner_agent is in this list; a disabled track costs nothing.
                              # See ../init.md § Documentation Tracks for the selection flow + defaults.
  wiki_dir: wiki-<project>    # docs folder name (its own git repo, unique per project, e.g. wiki-acme).
                              # Commands resolve the docs root by the wiki-*/ dir holding this
                              # .internal/plan.yaml. In every path below, `wiki/` is the LOGICAL
                              # docs root and resolves to wiki_dir at runtime.
  repos:                      # the project's canonical repo set (a collection of repos), matched
                              # to workspace folders BY FOLDER NAME. A repo absent from the workspace
                              # is skipped as partial access (../recheck.md Phase R1 step 5) — not an error.
    - name: <folder name>     # the repo's folder name in the workspace (clone under this name)
      path: <workspace-relative folder>   # normally the same as name
  generated_at: <ISO-8601 date>
  generator_version: "wiki-system v<N> · <model-id>"  # skill version + model that produced this plan;
                                                       # lets recheck detect generator drift, not just source drift
  schema_version: "1.4"  # bump on breaking changes to this schema
                         # 1.2: folder index file renamed OVERVIEW.md -> index.md; the technical
                         #      track is always nested under wiki/TECHNICAL/<repo>/, one folder
                         #      per repo, never directly under wiki/TECHNICAL/.
                         # 1.3: third track `ai` (wiki/AI/) added — agent-optimized,
                         #      code-grounded, default-ON; owner_agent gains the value `ai`;
                         #      meta.tracks records which tracks are enabled (default then
                         #      [ai, product]; the default is now [ai] — see `tracks` above).
                         # 1.4: workspace model — meta.wiki_dir records the per-project docs folder
                         #      name (wiki-<project>); `wiki/` in paths is the logical docs root
                         #      resolved to wiki_dir; repos matched by folder name; an absent repo
                         #      is partial access (recheck R1 step 5), not an error.

# Sections correspond to folders under wiki/<TRACK>/, where <TRACK> is one of the
# uppercase literals AI, TECHNICAL, PRODUCT. There are up to THREE tracks:
#   - ai        (wiki/AI/)              — agent-optimized, ALWAYS ON; one `ai` section
#                                          (parent null); see ../specialists/ai.md.
#   - technical (wiki/TECHNICAL/<repo>/) — repo-scoped developer reference (opt-in); ALWAYS
#                                          nested one folder per repo, even for a single repo.
#   - product   (wiki/PRODUCT/)          — feature-scoped, code-free (opt-in).
# Only tracks listed in meta.tracks are planned. The orchestrator never plans content at
# the wiki root — those are hand-written.
# A section with has_overview: true produces an index.md at that folder.
# Nesting is arbitrary depth — use it. The scope-to-depth table below forces it.
sections:
  - id: <stable slug, e.g. technical/api/models or ai/contracts>
    path: wiki/<TRACK>/<slug>/
    parent: <parent section id, or null for top-level>
    owner_agent: technical | product | ai
    has_overview: true | false
    scope_loc_estimate: <integer — sum of source LOC this section documents>
    split_reason: "<why this section is a folder rather than a single page>"  # optional
    scan_summary: |
      <2-5 line structured summary: tech stack, key subsystems, entry points.
      This is what writers receive in lieu of re-scanning the project.>

# Pages are leaf documents. Page paths always start with wiki/<TRACK>/.
pages:
  - id: <stable slug, e.g. technical/api/models/user>
    path: wiki/<TRACK>/<slug>.md
    section: <section id this page belongs to>
    owner_agent: technical | product | ai
    scope_files: [<glob or file paths relative to project root>]
    scope_loc_estimate: <integer>
    complexity: S | M | L | XL
    links_to: [<page or section ids this page must cross-link>]
    section_parity: strict | suggested | none
    state: new | rewrite | unchanged
    split_allowed: true | false  # may the page worker submit a split_request?

# Execution graph — how the scheduler fans out work.
execution:
  parallel_tracks:
    - <list of section ids that can run concurrently>
  depends_on:
    <section id>: [<section ids that must finish first>]  # usually empty
  stub_first: true  # always; see Phase 3a in ../init.md
```

Field order is free. Every listed field is required unless marked optional.

---

## FIELD SEMANTICS

### `sections[]`

- **id** — stable slug; used as the key when agents reference the section.
  Must match the path structure: `technical/api/models` → `wiki/TECHNICAL/api/models/`.
- **parent** — the section id one level up. `null` for a top-level track
  section. The track sections `ai`, `technical`, and `product` have
  `parent: null`; each repo section (e.g. `api`) has `parent: technical`.
- **owner_agent** — which specialist writes this section, and which verifier
  `mode` checks it. `technical` → repo-scoped developer docs (`../specialists/technical.md`);
  `product` → feature-scoped, code-free docs (`../specialists/product.md`);
  `ai` → agent-optimized, code-grounded docs under `wiki/AI/`
  (`../specialists/ai.md`). The value must be one of the enabled `meta.tracks`.
- **has_overview** — `true` means the section is a folder with an
  `index.md`. `false` means the section is a single leaf page (in which
  case `path` should end in `.md`, not `/`).
- **scope_loc_estimate** — sum of source LOC across all pages in this
  section. Used by the scope-to-depth rule.
- **scan_summary** — short structured summary of the subsystem. Writers use
  this instead of re-scanning the whole project; verifiers do not use it.

### `pages[]`

- **id** — stable slug matching `path` minus `wiki/<TRACK>/` and `.md`
  (e.g., `wiki/TECHNICAL/api/authentication.md` → id
  `technical/api/authentication`, or a shorter convention such as
  `api/authentication` that keeps the repo name but drops the `technical/`
  prefix — pick one convention per project and document it; whichever you choose,
  keep it stable across runs so verification report filenames don't churn).
- **section** — the id of the section this page belongs to. Every page
  belongs to exactly one section. The orchestrator-generated root file
  (`wiki/index.md`) is not part of the plan; it has no `section` because it
  is not in `pages[]` at all.
- **scope_files** — list of file paths or globs in the source repo that
  this page documents. The writer reads these; the verifier verifies
  claims against these.
- **scope_loc_estimate** — LOC count over `scope_files`. If the real scope
  exceeds this by a significant margin during the writer's deep scan, that
  is grounds for a `split_request`.
- **complexity** — coarse size bucket used for scheduling and for deciding
  whether a verifier pass is warranted:
  - `S` — 300–800 LOC, simple. Verifier may be skipped on runs where
    verification is selective.
  - `M` — 800–1,500 LOC, standard. Verifier always runs.
  - `L` — 1,500–3,000 LOC, substantial. Verifier always runs; extra weight
    in scheduler priority.
  - `XL` — 3,000+ LOC. Should almost always have been split per the
    scope-to-depth table; flag as a planning error.
- **links_to** — ids of other pages or sections this page must
  cross-reference. The orchestrator's stub-out phase uses this to create
  placeholder targets before any writer runs, so cross-links always
  resolve.
- **section_parity** — whether counterpart pages are required in sibling
  sections:
  - `strict` — must exist in every sibling (e.g., `authentication` must
    appear in api, client, and product).
  - `suggested` — usually worth having but not required.
  - `none` — intentionally one-sided (e.g., client-only accessibility).
- **state** — lifecycle for this page:
  - `new` — did not exist in the prior plan.
  - `rewrite` — exists but source has drifted; must be re-written.
  - `unchanged` — source is unchanged since last generation; may be skipped.
- **split_allowed** — if `true`, the writer may return a `split_request`
  when the page's real scope exceeds the plan. If `false`, the page must
  remain flat (used for cross-repo integration summaries that should not
  fragment).

### `execution`

- **parallel_tracks** — lists of section ids that may be scheduled
  concurrently. Empty nested lists mean no explicit constraint; the
  scheduler fills its pool freely.
- **depends_on** — mapping from a section id to the set of section ids
  that must complete before it starts. Usually empty. Use it only when a
  section's content materially depends on another section having been
  written first (rare — cross-links use stub-first instead).
- **stub_first** — always `true`. Kept as a field so a future variant
  could disable stubbing for experimental runs.

---

## SCOPE-TO-DEPTH TABLE (CANONICAL)

The orchestrator applies this table before finalizing `sections` and
`pages`. Writers apply it recursively when evaluating whether to return a
`split_request`. Verifiers reference it when judging whether the plan was
correctly shaped. This table is authoritative for technical docs and for the
`ai` track's `reference/`, `contracts/`, `runbooks/`, and `map/` folders; the
product specialist uses a feature-based variant (see `../specialists/product.md`).
The `ai` track has a fixed top-level shape (`index`, `invariants`, `glossary`,
`contracts/`, `runbooks/`, `map/`, `reference/`) regardless of size — see
`../specialists/ai.md` — and applies this table only to size those folders.

| Source scope                              | Required structure                                                                 |
| ----------------------------------------- | ---------------------------------------------------------------------------------- |
| < 300 LOC or < 5 files                    | Fold into parent section; do not create a dedicated page                           |
| 300–1,500 LOC                             | Single `topic.md` page                                                             |
| 1,500–5,000 LOC across ≥2 concern areas   | Folder `topic/` with `index.md` + 2–5 child pages                               |
| 5,000+ LOC, or ≥3 distinct concern areas  | Folder `topic/` with `index.md` + children; children may themselves be folders  |

The rule applies recursively. A 5,000-LOC subsystem split into children of
1,800 LOC each that themselves cover multiple concern areas must split
again. Depth is not capped — structure matches the code.

---

## VERIFIER REPORT SCHEMA

Each verifier sub-agent writes a YAML report to
`wiki/.internal/verification/<page-id>.yaml`. The shape:

```yaml
page_id: <stable slug — same id as in wiki/.internal/plan.yaml pages[]>
page_path: wiki/<TRACK>/<slug>.md
mode: technical | product | ai
verified_at: <ISO-8601 timestamp>
verdict: pass | fail_soft | fail_hard

stats:
  total_claims: <integer>      # all claims considered, including resolved
  resolved: <integer>          # claims successfully verified against source — calibration
  consideration: <integer>     # minor; does NOT contribute to verdict
  improvement: <integer>       # material; 1–3 → fail_soft, 4+ → fail_hard
  critical: <integer>          # contradicted or central-unverified; any → fail_hard
  code_refs: <integer>         # product mode only; counted within `critical`
  omissions: <integer>         # material completeness gaps (verifier Step 3b); counted within their severity tier

issues:
  - id: <integer>
    status: unverified | contradicted | code_reference | scope_gap | omission
    severity: consideration | improvement | critical
    claim: "<exact quote or paraphrase>"
    page_location: "<line number, heading, or 'throughout'>"
    evidence: "<file:line, symbol, or 'not found in scope_files'>"
    recommendation: "<actionable instruction to the writer>"

scope_coverage:
  files_read: <integer>
  files_total: <integer>       # from scope_files
  files_skipped: []            # any files not read, with reason
```

**Verdict computation rules** (deterministic — must match what
`../specialists/verifier.md` § Step 5 specifies):

- `pass` — `critical == 0` AND `improvement == 0`. Any number of
  `consideration` items is tolerated.
- `fail_soft` — `critical == 0` AND `1 ≤ improvement ≤ 3`.
- `fail_hard` — `critical ≥ 1` OR `improvement ≥ 4`.

Consumers — the orchestrator's auto-fix step, and any downstream publish step
that chooses to gate on verdict — read this YAML. The `stats.resolved` field is
calibration signal — a clean `pass` with `resolved: 0` is suspicious (verifier didn't
extract any claims), distinguishable from `pass` with `resolved: 12`
(verifier did real work and found nothing wrong).

The `issues` list contains only non-`resolved` items. Resolved claims are
summarized by `stats.resolved` alone; do not enumerate them as issues.

The `omission` status is a **completeness** gap (something the page should cover
but doesn't), produced by the verifier's Step 3b. Unlike the other statuses
(which judge claims that ARE present), an `omission` judges what's *missing*. It
carries a severity like any issue and feeds the same verdict math — a missing
central subject is `critical`, a material secondary gap `improvement`. See
`../specialists/verifier.md` § Step 3b for the content-conditioned rules.

---

## _failures.md SCHEMA

`wiki/.internal/verification/_failures.md` is human-readable but
machine-parseable. Each `fail_hard` entry is a markdown section preceded by
a YAML frontmatter fence so the orchestrator's resolution gate
(`init.md` Phase 3d.5 / `recheck.md` R4.3) can read entries back
deterministically.

````markdown
---
page_id: <plan slug>
page_path: wiki/<TRACK>/<slug>.md
run_id: <ISO-8601 timestamp of the run that produced the failure>
verdict: fail_hard | fail_hard_post_user
verdict_reason: "<short string — e.g. '1 critical issue', '5 improvement issues', 'writer–verifier disagreement', 'incomplete stub'>"
tier2_attempted: true | false
tier2_verdict: pass | fail_soft | fail_hard | not_run
oscillation_signal: true | false       # issue categories differed across attempts
top_issues:                            # capped at 5 entries; severity desc then page_location-diverse
  - status: <verifier status>
    severity: <verifier severity>
    claim: "<one-line excerpt>"
    page_location: "<heading or line>"
    evidence: "<file:line or 'not found in scope_files'>"
prior_entry_count: <integer>           # how many prior _failures.md entries this page already has
resolution:
  status: pending | regenerated | patched | shrunken | accepted | deleted | deferred
  decided_at: <ISO-8601 timestamp, or null while pending>
  user_note: "<free-text from the user, optional>"
  outcome_verdict: pass | fail_hard_post_user | n/a
  # n/a is correct for accepted / deleted / deferred (no re-verification ran)
  accepted_until: <ISO date | null>    # REQUIRED when status == accepted AND the whole page was wrapped (not a localized section). Null when only a localized section was wrapped. On expiry, R1 surfaces the entry as a re-review candidate.
---

### <Page id or title>

<one-paragraph human-readable summary — same content as the verifier's final
message, kept here for skim-reading without parsing the frontmatter>
````

**Invariants:**

- The file is **append-only for entries** — never truncate or rewrite past
  entries. Old free-prose entries from before this schema landed remain
  readable but are not parsed by the gate; new entries must use frontmatter.
- The orchestrator updates `resolution.*` fields in place when the user
  decides on a pending entry. This is the **only** mutation allowed on a
  closed entry; the page-summary prose below the frontmatter is never
  rewritten.
- `resolution.status: pending` blocks run completion (see `../init.md`
  QUALITY GATES "Verification verdicts" and `../recheck.md` "Failures
  triaged"). Every other status is terminal for the run.
- `deferred` is the explicit "I'll deal with it later" choice. The next
  run's R1 surfaces deferred entries with priority.
- `fail_hard_post_user` records a user-initiated re-attempt
  (`regen_with_context` or `patch_scope`) that also failed. The entry is
  closed; the page ships in its failing state. The user can re-run the
  skill if they want another attempt; gate-time looping is forbidden by
  the same retry-cap rule that governs auto-fix.
- `accepted` and `deleted` carry no `outcome_verdict` (`n/a`). For
  `accepted`, the page-on-disk has been wrapped in
  `<!-- AUTOREGEN_SKIP_BEGIN/END -->` markers and ships as-is. For
  `deleted`, the page file and its `plan.yaml` entry are gone; sibling
  pages whose `links_to` referenced this id have been patched and
  re-verified.
- `shrunken` retains the page on disk with a stub block fenced by
  `<!-- AUTOREGEN_SKIP_BEGIN/END -->` covering the dropped sections.
  Available only when verifier issues localize to identifiable headings.
- Entries from prior runs that already have a terminal `resolution.status`
  are audit history — the current run does not re-prompt for them. Only
  `pending` entries flow into the current run's gate. `deferred` entries
  are surfaced in R1 for prioritization but do not auto-enter the gate
  unless this run's verifier produces a fresh `fail_hard` for the same
  page.
- **Per-run entry rule.** When a page fails again in a new run, the
  orchestrator **appends a new entry** for the new run — it does not
  mutate the prior entry. The prior entry's `resolution.status` (deferred
  / accepted / etc.) is preserved as-is. The new entry's
  `prior_entry_count` reflects the count of all prior entries for that
  `page_id`, and the gate presents the new entry alongside the most
  recent prior entry's summary so the user sees whether the failure mode
  changed.
- **Synthetic-stub entries.** When a page is an incomplete stub from a
  prior run (R1 detects this; the verifier is not dispatched), the
  orchestrator creates a synthetic entry with `verdict_reason: "incomplete
  stub"` and a single `top_issues` entry: `status: scope_gap`, `severity:
  critical`, `claim: "Page was never written (stub from prior run)"`,
  `evidence: "<page_path>:1"`, `recommendation: "Dispatch writer with
  scope or delete page"`. `tier2_attempted: false`, `tier2_verdict:
  not_run`.
- **Tier-2 dispatch failure.** If `strong_verifier_model` is configured
  but tier-2 dispatch fails (rate limit, model unavailable, network),
  set `tier2_attempted: true`, `tier2_verdict: not_run`, and include the
  dispatch failure reason in `verdict_reason` (e.g.
  `"5 improvement issues; tier-2 dispatch failed: rate_limit"`). The
  page proceeds to the gate; the failure is also recorded in
  `wiki/.internal/trace/decisions.md`.
- **`top_issues` cap.** At most 5 entries, selected by `severity` desc
  (critical first), then by `page_location` diversity (no two from the
  same heading). The full issue set remains in the per-page YAML report
  at `wiki/.internal/verification/<page-id>.yaml`.

**Consumers:**

- The Phase 3d.5 / R4.3 user resolution gate reads the queue of pending
  entries from this file and presents them to the user.
- Phase R1 of `recheck.md` reads `deferred` entries for next-run prioritization.
- The decision log (`wiki/.internal/trace/decisions.md`) records terminal
  resolutions for audit, but does not duplicate the issue detail — the
  `_failures.md` entry is the authoritative store.

---

## WORKER RETURN SCHEMA

A writer sub-agent's final message is machine-read by the orchestrator. It
returns **exactly one** of the following shapes (free prose may accompany the
summary case, but the structured blocks must parse). These are the only worker
return contracts; keep them as disciplined as the verifier report above.

**1. Normal completion** — pages written:

```yaml
summary:
  pages_written: [<page id>, ...]
  integration_points: ["<one-line note>", ...]   # optional
cross_section_ripples: [<page id>, ...]           # sibling pages this change may affect; [] if none
```

**2. Split request** — scope exceeds the plan (only if `split_allowed: true`):

```yaml
split_request:
  parent_page: <page id>
  reason: "<observed LOC / concern areas vs. the plan estimate>"
  proposed_structure:
    parent_becomes: overview
    children:
      - id: <slug>
        path: wiki/<TRACK>/<slug>.md       # MUST start with wiki/<TRACK>/ and end in .md
        scope_files: [...]
        scope_loc_estimate: <integer>
        links_to: [...]
```

The writer writes **nothing** for the page when returning `split_request`.

**3. Decline to rewrite** — on a `fail_soft` re-dispatch, the writer judged the
verifier wrong:

```yaml
skipped: true
skip_reason: "<why the existing page is correct and the verifier's issue is not>"
```

Resolution of `skipped: true` is defined in `../init.md` Phase 3d
(re-verify once; still-not-`pass` → `fail_hard`; record the reason in
`_failures.md`). `cross_section_ripples` is advisory — the orchestrator uses it
to prioritize sibling-page verification on the next run; the writer never edits
sibling pages itself.

---

## INVARIANTS

A valid `wiki/.internal/plan.yaml` must satisfy all of:

1. Every `sections[].path` starts with `wiki/<TRACK>/`, and every
   `pages[].path` starts with `wiki/<TRACK>/` and ends with `.md`, where
   `<TRACK>` is one of `{AI, TECHNICAL, PRODUCT}`. The folder names are
   literally uppercase — `AI`, `TECHNICAL`, `PRODUCT`, never lowercase (casing
   invariant). Technical pages nest as `wiki/TECHNICAL/<repo>/…`. Pages outside
   `wiki/<TRACK>/` are not part of the auto-gen plan and must not appear.
2. Every page's `section` refers to an existing section id.
3. Every section's `parent` refers to an existing section id or `null`.
4. Every id in any `links_to` list refers to an existing page or section.
5. No two pages share the same `path`.
6. No section with `has_overview: true` has a `path` ending in `.md`.
7. No section with `has_overview: false` has child pages (it's a leaf —
   it should be a page, not a section).
8. For every section with `scope_loc_estimate ≥ 1,500`,
   `has_overview: true` (per the scope-to-depth table).
9. For every page with `section_parity: strict`, a counterpart page
   exists in each sibling section where parity is meaningful.
10. `meta.tracks` is a non-empty subset of `{ai, technical, product}`. Every
    `owner_agent` (sections and pages) is one of the enabled `meta.tracks`, and
    every enabled track has at least one section. `scope_loc_estimate` and the
    scope-to-depth invariant (#8) apply to `technical` and `ai` sections; a
    `product` section is feature-sized, not LOC-sized, and is exempt from #8.
11. `meta.schema_version` matches the version this file documents (`1.4`).

The orchestrator validates these in Phase 2 before writing the plan and
in Quality Gates at the end of Phase 3e.

---

## EVOLUTION

When the schema changes in a breaking way, bump `meta.schema_version` and
update this file. Non-breaking additions (new optional fields) do not
require a version bump.

The plan is intentionally minimal. Resist adding fields that could be
computed from source code or filesystem state at run time — the plan is a
coordination spec, not a cache.
