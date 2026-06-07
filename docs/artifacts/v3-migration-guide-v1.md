# v3 Migration Guide v1

Status: Draft for rollout execution
Based on: [docs/artifacts/v3-benchmark-report-v1.md](v3-benchmark-report-v1.md), [docs/artifacts/v3-adapter-evaluation-v1.md](v3-adapter-evaluation-v1.md), [docs/artifacts/v3-hook-policy-spec-v1.md](v3-hook-policy-spec-v1.md)

## 1) Scope

This guide defines reversible migration from v2 to v3 for teams using emage.code platform projections and orchestration workflows.

## 2) Preconditions

Required baseline before migration:
- CI pipeline green on `develop`.
- v3 validation gate passes (`required`, `schemas`, `cookbooks`, `handoff-security`, `hook-policy`, `telemetry`, `benchmarks`, `registry`, `packaging`, `triggers`, `adapters`).
- Migration branch created from `develop` with rollback tag on last stable v2 commit.

## 3) Migration paths

### Path A: Conservative (recommended)

Use v3 in parallel while retaining v2 as active fallback.

Steps:
1. Keep v2 deployment untouched.
2. Enable v3 validation and smoke checks in CI.
3. Run v3 trigger and adapter smoke workflows in non-production environments.
4. Switch a pilot project to v3 outputs.
5. Promote to wider rollout after two consecutive green release cycles.

Rollback:
- Repoint consumers to v2 projected folders.
- Disable v3 experimental adapter flags.
- Restore previous release tag.

### Path B: Fast-track (limited use)

Use for low-risk internal teams needing rapid v3 adoption.

Steps:
1. Sync and verify v3 outputs.
2. Enable packaging and trigger workflows directly.
3. Enable adapters only for sandbox execution.

Rollback:
- Disable v3 adapters and triggers.
- Re-activate v2-only CI gates.

## 4) Compatibility matrix

| Area | v2 behavior | v3 behavior | Migration note |
|---|---|---|---|
| Knowledge source | v2 knowledge canonical | v3 implementation stream | keep v2 source for parity checks during migration |
| Validation | basic drift checks | super-gate + drift + functional smoke | adopt gates incrementally |
| Packaging | not standardized | install/update/uninstall workflow | use sample pack workflow as bootstrap |
| Triggers | none | schedule/event runner prototype | run in non-prod first |
| Adapters | projection-only model | optional SDK adapter prototypes | feature flags must remain off in prod initially |

## 5) Validation before cutover

Run from repository root:

```bash
python3 implementation/scripts/check-v3.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
python3 tests/run.py --suite functional
```

## 6) Reversibility checklist

Rollback is considered ready when all are true:
- Latest stable v2 release tag exists and is documented.
- v2 projection artifacts are still generated and verified.
- v3 feature flags can be disabled without code changes.
- Operator runbook includes rollback commands and owner contacts.

## 7) Known risks and controls

- Risk: CI drift due generated artifacts.
  Control: enforce generator `--check` modes in pipeline.
- Risk: trigger misconfiguration causes noisy orchestration.
  Control: policy allowlists + audit log review.
- Risk: adapter misuse introduces unsafe command paths.
  Control: fixed command mappings + disabled-by-default flags.

## 8) Go/No-Go decision rule

Go when:
- two consecutive pipeline runs are green,
- security controls and rollback checklist are complete,
- pilot users report no critical migration blockers.

No-Go when:
- any `FAIL` validation gate persists,
- rollback path is not verified,
- adapter or trigger controls are bypassed.
