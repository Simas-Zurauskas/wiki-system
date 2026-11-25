# Refresh the map

Follow SKILL.md preflight. `update` and `recheck diff` are incremental; `update --full` and
`recheck` revisit every documented area and its relevant source flows. Neither means an exhaustive
claim-by-claim audit. If an older map has unsupported state, use [init](init.md) to write a fresh map
at the same destination within the recorded/requested repo scope. Do not introduce a migration phase,
compatibility pages or archives. A usable current map stays incremental regardless of skill version.

## Select affected work

Run `python3 <skill>/scripts/changed.py <WIKI>/AGENTS --root <workspace> --json`.
Read changed paths, touched areas, referenced pages, index hints, unmapped files, newly discovered
repos and fallback/unavailability reasons. Zero touched areas does not imply no work. Include
unresolved review limitations when they can now be checked, even when source is unchanged.
An explicit report of poor navigation is actionable evidence even with unchanged source: reproduce
the affected lookup, then repair supported gaps within the requested scope.

- Follow ownership, watches and cited-path references; trace consequential changes into callers
  and consumers even when no direct file citation selects them.
- Inspect unknown/config/test/asset changes for actual documentation impact; do not silently discard
  them because their extensions are unfamiliar. Generated/vendor/cache and secret exclusions remain.
- Reconcile repo additions/removals with project intent. An absent checkout is not authorization
  to drop its state or pages. Retain its snapshot and label dependent claims unverified.
- For an unusable baseline, reread the affected repo's map scope. A new skill/model version alone
  is advisory, not a reason to broaden an incremental request into full generation.
- Full refresh includes all managed areas, index sections and meaningful boundaries. It does not
  force per-file prose or the creation of optional pages.

## Refresh and finalize

1. If the task prompt is missing, install it using init's install-once procedure **before capture**.
   Existing prompts never change. Save pre-edit map/state in scratch. Update page ownership only as needed while preserving old
   repo baselines. Capture with snapshot.py as in [init](init.md) before editing prose.
2. Read affected source and selected existing pages. Keep true prose unchanged. Update only the
   affected facts/links; remove obsolete generated claims when their removal is established. Preserve
   unowned material and all keep/AUTOREGEN_SKIP blocks. A source change may need no prose change.
3. Use the same economical writer policy and structural check as init. Review changed consequential
   contracts/constraints and rotate an ordinary area using the [review brief](specialists/verifier.md).
   Retain unresolved limitations, clearing them only with evidence. Record the actual `review_summary`.
4. Finalize against the captured snapshot, then run public check. If source moved, review the affected
   changes and repeat; do not advance state to make the map look current. For unavailable repos,
   only available snapshots advance and the result remains partial.

A genuine no-op requires no relevant source/topology changes, no unresolved actionable review work,
and passing structural checks. Capture/finalize may confirm source stability without rewriting pages;
retain the previous semantic review summary and do not claim a new factual review. Report the no-op.

## Report

Summarize changed/unchanged pages, structural/freshness status, actual semantic review and omissions.
A current source snapshot is not exhaustive semantic certification. If blocked/partial, name the
unavailable sources or failed checks and preserve their older baselines. No source edits, entry-file
regeneration, commits or remote operations occur as a side effect of update.
