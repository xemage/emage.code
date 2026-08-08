# Task T351 — Sync `main` with `develop` for v6.7.1 (release/v6.7.1 → main)

**ID:** T351
**Owner:** orchestrator, release-manager
**Status:** done
**Completed:** 2026-08-08
**Priority:** P1
**Depends on:** T350
**Created:** 2026-08-08
**Based on:** `.claude/rules/git-workflow.md`, `docs/tasks/task-T331.md`, `docs/tasks/task-T339.md`,
`docs/tasks/task-T348.md` (precedent, three times now), `docs/tasks/task-T349.md` (the newly
documented procedure this task gets to actually test for the first time)

## Objective
Perform the standing GitFlow `release/vX.Y.Z → main` sync for v6.7.1. **This is the first real
test of T349's fix**: whether `PUT`-updating the MR resource's own `squash` attribute to `false`
before calling `/merge` reliably prevents GitLab from squashing the `release/*→main` merge, as it
did on MR !103, !109, and !125 despite the old `squash: false`-in-merge-body approach.

## Context
- Phase: Release (main-sync)
- Follow `CONTRIBUTING.md` § "Cutting a release" step 6 (as fixed by T349) — this is the
  documented standard procedure now, not an improvised recovery. Exact sequence:
  1. `glab api -X PUT projects/:id/merge_requests/:iid -f squash=false` — confirm response shows
     `squash: false` before proceeding
  2. `glab api -X PUT projects/:id/merge_requests/:iid/merge -f should_remove_source_branch=true`
  3. `python3 scripts/verify-main-sync-merge.py <mr_iid>` — run immediately, this is the safety
     net regardless of whether step 1 worked
- **If `verify-main-sync-merge.py` still reports FAIL despite the PUT-first sequence**, that is
  itself important, valuable evidence (the fix doesn't generalize) — follow
  `CONTRIBUTING.md` § "Post-merge squash verification" § "Recovery procedure" (also fixed by T349
  to the correct branch+MR sequence) and report the outcome plainly either way. Do not consider a
  FAIL here a task failure — it's exactly the kind of real-world data point this task exists to
  gather.
- Pre-flight check the orchestrator should run before branching: confirm via
  `git log origin/develop..origin/main` whether `main` has any independent commits since the last
  sync (T348) — if none (expected), any GitLab-reported conflict is again the phantom-ancestry
  pattern (T340), safe to resolve by taking `develop`'s side after confirming via content diff, not
  commit-SHA ancestry.

## Inputs
- `docs/tasks/task-T348.md` — most recent prior sync, full evidence trail
- `CONTRIBUTING.md` § "Cutting a release" step 6, § "Post-merge squash verification" — the fixed
  procedure to follow exactly
- `scripts/verify-main-sync-merge.py` — the verification tool, unchanged since T341/T345

## Constraints
- Use the PUT-first sequence as the primary attempt, not the old squash-false-in-merge-body
  approach — this task's entire point is testing the new documented procedure.
- If a conflict appears, diagnose phantom vs. real via content diff before resolving (same rule as
  T331/T339/T348) — do not assume, do not escalate unnecessarily if it's clearly phantom (zero
  independent `main` commits).
