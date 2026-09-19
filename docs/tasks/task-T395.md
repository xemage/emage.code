# Task T395 — Sync `main` with `develop` for v6.10.0 (release/v6.10.0 → main)

**ID:** T395
**Owner:** release-manager (executed jointly with orchestrator per T367/T359/T351/T348 precedent —
ledger `Owner` column uses the single validated slug `release-manager`)
**Status:** done
**Priority:** P1
**Depends on:** T394
**Created:** 2026-08-10
**Completed:** 2026-08-10
**Based on:** CONTRIBUTING.md § "Cutting a release" step 6 (PUT-first sequence); docs/tasks/task-T367.md,
task-T359.md, task-T351.md, task-T348.md (precedent)

## Objective
Perform the standing GitFlow `release/vX.Y.Z → main` sync for v6.10.0, following
`CONTRIBUTING.md` § "Cutting a release" step 6 exactly (the PUT-first sequence, 4/4 successful as
of T367).

## Context
- Phase: Release (main-sync)
- Exact sequence (per CONTRIBUTING.md, verified current before use):
  1. `glab api -X PUT projects/:id/merge_requests/:iid -f squash=false` — confirm response shows
     `squash: false`.
  2. `glab api -X PUT projects/:id/merge_requests/:iid/merge -f should_remove_source_branch=true`
  3. `python3 scripts/verify-main-sync-merge.py <mr_iid>` — run immediately regardless of step 1's
     apparent success.
- Pre-flight: confirm via `git log origin/develop..origin/main` whether `main` has any independent
  commits since the last sync (expected: none, per the T351/T359/T367 pattern).

## Inputs
- `docs/tasks/task-T367.md` — most recent prior sync, full evidence trail
- `CONTRIBUTING.md` § "Cutting a release" step 6
- `scripts/verify-main-sync-merge.py`

## Constraints
- Use the PUT-first sequence as the primary attempt.
- If a conflict appears, diagnose phantom vs. real via content diff before resolving; escalate to
  user if it looks like a genuine (non-phantom) conflict.
- Token budget: ≤ 60k.

## Expected Outputs
- `release/v6.10.0` branched from `origin/develop`'s tip, pushed
- MR `release/v6.10.0 → main` opened and merged via the PUT-first sequence
- `scripts/verify-main-sync-merge.py` result recorded
- Content verified identical between `origin/main` and `origin/develop` post-merge
- Post-merge `main` pipeline green
- Local `develop`/`main`/tags synchronized with origin

## Acceptance Criteria
1. `release/v6.10.0` branched from `origin/develop` tip, pushed to origin.
2. MR `release/v6.10.0 → main` opened.
3. Any conflict correctly diagnosed as phantom or real before resolution (escalate if real).
4. Merged via the PUT-first sequence.
5. `scripts/verify-main-sync-merge.py` result recorded — explicit PASS/FAIL.
6. `git diff origin/develop origin/main` empty after merge (and any recovery).
7. Post-merge `main` pipeline green.
8. No destructive git operations used at any point.
9. Local checkout synchronized with origin after everything lands.

## Blocker Protocol
Report blockers as: type + severity + proposed mitigation. Max 2 retries. A real (non-phantom)
conflict on `main` is a `critical` blocker requiring escalation.

## Execution notes

**Executed by:** orchestrator, release-manager, 2026-08-10.

**Pre-flight:** `git log origin/develop..origin/main` confirmed `main`'s tip (`6dbc29d`, T367's
merge) had zero independent commits since the last sync — everything listed was its own lineage.

**Sync — fifth consecutive clean sync since T348's ancestry-restore fix:** `release/v6.10.0`
branched from `origin/develop`'s post-release-docs tip (`a09c242`), pushed. MR !177 opened
(`release/v6.10.0 → main`). GitLab reported `has_conflicts: false` immediately, matching the
T351/T359/T367 clean-sync pattern. MR CI green before merge.

**PUT-first sequence (CONTRIBUTING.md § "Cutting a release" step 6):**
```
$ glab api -X PUT .../merge_requests/177 -f squash=false
squash: False
$ glab api -X PUT .../merge_requests/177/merge -f should_remove_source_branch=true
state: merged, merge_commit_sha: 43fce57794ae8c511ac4f8f9272b92008a656697,
squash: False, squash_commit_sha: None
$ python3 scripts/verify-main-sync-merge.py 177
verify-main-sync-merge: MR !177 PASS — squash=false, squash_commit_sha=null, ...
```
**Result: PASS. T349's fix is now 5/5** (MR !126 recovery, MR !134/!151/!156/!177 as standard
procedure).

**Independent re-verification via git plumbing:**
```
$ git log origin/main -1 --parents
43fce57 6dbc29d a09c242   Merge branch 'release/v6.10.0' into 'main'
```
`a09c242` is `origin/develop`'s own real tip — genuine 2-parent merge, not a squash substitute.
`git merge-base --is-ancestor origin/develop origin/main` → exit 0. `git diff origin/main
origin/develop` → empty (0 lines).

**Pipeline, final sync:** `main`'s post-merge pipeline (`43fce577`) watched to completion:
**success**. Local `develop`/`main`/tags and stale session branches synchronized/cleaned up in
Phase 3 (see checkpoint-release-v6.10.0.md and the final orchestrator report).

**Significance:** Five consecutive successful uses of the PUT-first fix (MR !126, !134, !151, !156,
!177), and four consecutive conflict-free syncs (T351, T359, T367, this task) since T348's
ancestry-restore commit — the pattern continues to hold reliably over time.
