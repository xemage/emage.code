# Task T359 — Sync `main` with `develop` for v6.8.0 (release/v6.8.0 → main)

**ID:** T359
**Owner:** orchestrator, release-manager
**Status:** pending
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
