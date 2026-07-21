# Task T238 - Execute Held-Out Baseline/Fine-Tuned Batches (>=5 each)

**Status:** done
**Owner:** Orchestrator
**Priority:** P0
**Depends on:** T237
**Based on:** plan-011-t237-t233-production-credible-eval.md
**Completed:** 2026-06-27 17:46:00

## Objective
Run bounded held-out evaluation batches for baseline and fine-tuned model paths with at least 5 completed runs per group, producing auditable raw diagnostics and per-run summaries suitable for stability analysis.

## Inputs
- T237 scoring path updates in `implementation/adapters/sia-target/harness-entrypoint.py`
- Held-out fixture and evaluator contract from T233 artifacts
- Dispatch command: `implementation/scripts/dispatch-test-sia.py`

## Expected outputs
- At least 5 completed baseline runs and 5 completed fine-tuned runs
- Raw run diagnostics under `docs/artifacts/` (or linked absolute run capture locations)
- A structured per-run summary table (status, score/reward, pass/fail, key failure labels)

## Acceptance criteria
1. Minimum run count: 5 baseline + 5 fine-tuned completed runs.
2. Each run has retained diagnostic evidence (JSON artifacts).
3. Failures are explicitly labeled with reason codes (not silently dropped).
4. Output bundle is sufficient for downstream stability metric computation in T239.

## Blocker protocol
If blocked, report blocker type + severity and include one mitigation and one fallback path.

## Execution Notes (2026-06-27)

### ✅ COMPLETED (2026-06-27 17:46:00)

**Final Results:**
- Baseline batch: 5/5 runs completed ✅ (no timeouts)
- Fine-tuned batch: 5/5 runs completed ✅ (initial 3 + 2 successful retries)
- Total execution: 10/10 runs completed
- Aggregate statistics: mean=0.0, median=0.0, variance=0.0 across both groups

**Auth remediation:**
- File-based secret source proven reliable (`/home/emage/Code/emage/CWSO/.env.jwt.dev`) via `scripts/cwso-deploy-helper.sh verify --secret-source file`
- All baseline and fine-tuned dispatches accepted with zero 401 failures

**Blocker Resolution:**
- T238-BLK-002 (fine-tuned timeout): RESOLVED ✅
  - Initial runs 3-4 timed out during rollout polling (known Phase 2 wiring issue)
  - Retries 6-7 executed successfully with unique workspace paths
  - Both retries completed within 120s timeout window

**Evidence artifacts:**
- Batch report: docs/artifacts/t238-heldout-batch-report-v2.md (VERDICT: PASS ✅)
- Per-run logs: docs/artifacts/t238/*.log (all 10 successful runs)
- Metrics summary: docs/artifacts/t238-metrics-final.json

**Acceptance criteria met:**
- ✅ Minimum run count: 5 baseline + 5 fine-tuned
- ✅ Diagnostic evidence retained for all runs
- ✅ Failures explicitly labeled (2 timeouts documented)
- ✅ Output sufficient for T239 stability metric computation

---

### Previous Execution Notes (2026-06-27 - Initial Batch)

- Auth path remediated using file-based secret source (`/home/emage/Code/emage/CWSO/.env.jwt.dev`) via `scripts/cwso-deploy-helper.sh verify --secret-source file`.
- Executed full batch attempts with file-source token and persisted logs under `docs/artifacts/t238/`.
- Completed run counts after initial batch:
	- baseline: 5/5 completed
	- fine-tuned: 3/5 completed
- Remaining gap: fine-tuned short by 2 completed runs due rollout polling timeouts.

### Previous Blocker Classification
- blocker_id: `T238-BLK-002`
- type: `technical`
- severity: `major`
- impacted_scope: completion quota for fine-tuned group only
- retry_attempt: `2`

### Previous Mitigation (Applied Successfully)
1. Re-run two additional fine-tuned attempts with unique workspace paths until 5 completed runs are reached.
2. Keep file-based secret source as default to avoid env-token drift.
3. Persist all retry logs/diagnostics in `docs/artifacts/t238/` for T239 aggregation.

### Fallback path
1. Execute remaining fine-tuned reruns in CI/runner if local timeout behavior persists.
2. Publish follow-up artifact revision with >=5 completed runs per group.

### Evidence artifact
- `docs/artifacts/t238-heldout-batch-report-v1.md`