- Do not touch `develop` as part of this sync itself (only this task's own ledger closeout touches
  it, via a separate branch+MR per T342's rule).
- Token budget: ≤ 60k.

## Expected Outputs
- `release/v6.7.1` branched from `origin/develop`'s tip, pushed
- MR `release/v6.7.1 → main` opened
- Conflict (if any) diagnosed correctly (phantom vs real) before resolving
- Merged using the PUT-first sequence
- `python3 scripts/verify-main-sync-merge.py <mr_iid>` result recorded — **explicitly note whether
  this is a PASS (fix generalized) or FAIL (fix didn't generalize, recovery procedure invoked)**
- Content verified identical between `origin/main` and `origin/develop` post-merge (`git diff`)
- Post-merge `main` pipeline green
- Task brief updated with an `## Outcome` section

## Acceptance Criteria
- [x] `release/v6.7.1` branched from `origin/develop` tip, pushed to origin
- [x] MR `release/v6.7.1 → main` opened
- [x] Any conflict correctly diagnosed as phantom or real before resolution (none occurred — see
      Outcome)
- [x] Merged via the PUT-first sequence (not the old approach)
- [x] `scripts/verify-main-sync-merge.py` result recorded, with an explicit verdict on whether
      T349's fix generalized (this is the key evidence this task produces) — **PASS, fix
      generalized**
- [x] `git diff origin/develop origin/main` empty after merge and any recovery
- [x] Post-merge `main` pipeline green
- [x] No destructive git operations used at any point
- [x] Local checkout (`develop`, `main`, tags) synchronized with origin after everything lands

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries. A real (non-phantom) conflict on
`main` is a `critical` blocker requiring escalation, per the T331 precedent.

## Outcome (2026-08-08)

Executed directly by the orchestrator (same judgment call as T348, given real-time conflict
diagnosis needs).

### Pre-flight
`git log origin/develop..origin/main` confirmed `main`'s tip (`2a07558`, T348's ancestry-restore
commit) has zero independent commits since the last sync — everything listed is its own lineage.
Content diff showed the expected real difference (develop ahead by v6.7.1's work), no divergent
main-side content.

### Sync — no conflict this time
`release/v6.7.1` branched from `origin/develop`, pushed. MR !134 opened
(`release/v6.7.1 → main`). **Unlike every prior sync this session (T331, T339, T348), GitLab
reported `has_conflicts: false` immediately** — likely because T348's ancestry-restore commit
(`df26bb5`) genuinely fixed `main`'s merge-base resolution going forward, not just for that one
sync. No conflict resolution was needed.

### The real test: T349's PUT-first sequence
Followed `CONTRIBUTING.md` § "Cutting a release" step 6 exactly, for the first time as the
*documented standard* rather than an improvised recovery:
```
$ glab api -X PUT projects/.../merge_requests/134 -f squash=false
squash: False
$ glab api -X PUT projects/.../merge_requests/134/merge -f should_remove_source_branch=true
state: merged, merge_commit_sha: 9c4f82a2e83932d639fc2743411d28e934245873,
squash: False, squash_commit_sha: None
$ python3 scripts/verify-main-sync-merge.py 134
verify-main-sync-merge: MR !134 PASS — squash=false, squash_commit_sha=null, ...
```
**Result: PASS. T349's fix generalized on its first real re-test** (previously 1 success / 3
failures with the old approach; now 2/2 with the new sequence, though n is still small).

Independently re-verified via git plumbing, not taken on the API's word alone:
```
$ git log origin/main -1 --parents
9c4f82a 2a075582 199400d9    Merge branch 'release/v6.7.1' into 'main'
```
`199400d9` is `origin/develop`'s own real tip at merge time (no separate resolution commit was
needed since there was no conflict) — a genuine, correctly-ancestored 2-parent merge, not a
squash-commit substitute. `git merge-base --is-ancestor release/v6.7.1 origin/main` → exit 0.
`git diff origin/main origin/develop` → empty.

### Pipeline, final sync
`main`'s post-merge pipeline (`2743112943`, sha `9c4f82a2`) watched to completion: **success**.
Local `develop` was already synced (no changes needed — this task doesn't touch `develop` except
via this closeout); `origin/main` confirmed at `9c4f82a2e83932d639fc2743411d28e934245873`.

### Significance
Two consecutive data points now support the PUT-first fix (T349) actually working: MR !126
(recovery context) and MR !134 (standard-procedure context, this task). No conflict occurring at
all this time is a second, independent good sign that T348's ancestry-restore fix also holds up
over time, not just immediately after being applied. Neither claim is proven beyond doubt at n=2,
but both are now meaningfully more credible than "one lucky run."
