# Task T348 — Sync `main` with `develop` for v6.7.0 (release/v6.7.0 → main)

**ID:** T348
**Owner:** orchestrator, release-manager
**Status:** in_progress
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
- [ ] `release/v6.7.0` branched from `origin/develop` tip, pushed to origin
- [ ] MR `release/v6.7.0 → main` opened
- [ ] Any conflict correctly diagnosed as phantom or real before resolution (cite the check)
- [ ] Merged with `squash: false` explicitly requested
- [ ] `scripts/verify-main-sync-merge.py` run against the real merged MR, result recorded
      (including recovery-procedure execution if it fires)
- [ ] `git diff origin/develop origin/main` empty (content-identical) after merge and any recovery
- [ ] Post-merge `main` pipeline green
- [ ] No destructive git operations used at any point
- [ ] Local checkout (`develop`, `main`, tags) synchronized with origin after everything lands

## Blocker Protocol
Report blockers per `AGENTS.md`: type (`technical` | `dependency` | `unclear_requirements` |
`external`) + severity (`critical` | `major` | `minor`). Max 2 retries. A real (non-phantom)
conflict on `main` is a `critical` blocker requiring escalation, per the T331 precedent — do not
resolve real content drift unilaterally.
