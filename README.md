# Wiki System

A Claude Code skill that generates and maintains structured codebase documentation. You run it in a **workspace** — a folder holding the project's code repos beside its docs. It reads the repos' source, plans a multi-page wiki, dispatches writer and verifier sub-agents, and produces a per-project `wiki-{project}/` docs repo — every claim checked against the source it documents.

This README explains how the system works and why it's built this way. `SKILL.md` is the operational entry point (modes, routing, pre-flight); read that to run it.

---

## What it solves

- **Docs drift from code.** Hand-written docs go stale; auto-generated docs (Swagger, JSDoc) only cover API shape, not behavior, integration, or gotchas. This system writes natural-language docs from source and re-verifies them against source on every recheck.
- **Different readers need different docs.** AI agents want self-contained, source-anchored invariants/contracts/runbooks loaded on demand; engineers want file paths and function names; product people want flows and rules in plain language. The pipeline produces up to three tracks — `AGENTS` (always on), plus opt-in `PRODUCT` and `TECHNICAL` — from the same source, with the same accuracy guarantee.

It does **not** produce ADRs, design docs, tutorials, or onboarding guides. Durable hand-written narrative — plans, RFCs, research — lives in user-owned docs-root folders (task workspaces, research folders), outside the pipeline.

---

## Core ideas

1. **Source code is the source of truth.** Every auto-generated claim must be verifiable against source at HEAD. Writers read source; verifiers re-read it. Nothing is trusted because "the model knows" or "we said so last time."
2. **One generated home.** `wiki/` is auto-generated and authoritative for "what the system does" — every page written from source and re-verified against it. Hand-written intent (plans, RFCs, research) lives in user-owned docs-root folders, outside the pipeline. Small in-place hand-edits survive re-runs via `AUTOREGEN_SKIP` zones.
3. **The plan is the coordination spec.** `wiki/.internal/plan.yaml` defines every page, its source files, its writer, and its links. The orchestrator writes it once; writers and verifiers consume it. A run interrupted mid-flight resumes from the plan plus on-disk state.
4. **The verifier is the only quality gate.** No human-confirm step. The verifier's verdict decides a page's fate: accept, auto-fix, or flag for human review.
5. **Verify cheaply, regenerate only what fails.** A recheck verifies pages (cheap, read-only) and regenerates only those that drift. With `git diff`, pages whose source is unchanged are skipped entirely.

---

## The wiki shape

```
wiki/
├── index.md                ← orchestrator-generated (finalize phase) — human table of contents
│
├── .internal/                 ← skill artifacts: plan, verification, traces (COMMITTED to git)
│   ├── plan.yaml              ← coordination spec
│   ├── verification/          ← per-page verifier reports + _failures.md
│   └── trace/decisions.md     ← per-run decisions log
│
├── AGENTS/                        ← agents track (ALWAYS ON) — agent-optimized, standalone-complete
│   ├── index.md               ← navigable machine index (the agent's front door)
│   ├── invariants.md  glossary.md
│   └── contracts/  runbooks/  map/  reference/
├── TECHNICAL/                 ← technical track (opt-in) — one folder per repo (ALWAYS nested here)
│   ├── index.md
│   └── <repo>/                ← one folder per repo, even for a single-repo project
│       ├── index.md
│       └── ...
└── PRODUCT/                   ← product track (on when the project has a product surface) — feature-scoped
```

Only enabled tracks exist on disk — routing and `wiki/index.md` list only tracks present. `wiki/.internal/` **is committed to git** (it is the coordination state, not a scratch cache). The folder is really `wiki-{project}/` — its own git repo, unique per project, sitting in the workspace beside the code repos (`wiki/` above is shorthand for it; commands resolve the real folder by its `.internal/plan.yaml` marker).

| Surface | Produced by | Verified? | Mutability |
| --- | --- | --- | --- |
| `wiki/index.md` | Orchestrator (finalize) | No | Auto-rewritten; hand-edit zones survive |
| `wiki/{AGENTS,TECHNICAL,PRODUCT}/**` | agents / technical / product writer | Yes (claim-by-claim) | Auto-rewritten; hand-edit zones survive |
| `CLAUDE.md` | `claude` mode only | No | Individual per dev, **not committed**; machine-generated + preserved `AUTOREGEN_SKIP` human zone |

`wiki/index.md` is derived in the finalize phase from the completed reference tree — it is not a writer page and does not appear in `plan.yaml`. `CLAUDE.md` is written **only** by the `claude` mode; `init`/`recheck` just suggest running it. Hand-edit zones (`<!-- AUTOREGEN_SKIP_BEGIN/END -->`) let projects keep hand-written sections through re-runs.

---

## The pipeline

Two flows: a full **bootstrap** (`init`) and an incremental **recheck**. Recheck is the steady state — verify what exists, regenerate only what drifted:

