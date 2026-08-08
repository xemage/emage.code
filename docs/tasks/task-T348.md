# Task T348 — Sync `main` with `develop` for v6.7.0 (release/v6.7.0 → main)

**ID:** T348
**Owner:** orchestrator, release-manager
**Status:** done
**Completed:** 2026-08-08
**Priority:** P1
**Depends on:** T347
**Created:** 2026-08-08
**Based on:** `.claude/rules/git-workflow.md`, `docs/tasks/task-T331.md` and `docs/tasks/task-T339.md`
(precedent — this exact operation, twice), `docs/tasks/task-T340.md` (root-cause of the recurring
phantom-ancestry conflict), `docs/tasks/task-T341.md` (the new verification tool this task gets to
actually use for the first time on a real sync)

## Objective
Perform the standing GitFlow `release/vX.Y.Z → main` sync for v6.7.0, per the policy T331
diagnosed as historically neglected and the `main-develop-drift-gate` (plan-019) now enforces.
`main` is currently 1 release behind `develop` (`main` at v6.6.0's sync point, `develop` at
v6.7.0) — within the drift gate's grace window, but due for sync now per this repo's standing
practice of syncing every release before the next one ships.

## Context
- Phase: Release (main-sync, not a new feature release)
- Pre-flight check already done by the orchestrator: `git log origin/develop..origin/main`
  confirms `main`'s current tip (`c14bf79`, the T339/MR !109 sync commit) has **zero independent
  commits** since the last sync — everything listed is `main`'s own historical lineage, not new
  content added on top of `develop`. This matches the exact pattern from both T331 and T339: safe
  to resolve any conflict by taking `develop`'s side, if a conflict appears.
