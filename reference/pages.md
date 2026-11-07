# Map content and state

Only `index.md` and `.state.json` are required. Optional pages live wherever the index makes them
easy to retrieve: `areas/<name>.md`, `catalog.md`, `contracts.md`, `invariants.md`, for example.
No mandatory spine, directory index, glossary, product track or page per file. An index-only map
can answer a small project's questions without empty companion pages.

## Writing useful context

Every managed page starts with:

`<!-- wiki-system: generated from code; refresh with /wiki-system update -->`

The index identifies the repos, links every managed page, explains important connections and points
to authoritative commands/docs. Link owner policy and LINKS.md separately when present. Provide
capability and change-entry navigation in the index or a separate page when useful.

For an area, explain its purpose, entry files/symbols, main cross-file flow, non-obvious constraints,
and where a common change begins. Omit empty sections. Read actual producers and consumers for
boundary claims; a file name or comment is not sufficient evidence. Include admin/background flows
when relevant, and identify prototypes or uncertain behavior honestly.

Use workspace-relative paths in backticks; append `/` for directories. Markdown links are relative
to the containing page. Quote paths containing spaces with angle brackets in links. Cite symbols
agents can search, not brittle line anchors. Keep exact schemas, enum lists, configuration values
and inventories in machine sources; point to them. State a literal only when it is itself a useful
cross-system contract and give its source. Don't make a generated map the authority for policy.

Aim for roughly 600 words or fewer per area; size warnings invite trimming or a useful split,
not automatic failure. Avoid splitting one coherent flow into fragments merely to meet a budget.
Keep startup instructions much smaller: links to relevant documentation, not an imported manual.

## Ownership

`managed_pages` declares generated ownership; a location alone does not. Never add an existing
handwritten file to that list to make a validator accept it. Inventory existing files before
claiming ownership. Preserve unmarked files byte-for-byte and link them when useful.

Preserve complete `<!-- keep -->` … `<!-- /keep -->` blocks and legacy
`<!-- AUTOREGEN_SKIP_BEGIN -->` … `<!-- AUTOREGEN_SKIP_END -->` blocks exactly. Never trim them
for size warnings or silently relocate/drop their parent page. Snapshot finalization checks these
blocks and existing unowned files. A missing source repo's pages likewise retain their last known
content; mark the run and dependent claims partial rather than writing guesses.

## State format

New state uses schema version **3**, independent of the library VERSION. Minimal valid planning
state for a single Git repo (baseline fields are filled only by snapshot finalization):

```json
{
  "skill": "wiki-system",
  "version": 3,
  "repos": {".": {"sha": null}},
  "managed_pages": ["index.md"],
  "areas": [],
  "unmapped_ok": []
}
```

For sibling repos, replace `.` with each immediate repo name. Do not mix `.` with siblings.
When areas have separate ownership, add records such as:

```json
{
  "id": "payments",
  "title": "Payments",
  "page": "areas/payments.md",
  "paths": ["api/payments/**"],
  "watch": ["web/src/checkout.ts", "api/infra/payments.tf"]
}
```

Include each area page in `managed_pages`. `paths` is ownership; `watch` is relevant dependency
change evidence. Both use workspace-relative Python fnmatch globs (`*` crosses `/`). Cited paths
also select referencing pages. Explicit watches/citations include ignored first-party dependencies
when safe; broad ownership does not override Git ignore rules or prove all code was understood. Paths can
include tests, generated contracts or infrastructure not counted by the LOC inventory.

Optional fields:

- `excluded_repos`: immediate sibling repo names intentionally outside this map.
- `project_rules`: existing workspace-relative Markdown policy outside generated AGENTS; never invent it.
- `unmapped_ok`: objects with `glob` and a concrete `why`; omit irrelevant/generated content deliberately.
- `review_summary`: last actual semantic review, not a receipt for every file. Example:

```json
{
  "pages": ["index.md", "areas/payments.md"],
  "ordinary_area": "payments",
  "method": "independent",
  "limitations": ["Provider behavior checked against local adapter; live provider not exercised."]
}
```

Use `ordinary_area: null` for an index-only map, and `method: "self"` for self-review. Retain unresolved
limitations until evidence resolves them. A source-only no-op keeps this summary; it does not imply
another semantic review. The run report names source paths/sections actually checked when useful.

Snapshot helpers own per-repo `sha`, `dirty`, `dirty_files`, `dirty_hashes`, `fingerprint`, plus
`generated`, `generator_version`, `snapshot_status` and `unavailable_repos`. Do not fabricate them or
replace old baselines manually. Current/partial describes snapshot availability, not semantic completeness.
Use explicit `--root` so nested/external docs locations don't change workspace interpretation.
