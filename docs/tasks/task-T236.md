# Task T236 - SIA Evaluator Discriminative Scoring

**Status:** in_progress
**Owner:** backend-developer
**Priority:** P0
**Depends on:** T235
**Created:** 2026-06-24
**Blocker reference:** T233-BLK-002 (from `docs/artifacts/closed-loop-eval-report-v1.md`)

## Objective

Resolve the evaluator scoring layer so that harness execution produces non-zero,
discriminative reward signals that can support valid baseline vs fine-tuned model
quality delta measurement for T233.

## Background

T235 Phases 3.1–3.3 are complete: the CWSO executor correctly invokes the SIA
harness entrypoint. However, the `sia.util.run_agent` stub returns a mock
trajectory with no real LLM-generated code. As a result, the evaluator returns
`reward=0` for all runs regardless of model label — the scoring is non-discriminative.

Evidence:
- Both baseline (`07c25530`) and fine-tuned (`7be3c023`) v3 runs return `reward=0`
- `harness_status=success` in both cases — the execution pipeline is correct
- The stub generates placeholder trajectories, not real code the evaluator can score
- Parquet trajectories not captured (proxy has nothing to intercept when no LLM
  calls are made)

## Root Cause

`implementation/sia/util.py::run_agent()` is a PoC stub that returns a hardcoded
mock trajectory. This was created to unblock Phase 3.3 container wiring (T235).
The real implementation requires invoking an actual LLM through the rollout proxy.

## Work Items

### Option A: Wire real LLM via rollout proxy (preferred for real eval)

- Set `ANTHROPIC_BASE_URL` (or `OPENAI_BASE_URL`) in the executor environment to
  point at the rollout proxy (`http://rollout:8787`)
- Implement `sia.util.run_agent()` to make real agent calls through the proxy
- Confirm Parquet trajectories are captured per session ID
- Acceptance: `reward > 0` for at least one execution; Parquet file matches session ID

### Option B: Deterministic evaluator mock (unblocks T233 scoring parity test)

- Implement `sia.util.run_agent()` to return model-label-dependent output (e.g.,
  different quality code for baseline vs v1-ft labels)
- Allows the evaluator to score differently for the two groups
- Validates that the T233 scoring pipeline (harness → evaluator → reward) works end-to-end
- NOTE: Scores will be synthetic, not real model quality deltas — document clearly
- Acceptance: baseline and fine-tuned produce different `reward` values; delta != 0

## Expected Outputs

- Updated `implementation/sia/util.py` with real or discriminative stub agent
- If Option A: confirmation of Parquet capture with real LLM calls
- Updated `docs/artifacts/closed-loop-eval-report-v1.md` with non-zero delta results
- T233 unblocked and progressed to `in_review`

## Acceptance Criteria

1. At least one evaluation run returns `reward > 0` with non-stub execution
2. Baseline and fine-tuned groups produce different reward values (delta != 0)
3. T233 acceptance criteria achievable with new scoring signal
4. No hardcoded reward values in production path (Option B must be clearly documented as test-only)

## Execution Notes (2026-06-24)

- Option A implementation started and code changes applied:
  - `implementation/sia/util.py` now calls Anthropic `/v1/messages` via `ANTHROPIC_BASE_URL`
  - model label mapping added (`baseline`/`v1-ft` -> runtime model IDs)
  - generated code is extracted from response and persisted as `solution.py`
  - harness output now exposes `generated_code`, `runtime_model`, and usage metadata
  - executor compose wiring includes proxy + API key env passthrough
- Local regression tests: `tests/unit/test_sia_executor_phase32.py` pass (19/19).
- Validation blocker: live LLM run could not be executed in this shell because
  `ANTHROPIC_API_KEY` is not present in the active terminal environment.

## Execution Notes (2026-06-24, post-credit rerun)

- Local relay troubleshooting edits were reverted from the working tree before rerun.
- Re-ran Option A dispatches with fresh workspaces:
  - baseline: `bc349b82-7cfa-4f03-ac45-e4486f0115c3`
  - v1-ft: `30cd8b0c-efd9-4384-adc9-b92e5eb844ca`
- Current rollout status for both tasks remains `running` (no terminal result yet).
- `partial_results` and `trajectories` are empty for both runs, so reward values are
  still unavailable and delta is currently `null`.
- Captured summary artifact:
  - `docs/artifacts/t236-optionA-run-summary-2026-06-24.json`
- Captured diagnostics:
  - `/tmp/t236-rollout-baseline-optA5.json` reports `incomplete_phase2_runtime`
    with missing progression signals: no partial results, no trajectories,
    no parquet capture.
- Parquet store timestamps remain unchanged since 2026-06-23 14:02 for
  `/tmp/t226-parquet-store/trajectories-shard-00.parquet`,
  `/tmp/t226-parquet-store/trajectories-shard-01.parquet`, and
  `/tmp/t226-parquet-store/trajectories-shard-02.parquet`.

## Execution Notes (2026-06-24, optA6 live terminal polling)

- Previously stuck optA5 tasks (`bc349b82-7cfa-4f03-ac45-e4486f0115c3`,
  `30cd8b0c-efd9-4384-adc9-b92e5eb844ca`) were re-checked before cancellation and
  had already transitioned to terminal `completed` with timeout-origin outcomes,
  so no explicit cancel operation was required.
- Ran fresh Option A pair with extended live polling (`timeout=900s`) to force
  terminal states:
  - baseline: `04985794-0c24-4b59-bed7-0a07febf04f7`
  - v1-ft: `e6fdf50f-e68d-4824-a6df-41b32a901468`
- Both reached terminal `completed` with `merge_outcome=completed` and
  `trajectories_count=1`.
- Rewards remained non-discriminative:
  - baseline reward: `0`
  - v1-ft reward: `0`
  - delta: `0`
- Updated artifact with terminal evidence:
  - `docs/artifacts/t236-optionA-run-summary-2026-06-24.json`
- Parquet shard mtimes remain unchanged (still 2026-06-23 14:02), indicating no
  observable new shard writes in `/tmp/t226-parquet-store` despite terminal runs.