```mermaid
flowchart TD
    Start[Recheck run] --> Cov[Coverage-gap scan:<br/>find undocumented source]
    Cov --> Verify[For each page:<br/>verify against scope_files]
    Verify --> Pass{Verdict?}
    Pass -->|pass| Skip[Leave page alone]
    Pass -->|fail_soft| Regen[Regenerate page]
    Pass -->|fail_hard| Tier2{Tier-2<br/>strong verifier}
    Regen --> Reverify[Re-verify]
    Reverify -->|pass| Done[Page updated]
    Reverify -->|still failing| Tier2
    Tier2 -->|pass| Done
    Tier2 -->|still failing| Gate[End-of-run user gate:<br/>regen / patch / shrink /<br/>accept / delete / defer]
    Gate --> Done
```

A full generation (`init`, or a forced full rebuild) runs up to six sub-phases (3d.5 fires only when Phase 3d produced any `fail_hard` pages):

| Phase | Purpose |
| --- | --- |
| 1. Scan | One scan sub-agent per repo (parallel); each returns a condensed summary. The orchestrator synthesizes a cross-repo integration map — raw source never enters its context. |
| 2. Plan | Write `plan.yaml` per `spec/plan-schema.md`. |
| 3a. Stub | Create `*TODO*` stubs for every planned page so cross-links resolve immediately. |
| 3b–c. Write | Dispatch writer sub-agents in parallel, one per section. |
| 3d. Verify | Dispatch verifier sub-agents in parallel. Auto-fix `fail_soft`; escalate via tier-2 strong verifier; queue surviving `fail_hard` pages for the user gate. |
| 3d.5. User gate | If any pages reached `fail_hard`, halt for a batched user-resolution checkpoint (regen / patch / shrink / accept / delete / defer). Skipped if the queue is empty. |
| 3e. Finalize | Generate `index.md`; run link / parity / numeric-consistency checks. Preserve hand-edit zones. |

A recheck does not re-plan unless `plan.yaml` is missing or stale — it only runs the steps that apply to drifted or failing pages.

---

## Commands

Three commands. Ground truth for verification is always the **source code**.

| Command | What it does |
| --- | --- |
| `/wiki-system init` | Bootstrap the local wiki from scratch: scan → plan → stub → write → verify → finalize. |
| `/wiki-system recheck` | Audit the local wiki against current code: coverage-gap scan, verify-first, regenerate drift. Does not re-plan. |
| `/wiki-system claude` | Create/update a lean (≤200-line) `CLAUDE.md` routing agents at `wiki/AGENTS`. The only command that writes it. |

Mental model: `init`/`recheck` create and audit the local wiki; `claude` regenerates `CLAUDE.md`.

---

## The prompt files

Each is project-agnostic; per-project configuration lives in `init.md`'s CONFIGURATION block.

| File | Role |
| --- | --- |
| `init.md` | Bootstrap orchestrator: scans, plans, dispatches writers and verifiers, finalizes. |
| `recheck.md` | Recheck orchestrator: audits the existing wiki against source. |
| `claude-md.md` | `CLAUDE.md` orchestrator (`claude`). |
| `specialists/agents.md` | agents-track writer (always-on track) — agent-optimized, code-grounded: self-contained, atomic source-anchored claims, invariants + contracts + runbooks + flow map + concise per-area reference + a machine index. |
| `specialists/technical.md` | Technical writer — reference pages with file paths, function names, line citations. |
| `specialists/product.md` | Product writer — flows and business rules in plain language, zero code references. |
| `specialists/verifier.md` | Verifier — reads a draft + its scope files, emits a per-claim YAML report. Read-only. Modes: `agents` / `technical` / `product`. |
| `spec/plan-schema.md` | Schema reference for `wiki/.internal/plan.yaml`. |

**Why writer and verifier are split.** A writer self-checking is an unreliable check — its incentive is to ship. A separate verifier prompt confronts the prose with source. The independence is prompt-level, not model-level (usually the same underlying model), so the real safeguard is re-reading the source; the prompt split is a secondary one.

**Why the writer tracks are split.** Audience and vocabulary control. The `agents` track is written for an agent retrieving fragments on demand (self-contained, atomic, source-anchored, task/contract-oriented); technical pages are human narrative that cite `file:line`; product pages may not mention any code identifier. Three specialists with distinct rules produce cleaner, non-overlapping output than one prompt trying to do all three — and overlap is actively harmful (duplicated/near-duplicate content is retrieved as conflicting "distractor" context), so the `agents` track links to the others rather than restating them.

---

## Key techniques

