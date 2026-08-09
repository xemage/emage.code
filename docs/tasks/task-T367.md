# Task T367 — Sync `main` with `develop` for v6.9.0 (release/v6.9.0 → main)

**ID:** T367
**Owner:** release-manager (executed jointly with orchestrator per T359/T351/T348 precedent —
ledger `Owner` column uses the single validated slug `release-manager`; the multi-agent execution
pattern is documented in `completed-tasks.md`'s own column format, not the active-ledger schema)
**Status:** pending
**Priority:** P1
**Depends on:** T366
**Created:** 2026-08-09
**Based on:** CONTRIBUTING.md § "Cutting a release" step 6 (PUT-first sequence); docs/tasks/task-T359.md,
task-T351.md, task-T348.md (precedent)

## Objective
Perform the standing GitFlow `release/vX.Y.Z → main` sync for v6.9.0, following `CONTRIBUTING.md`
§ "Cutting a release" step 6 exactly (the PUT-first sequence, 3/3 successful as of T359).

## Context
- Phase: Release (main-sync)
- Exact sequence (per CONTRIBUTING.md, verified current before use — do not pattern-match from
  memory):
  1. `glab api -X PUT projects/:id/merge_requests/:iid -f squash=false` — confirm response shows
     `squash: false`.
  2. `glab api -X PUT projects/:id/merge_requests/:iid/merge -f should_remove_source_branch=true`
  3. `python3 scripts/verify-main-sync-merge.py <mr_iid>` — run immediately regardless of step 1's
     apparent success.
- Pre-flight: confirm via `git log origin/develop..origin/main` whether `main` has any independent
  commits since the last sync (expected: none, per the T351/T359 pattern) — any GitLab-reported
  conflict is then almost certainly the phantom-ancestry pattern, safe to resolve by taking
  `develop`'s side after confirming via content diff, not commit-SHA ancestry (see
  `docs/tasks/task-T340.md` for why).

## Inputs
- `docs/tasks/task-T359.md` — most recent prior sync, full evidence trail
- `CONTRIBUTING.md` § "Cutting a release" step 6
- `scripts/verify-main-sync-merge.py`

## Constraints
- Use the PUT-first sequence as the primary attempt.
- If a conflict appears, diagnose phantom vs. real via content diff before resolving; escalate to
  user if it looks like a genuine (non-phantom) conflict, per the T331 precedent — do not resolve
  a real conflict unilaterally.
- Token budget: ≤ 60k.

## Expected Outputs
- `release/v6.9.0` branched from `origin/develop`'s tip, pushed
- MR `release/v6.9.0 → main` opened and merged via the PUT-first sequence
- `scripts/verify-main-sync-merge.py` result recorded
- Content verified identical between `origin/main` and `origin/develop` post-merge
- Post-merge `main` pipeline green
- Local `develop`/`main`/tags synchronized with origin

## Acceptance Criteria
1. `release/v6.9.0` branched from `origin/develop` tip, pushed to origin.
2. MR `release/v6.9.0 → main` opened.
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
<filled during execution>
