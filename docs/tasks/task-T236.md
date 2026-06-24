# Task T236 - SIA Evaluator Discriminative Scoring

**Status:** pending
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
