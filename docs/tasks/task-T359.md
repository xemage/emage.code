# Task T359 — Sync `main` with `develop` for v6.8.0 (release/v6.8.0 → main)

**ID:** T359
**Owner:** orchestrator, release-manager
**Status:** done
**Priority:** P1
**Depends on:** T358
**Created:** 2026-08-09
**Based on:** `.claude/rules/git-workflow.md`, `docs/tasks/task-T331.md`, `docs/tasks/task-T339.md`,
`docs/tasks/task-T348.md`, `docs/tasks/task-T351.md` (PUT-first sequence, now 2/2 successful:
MR !126, MR !134)

## Objective
Perform the standing GitFlow `release/vX.Y.Z → main` sync for v6.8.0, following `CONTRIBUTING.md`
§ "Cutting a release" step 6 exactly (the PUT-first sequence, now the documented standard procedure,
2/2 successful so far).

## Context
- Phase: Release (main-sync)
- Exact sequence:
  1. `glab api -X PUT projects/:id/merge_requests/:iid -f squash=false` — confirm response shows
     `squash: false` before proceeding
  2. `glab api -X PUT projects/:id/merge_requests/:iid/merge -f should_remove_source_branch=true`
  3. `python3 scripts/verify-main-sync-merge.py <mr_iid>` — run immediately regardless of whether
     step 1 worked
- **If `verify-main-sync-merge.py` reports FAIL despite the PUT-first sequence**, that's valuable
  data (the fix stopped generalizing) — follow `CONTRIBUTING.md` § "Recovery procedure" and report
  the outcome plainly either way. Not a task failure.
- Pre-flight: confirm via `git log origin/develop..origin/main` whether `main` has any independent
  commits since T351 (expected: none) — any GitLab-reported conflict is then almost certainly the
  phantom-ancestry pattern (T340), safe to resolve by taking `develop`'s side after confirming via
  content diff, not commit-SHA ancestry.

## Inputs
- `docs/tasks/task-T351.md` — most recent prior sync, full evidence trail
- `CONTRIBUTING.md` § "Cutting a release" step 6 — the procedure to follow exactly
- `scripts/verify-main-sync-merge.py` — the verification tool

## Constraints
- Use the PUT-first sequence as the primary attempt.
- If a conflict appears, diagnose phantom vs. real via content diff before resolving.
- Do not touch `develop` as part of this sync itself (only this task's own ledger closeout touches
  it, via a separate branch+MR per T342's rule).
- Token budget: ≤ 60k.

## Expected Outputs
- `release/v6.8.0` branched from `origin/develop`'s tip, pushed
- MR `release/v6.8.0 → main` opened
- Conflict (if any) diagnosed correctly (phantom vs real) before resolving
- Merged using the PUT-first sequence
- `python3 scripts/verify-main-sync-merge.py <mr_iid>` result recorded
- Content verified identical between `origin/main` and `origin/develop` post-merge (`git diff`)
- Post-merge `main` pipeline green
- Task brief updated with an `## Outcome` section

## Acceptance Criteria
- [ ] `release/v6.8.0` branched from `origin/develop` tip, pushed to origin
- [ ] MR `release/v6.8.0 → main` opened
- [ ] Any conflict correctly diagnosed as phantom or real before resolution
- [ ] Merged via the PUT-first sequence (not the old approach)
- [ ] `scripts/verify-main-sync-merge.py` result recorded, explicit PASS/FAIL verdict
- [ ] `git diff origin/develop origin/main` empty after merge and any recovery
- [ ] Post-merge `main` pipeline green
- [ ] No destructive git operations used at any point
- [ ] Local checkout (`develop`, `main`, tags) synchronized with origin after everything lands

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries. A real (non-phantom) conflict on
`main` is a `critical` blocker requiring escalation, per the T331 precedent.

## Outcome (2026-08-09)

Executed directly by the orchestrator (same judgment call as T348/T351, given real-time conflict
diagnosis needs).

### Pre-flight
`git log origin/develop..origin/main` confirmed `main`'s tip (`9c4f82a`, T351's merge) has zero
independent commits since the last sync — everything listed is its own lineage.

### Sync — no conflict, second time in a row
`release/v6.8.0` branched from `origin/develop`, pushed. MR !151 opened (`release/v6.8.0 → main`).
GitLab reported `has_conflicts: false` immediately, matching T351's result — the second consecutive
clean sync since T348's ancestry-restore fix, further evidence it's holding up over time.

### PUT-first sequence
```
$ glab api -X PUT projects/.../merge_requests/151 -f squash=false
squash: False
$ glab api -X PUT projects/.../merge_requests/151/merge -f should_remove_source_branch=true
state: merged, merge_commit_sha: f005c0f6f9fcf5ac95a7faf1898e1dec9db69083,
squash: False, squash_commit_sha: None
$ python3 scripts/verify-main-sync-merge.py 151
verify-main-sync-merge: MR !151 PASS — squash=false, squash_commit_sha=null, ...
```
**Result: PASS. T349's fix is now 3/3** (MR !126 recovery, MR !134 and MR !151 as standard
procedure).

Independently re-verified via git plumbing:
```
$ git log origin/main -1 --parents
f005c0f 9c4f82a a2fb072    Merge branch 'release/v6.8.0' into 'main'
```
`a2fb072` is `origin/develop`'s own real tip — genuine 2-parent merge, not a squash substitute.
`git merge-base --is-ancestor origin/develop origin/main` → exit 0. `git diff origin/main
origin/develop` → empty.

### Pipeline, final sync
`main`'s post-merge pipeline (sha `f005c0f6`) watched to completion: **success**. Local `develop`,
`main`, and tags synchronized with origin after everything landed; `release/v6.8.0` branch deleted
both locally and remotely (auto-removed on merge).

### Significance
Three consecutive successful uses of the PUT-first fix (MR !126, MR !134, MR !151), and two
consecutive conflict-free syncs (T351, T359) since T348's ancestry-restore commit — increasingly
solid evidence both fixes are holding up, not one-off results.