- **Expect a phantom conflict, not real drift.** Per T340's root-cause finding, `main`'s tip
  (`c14bf79`) has a GitLab-squashed second parent (`25fa98e`, MR !109's own `squash_commit_sha`)
  rather than `develop`'s real historical tip — this corrupts `git merge-base(main, develop)` for
  *any* future sync, not just the one immediately after. If GitLab reports a conflict on this MR,
  do not assume real content drift without checking: confirm via `git diff origin/develop
  origin/main` (content-level, not merge-base-level) whether they're actually divergent.
- **This is the first real production use of T341's `scripts/verify-main-sync-merge.py`.** Run it
  immediately after the merge completes, exactly as its own CONTRIBUTING.md § "Post-merge squash
  verification" documents. Given GitLab squashed both prior syncs (MR !103, MR !109) despite an
  explicit `squash: false` override, expect it may happen again — if it does, this task is the
  first real test of whether the tool's detection loop (verify → recovery procedure) actually
  works end-to-end, which is valuable evidence for T341's own "evaluate on the next real sync"
  condition (see `docs/tasks/task-T341.md` § Recommendation).

## Inputs
- `docs/tasks/task-T331.md`, `docs/tasks/task-T339.md` — exact prior procedure, twice-proven
- `docs/tasks/task-T340.md` § Findings — why phantom conflicts happen, so any conflict here is
  diagnosed correctly instead of re-investigated from scratch
- `scripts/verify-main-sync-merge.py`, `CONTRIBUTING.md` § "Post-merge squash verification" — the
  tool and procedure to run immediately post-merge
- `scripts/check-main-develop-drift.py` — for a pre/post sanity check of the drift signal

## Constraints
- No squash on the actual `release/v6.7.0 → main` merge — explicit `squash: false` in the merge
  API call, matching prior precedent (even though it has not reliably taken effect before — still
  the correct thing to request).
- If a conflict appears, resolve only after confirming (via content diff, not assumption) whether
  it is phantom (main has zero independent commits — take develop's side) or real (main has
  independent content — escalate to the orchestrator/user per the T331 precedent, do not resolve
  unilaterally).
- Do not touch `develop` as part of this sync itself (only this task's own ledger closeout touches
  it, via a separate branch+MR per T342's rule).
- Token budget: ≤ 60k.

## Expected Outputs
- `release/v6.7.0` branched from `origin/develop`'s tip, pushed
- MR `release/v6.7.0 → main` opened, referencing this task and `docs/releases/v6.7.0.md`
- Conflict (if any) diagnosed correctly (phantom vs real) before resolving
- MR merged (non-squashed intent, `main`, `develop` untouched otherwise)
- `python3 scripts/verify-main-sync-merge.py <mr_iid>` run immediately post-merge — result cited
  either way (PASS or the recovery procedure invoked)
- Content verified identical between `origin/main` and `origin/develop` post-merge (`git diff`,
  not commit-SHA ancestry)
- Post-merge `main` pipeline green
- Task brief updated with an `## Outcome` section citing exact commands/output

## Acceptance Criteria
- [x] `release/v6.7.0` branched from `origin/develop` tip, pushed to origin
- [x] MR `release/v6.7.0 → main` opened
- [x] Any conflict correctly diagnosed as phantom or real before resolution (cite the check)
- [x] Merged with `squash: false` explicitly requested (see Outcome for what actually happened)
- [x] `scripts/verify-main-sync-merge.py` run against the real merged MR, result recorded
      (including recovery-procedure execution if it fires)
- [x] `git diff origin/develop origin/main` empty (content-identical) after merge and any recovery
- [x] Post-merge `main` pipeline green
- [x] No destructive git operations used at any point
- [x] Local checkout (`develop`, `main`, tags) synchronized with origin after everything lands

## Blocker Protocol
Report blockers per `AGENTS.md`: type (`technical` | `dependency` | `unclear_requirements` |
`external`) + severity (`critical` | `major` | `minor`). Max 2 retries. A real (non-phantom)
conflict on `main` is a `critical` blocker requiring escalation, per the T331 precedent — do not
resolve real content drift unilaterally.

## Outcome (2026-08-08)

Executed directly by the orchestrator (not delegated — same judgment call as T339, given the
established, twice-proven procedure and the need for real-time conflict diagnosis).

### Pre-flight: confirmed phantom, not real, before touching anything
`git log origin/develop..origin/main` showed `main`'s tip (`c14bf79`) has zero independent commits
since the T339 sync — everything listed is its own historical lineage. This was the deciding fact
for every resolution choice below.

### Step 1 — branch, MR, conflict
`release/v6.7.0` branched from `origin/develop` (`dd9c52d`), pushed. MR !125 opened
(`release/v6.7.0 → main`). GitLab reported `detailed_merge_status: conflict`, `has_conflicts:
true` — as expected (T340's phantom-ancestry mechanism, not real drift).

### Step 2 — diagnosis before resolution
`git diff origin/main origin/develop --stat`: 63 files, insertions/changes only (the real v6.7.0
work), no divergent main-side content. Combined with the pre-flight check (zero independent main
commits), this confirms the conflict is phantom, matching T331/T339 exactly — not escalated, per
the brief's own criterion (only real drift requires escalation).

### Step 3 — resolution
Local `git merge origin/main` while on `release/v6.7.0` produced 32 conflicting files (all
`git checkout --theirs`-in-MR-terms are actually `--ours` here, i.e. `release/v6.7.0`'s own
content — full list in commit `cbd4d62`'s message). Resolved by taking `release/v6.7.0`'s side on
all 32 via `git checkout --ours -- <file>` for each, `git add -A`, committed
(`cbd4d62c8fc9d6639ab9469e0d96ec20742c4e71`), pushed. Verified before pushing:
`git diff origin/develop release/v6.7.0` → empty (byte-identical).

### Step 4 — verification bar, merge
MR !125 became conflict-free and `mergeable` after push. Full bar re-run on the resolved branch:
`tests/run.py` → 293 OK/17 skipped; `sync.mjs --check` → 0 drift/511 files;
`validate-tasks.py` → PASS. Merged via
`glab api -X PUT .../merge_requests/125/merge -f squash=false -f should_remove_source_branch=true`.
API response read `squash: True` anyway — same misleading-field pattern as MR !103/!109.

### Step 5 — T341's tool, first real production run
`python3 scripts/verify-main-sync-merge.py 125` → **FAIL** (exit 1): `squash=True,
squash_commit_sha=16298ff...`. This is the tool working exactly as designed — immediate,
actionable detection instead of discovering the corruption a full release cycle later (T339's
original experience). Independently confirmed via git plumbing:
`origin/main`'s new tip (`9831fb3`) has parents `c14bf79` (old tip) and `16298ff` (GitLab's own
`squash_commit_sha`) — **not** `cbd4d62` (the real, correctly-ancestored merge commit). Content
diff (`git diff origin/main origin/develop`) was still empty — phantom ancestry, correct content,
exactly T340's mechanism.

### Step 6 — recovery procedure, adapted for this project's actual branch protection
`CONTRIBUTING.md`'s documented recovery procedure (`git push` directly to `main` after a local
`-s ours` no-op merge) **cannot work as literally written**: confirmed via
`glab api projects/.../protected_branches/main` — `push_access_levels: ['No one']`, identical to
`develop`'s protection. Adapted: branched `chore/restore-ancestry-v6.7.0` from `origin/main`,
created the no-op merge commit there
(`git merge --no-ff cbd4d62 -s ours -m "chore(release): restore true ancestry..."`), verified
`git diff origin/main HEAD` empty and `git merge-base --is-ancestor cbd4d62 HEAD` → exit 0 before
pushing. Opened MR !126 (`chore/restore-ancestry-v6.7.0 → main`).

### Step 7 — root-cause finding: the actual fix for the recurring squash problem
Before merging MR !126, checked the MR resource's own `squash` field directly (not just the merge
call's parameter): `glab api projects/.../merge_requests/126` → `squash: true` (inherited from the
project's `squash_option: default_on`, independent of what gets passed to `/merge`). Tried
**`glab api -X PUT projects/.../merge_requests/126 -f squash=false`** — updating the MR resource
itself, not just the merge action's parameter — and it stuck: `squash: false` confirmed on
re-read. Merged MR !126 (without needing to pass `squash` in the merge call at all, since the MR
resource was already correctly `false`): response showed `squash: False`,
`squash_commit_sha: None` — **the override held, for the first time this session.**

Independently re-verified: `origin/main`'s new tip (`2a07558`) has parents `9831fb3` (previous
main tip) and `df26bb5` (the no-op restore commit), and `df26bb5`'s own second parent is `cbd4d62`
— so `cbd4d62` **is now a genuine ancestor of `main`**
(`git merge-base --is-ancestor cbd4d62 origin/main` → exit 0). Content diff still empty.
`python3 scripts/verify-main-sync-merge.py 126` → **PASS**.

**This is a genuine, actionable finding beyond this task's original scope**: T340 could not
determine whether GitLab's squash-despite-override behavior was a server quirk or a client
issue. This session's evidence points to the latter — updating the MR resource's persisted
`squash` attribute via `PUT /merge_requests/:iid` *before* calling `/merge` reliably prevented the
squash, where passing `squash: false` only in the `/merge` call's own body (as MR !103, !109, and
!125 all did) did not. Not yet generalized into `CONTRIBUTING.md`, `scripts/verify-main-sync-merge.py`,
or a fix task — flagged for the orchestrator/user to decide whether to schedule as a follow-up
(same treatment T331→plan-019 and T339→T340 got).

### Step 8 — pipelines, final sync
`main`'s pipeline for MR !125's merge (`9831fb31`, `2743014069`): success. `main`'s pipeline for
MR !126's merge (`2a075582`, `2743019468`): success (watched to completion, not assumed). Local
`develop` fast-forwarded to `origin/develop`'s tip (no changes were needed there — this task never
touches `develop` directly, only its own ledger closeout does, via a separate branch+MR).

Release URL (unchanged by this task, referenced for completeness):
<https://gitlab.com/em-age/emage.code/-/releases/v6.7.0>
