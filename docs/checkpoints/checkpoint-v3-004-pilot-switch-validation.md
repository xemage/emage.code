# Checkpoint v3-004 - Pilot Switch Validation

Phase: Pilot rollout validation
Date: 2026-05-23
Based on: [docs/checkpoints/checkpoint-v3-003-post-release-pilot-cycle.md](checkpoint-v3-003-post-release-pilot-cycle.md)

## Completed items

- Executed pilot trigger runs for schedule and event sources.
- Executed adapter sandbox smoke runs with explicit feature flags.
- Completed second rollback drill and validation gate sweep.

## Evidence summary

- Trigger execution:
  - schedule run: success in 1 attempt.
  - event run: success in 2 attempts with retry evidence.
- Pilot artifacts:
  - `tests/_reports/pilot/trigger-queue.json` (2 queued events)
  - `tests/_reports/pilot/trigger-audit.log` (9 audit entries, 1 retry)
  - `tests/_reports/pilot/adapter-antigravity.json`
  - `tests/_reports/pilot/adapter-opencode.json`
- Rollback anchors re-verified:
  - `v0.1.0` commit: `82840137171c15f89f8a62cf38beb5b4c90d934b`
  - `v0.1.1` commit: `9cd80c9cf9a5dcac7c7cde02bd95a61e425375fc`
- Validation gates:
  - v2 verify: pass
  - v3 super-gate: pass
  - functional suite: pass

## Verdict

CONDITIONAL_PASS

Conditions retained:
1. Keep adapter flags disabled by default outside sandbox/pilot environments.
2. Maintain deny-by-default trigger policies and audited execution paths.
3. Require one additional successful pilot cycle before broad rollout promotion.

## Next step

Proceed to pilot cycle 2 with unchanged rollback controls and publish a promotion-readiness checkpoint after second-cycle evidence collection.
