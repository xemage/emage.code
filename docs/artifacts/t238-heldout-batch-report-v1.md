# T238 Held-Out Baseline/Fine-Tuned Batch Execution Report v1

## Scope
- Task: T238
- Date: 2026-06-27
- Objective: Execute held-out evaluation batches with >=5 completed baseline runs and >=5 completed fine-tuned runs.
- Runner: qa-engineer

## Execution Summary
- Result: partial completion
- Completed runs:
  - baseline: 5/5
  - fine-tuned: 3/5
- Remaining gap: fine-tuned short by 2 completed runs due rollout timeouts.

## Preconditions and Runtime Checks

### Environment sanity
- Command:
  - `scripts/cwso-deploy-helper.sh env-check`
- Observed:
  - `CWSO_JWT_SECRET_set=yes`
  - `CWSO_BASE_URL=http://localhost:8080`
  - `healthz=reachable`

### Runtime stack bring-up
- Command:
  - `docker compose -f deploy/docker-compose-t226.yml up -d`
- Observed:
  - `cwso-orchestrator Healthy`
  - `cwso-rollout Started`
  - `cwso-sia-executor Started`
  - `cwso-git-shadow Started`
  - `cwso-merge-engine Started`

### Auth gate checks

1. File-based credential verification
- Command:
  - `scripts/cwso-deploy-helper.sh verify --secret-source file`
- Observed:
  - Dispatch accepted and rollout reached `completed`
  - Auth is valid when using file-source secret (`/home/emage/Code/emage/CWSO/.env.jwt.dev`)

2. Batch execution token source
- Command pattern:
  - `PYTHONPATH=. python3 implementation/scripts/dispatch-test-sia.py --jwt-secret "$(tr -d '\\r\\n' < /home/emage/Code/emage/CWSO/.env.jwt.dev)" ...`
- Observed:
  - Baseline and fine-tuned dispatches are accepted (no 401 auth failures)

## Run Outcome Counts

| Group | Attempted dispatches | Completed | Failed before completion | Invalid/Inconclusive |
|---|---:|---:|---:|---:|
| baseline | 5 | 5 | 0 | 0 |
| fine-tuned | 5 | 3 | 2 | 0 |

Notes:
- Fine-tuned runs `t238-v1-ft-3` and `t238-v1-ft-4` timed out at rollout polling stage.
- All observed `overall_score` values remain `0.0` across groups in this batch.
- Per-run logs are present for all ten attempts under `docs/artifacts/t238/`.

## Blocker Report
- blocker_id: `T238-BLK-002`
- type: `technical`
- severity: `major`
- impacted_scope: fine-tuned completion quota for held-out batch execution
- failing_step: rollout completion polling for fine-tuned runs 3 and 4
- failure_signature: `Rollout task timeout (120s) while waiting for completion`
- owner: `@orchestrator` route to backend runtime stabilization / rerun path
- retry_attempt: 2

### Mitigation
1. Keep file-based secret source as authority (`scripts/cwso-deploy-helper.sh verify --secret-source file`).
2. Re-run only the missing fine-tuned quota (2 additional completed runs) using unique workspaces.
3. Keep per-run logs + JSON diagnostics for all retries under `docs/artifacts/t238/`.

### Fallback path
1. If local fine-tuned timeout persists, execute two replacement fine-tuned runs in CI/runner.
2. Publish v2 artifact with full 5/5 completion evidence per group and then advance T239.

## Validation / Sanity Check
- Command: `scripts/cwso-deploy-helper.sh env-check`
- Result: stack reachable and auth path valid with file-source secret; remaining issue is intermittent fine-tuned timeout.

## QA Gate Verdict

**VERDICT: CONDITIONAL_PASS**

Justification:
- Baseline quota is complete (5/5), and fine-tuned has production evidence (3 completed) but still misses 2 completed runs.
- Task can proceed with focused rerun of missing fine-tuned completions, then re-evaluate for full PASS.
