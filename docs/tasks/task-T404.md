# Task T404 — Extend the release gate to block on version-consistency failure

**ID:** T404
**Owner:** release-manager
**Status:** pending
**Priority:** P0
**Depends on:** T400 (needs `scripts/check-version-consistency.py` to exist)
**Created:** 2026-08-12
**Completed:** —
**Based on:** docs/plans/plan-035-roadmap-v7-ground-up.md (Phase 0, §2.4)

This brief is self-contained. Read T400's brief (`docs/tasks/task-T400.md`) for the exact contract
of the script you're wiring in, but you don't need to re-derive it.

## Objective
Extend `scripts/verify-release-docs.py` so it also runs `scripts/check-version-consistency.py`
(added by T400) and fails the release gate if that check fails — i.e. a `vX.Y.Z` tag cannot be cut
while any non-archived doc still references a stale release. This is what makes Gate G0 durable:
without this wiring, T400's script is just a script anyone could ignore; with it, doc-version
drift becomes a release blocker, not a review-time nice-to-have (this directly closes the "Doc
drift returns after Phase 0" risk named in plan-035 §2.6).

## Inputs
- `scripts/verify-release-docs.py` (full file — read it entirely; you are extending `main()`, not
  rewriting the file)
- `scripts/check-version-consistency.py` (T400's output — by the time you execute, this should
  exist on the shared branch `feature/T400-phase0-ground-truth-v6.11.0`; if it doesn't yet exist,
  this task is blocked on T400, see Depends on above)
- `CONTRIBUTING.md`'s `## Releasing` / `### Cutting a release` sections — describe the current
  release procedure and where `verify-release-docs.py` is invoked from; your change must be
  reflected there too if the procedure text would otherwise become inaccurate.
- `.gitlab-ci.yml` — check whether `verify-release-docs.py` is invoked from a CI job; if the
  version-consistency check should also run as a standalone CI job (not only nested inside the
  release-docs gate), note this as a finding, but the primary integration point is inside
  `verify-release-docs.py` itself per T404's literal wording ("extend the release gate").

## Expected outputs
- `scripts/verify-release-docs.py` — extended so that running it (`python3 scripts/
  verify-release-docs.py --tag vX.Y.Z`) also invokes `scripts/check-version-consistency.py` (as a
  subprocess call or an imported function call — your choice, but prefer a subprocess call
  mirroring how the rest of this script already treats file/link checks as independent units, to
  keep the two scripts decoupled and each independently runnable) and includes any failure it
  reports in the same `errors` list / same non-zero exit / same `release-docs-verify: ...`-prefixed
  error line format the rest of the script already uses, for consistency.
- `CONTRIBUTING.md` — updated if the release-cutting procedure text needs to mention the new
  check (only if it would otherwise be inaccurate/incomplete; don't pad the doc if the existing
  wording already generically covers "run verify-release-docs.py before tagging").

## Acceptance criteria
1. `python3 scripts/verify-release-docs.py --tag <current-tag>` fails (non-zero exit, with a
   `release-docs-verify: ...`-prefixed message identifying the version-consistency failure) when
   `scripts/check-version-consistency.py` would itself fail on the current tree.
2. `python3 scripts/verify-release-docs.py --tag <current-tag>` still passes when the tree is
   clean (i.e. your addition introduces no false positive on a passing tree).
3. All of `verify-release-docs.py`'s pre-existing checks (required files, marker text, section
   requirements, link-checking) remain unmodified and still function exactly as before — this is
   an addition, not a rewrite. Confirm by re-running the script against a known-good tag before
   and after your change and diffing the output for anything unexpected.
4. If `scripts/check-version-consistency.py` itself is missing or fails to execute (e.g. a
   different repo state where T400 hasn't landed), `verify-release-docs.py` should fail loudly
   with a clear message, not silently skip the check.
5. `CONTRIBUTING.md`'s release procedure text remains accurate after your change (no stale
   description of what `verify-release-docs.py` checks).

## Blocker protocol
- If T400's script isn't present on the branch when you start — `type: dependency`, `severity:
  major` — this task is explicitly blocked on T400; report and wait rather than stubbing out a
  placeholder check.
- If wiring the check in as a subprocess call would require a Python version/import mismatch or
  other environment issue — `type: technical`, `severity: minor` — report the specific error.

## Git workflow
Same shared branch as T400–T403: `feature/T400-phase0-ground-truth-v6.11.0`. You have Bash access
(per your agent definition) — you may commit your own change directly to this branch, but **do
not push** and **do not open a merge request** — the orchestrator owns the branch's push/MR
lifecycle; T406 performs the final validation gate and merge for the whole batch. Commit with a
Conventional Commit message, e.g.:
```
feat(release): block release gate on version-consistency failure

scripts/verify-release-docs.py now also runs T400's
check-version-consistency.py and fails the release gate if it does,
so doc-version drift becomes a release blocker rather than a
review-time nice-to-have. Closes the "doc drift returns after Phase
0" risk from plan-035 Sec 2.6.

Refs T404
```

## Constraints
- Token budget: ≤15k tokens.
- File ownership: `scripts/verify-release-docs.py`, `CONTRIBUTING.md` (release-procedure text
  only, and only if genuinely needed for accuracy).
- Do not modify `scripts/check-version-consistency.py` itself — that's T400's file; if you find a
  defect in it, report as a blocker rather than silently patching someone else's task's output.