- **Plan-driven coordination.** Writers consume a fixed plan instead of self-organizing, so the same plan + same source yields the same structure. A writer that finds a page's scope too large returns a `split_request`; the orchestrator patches the plan and re-dispatches rather than letting writers freelance structure.
- **Stub-out before writing.** `*TODO*` stubs for every page are created up front, so cross-links resolve from the start, the folder structure is materialized on disk, and a crashed run can resume by re-dispatching only the remaining stubs.
- **Verify-first, not regen-first.** On recheck, each page is verified against existing docs; only drift triggers regeneration. Verification is far cheaper than writing, so a refactor that didn't change behavior usually verifies `pass` and is skipped.
- **Source-aware re-runs.** `plan.yaml` records each page's `scope_files`. A `git diff` scoped to those paths marks unchanged pages `state: unchanged` and skips them — a frontend-only change never re-touches the API pages.
- **Numeric-consistency gate.** After writes, every "`<number> <noun>`" pair is surfaced across the wiki and mismatches flagged (one page says "33 endpoints," its sibling says "32"). Writers reconcile by re-counting from source.
- **Hand-edit zones.** `<!-- AUTOREGEN_SKIP_BEGIN/END -->` markers fence hand-written content that writers preserve verbatim and verifiers ignore. Opt-in and rarely needed.
- **Generated-header on every page.** Every generated `wiki/*.md` (including `wiki/index.md`) opens with a one-line header marking it machine-generated and pointing at `recheck`. Writers and the finalize/regen phases emit it; the verifier ignores it (it is not a claim, so it is never counted or flagged) — the same treatment as an `AUTOREGEN_SKIP` block.

### Verdicts

The verifier emits one of three verdicts, driven by per-claim severity (`consideration` < `improvement` < `critical`):

| Verdict | Trigger | Action |
| --- | --- | --- |
| `pass` | 0 critical and 0 improvement (consideration tolerated) | Accept as-is. |
| `fail_soft` | 1–3 improvement, 0 critical | Auto-fix once, then re-verify. |
| `fail_hard` | 4+ improvement, or any critical | Tier-2 strong-verifier rescue attempt (if configured); surviving failures enter the end-of-run user resolution gate. Run does not complete until every queued page is triaged. |

Honest calibration matters: inflated severity blocks legitimate updates; deflated severity lets real errors through. The verifier prompt is explicit about this.

---

## Failure modes

| Failure mode | Mitigation |
| --- | --- |
| Verifier passes a real error (it's an LLM) | Cross-page consistency gates catch some leakage; the suspect-pass check (`resolved: 0` on a large page → re-verify) catches shallow audits; audit by hand periodically. |
| Verifier shares the writer's blind spots (same base model) | Re-reading source carries the weight, not the prompt split. For high-stakes pages, run a second verifier by hand. |
| `fail_hard` accumulating silently | Eliminated by design: the run does not complete until every `fail_hard` page from this run has a recorded resolution (regen / patch / shrink / accept / delete / defer). `defer` is an explicit dated choice surfaced again on the next run, not a silent skip. |
| Regen produces only rephrasing | Verify-first skips pages that didn't change. If unchanged pages keep getting rewritten, tighten `state: unchanged`. |
| Prompt drift after a model release | Version the prompts (`VERSION`); force a full `init` and review on a version bump. |
| Cost runaway on a large recheck | Verify-first keeps it down; `verify_breadth: by_complexity` bounds it further. |

The principle: **observable rot beats silent rot.** The system makes problems visible rather than pretending they can't happen.

---

## Adopting it in a new project

1. Copy the skill files (`SKILL.md`, `VERSION`, the orchestrator prompts, `specialists/`, `spec/`) into the project's `.claude/skills/wiki-system/`.
2. Set up the **workspace**: a folder with the project's code repos cloned as siblings. The skill discovers and confirms the repos at `init` — no config file to edit.
3. Run `/wiki-system init` once (it creates the `wiki-{project}/` docs repo and records the repo set), then `/wiki-system claude` to generate your `CLAUDE.md`.
4. Wrap any permanent hand-edits in `<!-- AUTOREGEN_SKIP_BEGIN/END -->` so future runs preserve them.

The `wiki-{project}/` folder is **its own git repo** (all of it, including `.internal/`, committed there) — the one shared artifact; `CLAUDE.md`, `.claude/`, and `.mcp.json` are individual per dev and not committed. A developer who lacks some repos can still `recheck` the parts they have — **absent repos are skipped and their pages kept as source of truth** (partial access). Re-run `/wiki-system recheck` periodically to keep the wiki aligned with the code.

---

## File map

| File | Role |
| --- | --- |
| `README.md` | This file — system explainer. |
| `SKILL.md` | Skill entry point: pre-flight, mode routing. |
| `VERSION` | Single integer; bump on material prompt changes. |
| `init.md` | Bootstrap orchestrator. |
| `recheck.md` | Recheck orchestrator. |
| `claude-md.md` | `CLAUDE.md` orchestrator (`claude`). |
| `check-update.sh` | Mechanical self-update check run by pre-flight step 0. |
| `specialists/agents.md`, `technical.md`, `product.md`, `verifier.md` | Writer (one per track) and verifier sub-agent prompts. |
| `spec/plan-schema.md` | Schema for `wiki/.internal/plan.yaml`. |

The per-project artifacts (`wiki/`, `wiki/.internal/*`) are documented at their point of use in the orchestrator prompts.
