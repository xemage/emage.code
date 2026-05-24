# Checkpoint v3-006 - Release Ready Execution

## Completed tasks
- T038: v3 drop-in contract defined (`docs/artifacts/v3-drop-in-contract-v1.md`)
- T039: v3 canonical tree bootstrapped (`v3/implementation/knowledge`, `platforms`, `_extras`, `docs`, conventions files)
- T040: v3 projection parity implemented (`sync-v3.mjs`, `verify-v3.mjs`, regression test)
- T041: v3 output generation and validation completed (`docs/artifacts/v3-parity-validation-report-v1.md`)
- T042: v3 CI gates added (`.gitlab-ci.yml`)
- T043: v3 docs and runbooks updated (`v3/implementation/README.md`, `README.md`, `CONTRIBUTING.md`, `docs/wiki/v3-implementation.md`)
- T044: QA/security gate executed (`docs/artifacts/v3-release-readiness-gate-v1.md`)

## In progress
- T045: Prepare v3 release candidate merge

## Key decisions
- v3 now uses a native default drift root (`v3/implementation`) while preserving optional v2 compatibility checks via `--root`.
- v3 sync/verify now uses cross-platform text normalization and POSIX manifest paths to avoid Windows false drift.

## Blockers
- None currently.

## Token metrics
- Planning budget (80k): within budget
- Implementation budget (120k): within budget
- QA/Security budget (60k): within budget

## Next steps
1. Commit and push branch changes over HTTPS.
2. Open or update MR and monitor branch/MR pipelines to green.
3. Merge and verify post-merge develop pipeline.
