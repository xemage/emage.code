# v3 Pilot Rollout Report v2

Status: Pilot cycle-2 executed (non-production)
Date: 2026-05-23
Based on: [docs/artifacts/v3-pilot-rollout-report-v1.md](v3-pilot-rollout-report-v1.md), [docs/plans/plan-003-v3-execution-wave1.md](../plans/plan-003-v3-execution-wave1.md)

## Objective

Execute pilot cycle-2 with unchanged controls and collect promotion-readiness evidence for broader rollout decisioning.

## Cycle-2 execution summary

1. Trigger framework runs:
- Schedule trigger completed in 1 attempt.
- Event trigger completed in 2 attempts with one simulated retry.
- Artifacts generated:
  - `tests/_reports/pilot-cycle2/trigger-queue.json`
  - `tests/_reports/pilot-cycle2/trigger-audit.log`

2. Adapter sandbox runs:
- Antigravity smoke output captured in `tests/_reports/pilot-cycle2/adapter-antigravity.json`.
- Opencode smoke output captured in `tests/_reports/pilot-cycle2/adapter-opencode.json`.
- Disabled-by-default guardrail re-verified: `adapter_disabled: antigravity` when flags are not set.

3. Evidence metrics:
- queue events: 2
- audit lines: 9
- retry entries: 1

## Rollback and validation checks

- v2 fallback verification: pass (`OK - no drift across 313 files`).
- v3 full super-gate: pass (`OK - 235 checks passed, 0 errors`).
- functional suite: pass (`Ran 56 tests ... OK`).
- rollback anchors re-verified:
  - `v0.1.0` -> `82840137171c15f89f8a62cf38beb5b4c90d934b`
  - `v0.1.1` -> `9cd80c9cf9a5dcac7c7cde02bd95a61e425375fc`

## Promotion readiness recommendation

CONDITIONAL_TO_GO for broader rollout.

Required controls before broad enablement:
1. Keep `V3_EXPERIMENTAL_ADAPTERS` disabled by default in production contexts.
2. Require security approval for any production-connected trigger source activation.
3. Maintain rollback drill cadence per release cycle and retain tag-anchor verification.
