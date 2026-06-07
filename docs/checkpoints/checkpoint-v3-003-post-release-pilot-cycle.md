# Checkpoint v3-003 - Post-release Pilot Cycle

Phase: Pilot rollout (Path A) after release publication
Date: 2026-05-23
Based on: [docs/plans/plan-003-v3-execution-wave1.md](../plans/plan-003-v3-execution-wave1.md), [docs/artifacts/release-announcement-v1.md](../artifacts/release-announcement-v1.md)

## Pilot scope

- Start conservative migration path in non-production.
- Keep v2 as active fallback baseline.
- Validate rollback anchors and rollback drill procedure.

## Rollback drill evidence

1. Tag anchors verified:
- `v0.1.0` and `v0.1.1` both exist and resolve to immutable commits.

2. v2 fallback baseline verified:
- Command: `node v2/implementation/scripts/verify.mjs`
- Result: `OK - no drift across 313 files`.

3. v3 pilot validation verified:
- Command: full super-gate via `python3 implementation/scripts/check-v3.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters`
- Result: `OK - 235 checks passed, 0 errors`.

4. Functional safety baseline verified:
- Command: `python3 tests/run.py --suite functional`
- Result: `Ran 56 tests ... OK`.

5. Feature-flag guardrail verified:
- Command: `python3 implementation/adapters/smoke.py --adapter antigravity --input tests/fixtures/adapters/sample-input.json`
- Result: `adapter_disabled: antigravity`.

## Pilot verdict

CONDITIONAL_PASS

Conditions to continue pilot and prepare wider rollout:
1. Keep `V3_EXPERIMENTAL_ADAPTERS` disabled outside sandbox/pilot environments.
2. Require explicit security approval before enabling trigger schedules against production-connected sources.
3. Execute one additional release cycle with unchanged rollback pass criteria.

## Next step

Proceed with pilot project switch to v3 outputs while keeping v2 rollback path active and re-run rollback drill at end of pilot window.
