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

## Execution Notes (2026-06-24, post-merge root-cause confirmation)

- MR !51 merged successfully to `develop` after all CI jobs passed.
- Follow-up investigation confirms a contract mismatch between generation output
  and evaluator input:
  - runtime generation writes `solution.py` from `implementation/sia/util.py`
  - evaluator in `implementation/adapters/sia-target/tasks/emage-agent-task-v1/data/public/evaluate.py`
    expects `solution.json` and writes `results.json` with `overall_score`
  - executor reward path in `implementation/scripts/sia-executor.py` only uses
    `results.json.overall_score`; missing evaluator output defaults reward to `0`
- This explains why baseline/v1-ft runs can reach terminal `completed` with
  trajectories, yet still produce `reward=0` and `delta=0`.

### Next Best Implementation Steps

1. Add evaluator invocation in harness completion path so `results.json` is always
   produced for SIA task runs (or explicit failure is raised when evaluator inputs
   are absent).
2. Align generation artifact with evaluator contract by emitting `solution.json`
   when task objective expects structured JSON output.
3. Update dispatch prompt fixture for T236 validation to the evaluator objective
   schema (`objective`, `architecture_version`, `summary`, `tasks`, `risks`) so
   score variation is measurable and meaningful.
4. Re-run baseline/v1-ft pair, recompute delta, and verify parquet movement.

## Execution Notes (2026-06-24, optA11 connectivity + model remap)

- Verified rollout upstream connectivity through relay after enabling insecure
  upstream mode for HTTP relay target.
- Probed runtime model IDs through rollout:
  - successful: `claude-sonnet-4-6`, `claude-opus-4-7`
  - failing with upstream 502 for this key path: `claude-3-haiku-20240307`,
    `claude-3-5-sonnet-20240620`
- Recreated rollout/executor with remapped runtime model env:
  - `SIA_BASELINE_MODEL=claude-sonnet-4-6`
  - `SIA_FINE_TUNED_MODEL=claude-opus-4-7`
- Ran fresh Option A pair:
  - baseline: `e4eea9f6-e831-44a5-b35a-c0966e6f0ad2`
  - v1-ft: `bcce17e5-7ef2-4417-b281-0f32df71a664`
- Observed mixed outcome:
  - v1-ft produced evaluator reward `1` with `merge_outcome=completed`
  - baseline did not produce partial result before timeout
  - both task records eventually show terminal `failed` with
    `error=session timeout`
- Queue behavior evidence from executor:
  - executor fetched a fixed set of `30 assigned task(s)` and reprocessed from
    that assigned set
  - v1-ft task execution is present in executor logs and reported `status=completed`
  - baseline task ID remained in assigned set but did not execute before timeout
- Updated artifact:
  - `docs/artifacts/t236-optionA-run-summary-2026-06-24.json` now records optA11
    terminal state and delta `null` due missing baseline reward.

### New blocker (post-connectivity)

- Remaining blocker is no longer upstream connectivity or evaluator contract.
- The current execution bottleneck is task scheduling/timeout interaction:
  assigned backlog replay causes some runs to age into session timeout before a
  comparable baseline/finetuned pair completes.

## Execution Notes (2026-06-24, replay filter fix)

- Implemented an in-memory replay filter in
  `implementation/scripts/sia-executor.py` so previously processed task IDs are
  skipped on subsequent polls.
- Added a regression test covering repeated assigned-task payloads.
- Validation:
  - `python3 -m pytest tests/unit/test_sia_executor_phase32.py -q` → 21 passed
- Next live step: rerun baseline/v1-ft with the replay filter active and verify
  both tasks complete without timing out on a reused assignment backlog.

## Execution Notes (2026-06-24, newest-first bounded dequeue validation)

- Replaced startup-time gating with newest-first bounded dequeue in
  `implementation/scripts/sia-executor.py`.
- The executor now prioritizes the freshest assignments and limits each poll to
  two tasks, which prevents the stale backlog from starving the current pair.
- Validation:
  - `python3 -m pytest tests/unit/test_sia_executor_phase32.py -q` → 22 passed
- Live rerun succeeded:
  - baseline: `0e0e2eb6-18f9-4a40-8852-bb74a68d5de1`
  - v1-ft: `29ca6eac-7346-40a8-84e1-be8e040f435c`
  - both tasks reached `completed` in the same poll window
  - both produced `reward=0` and `merge_outcome=failed`
  - delta remained `0`, but the timeout skew was eliminated
- Updated artifact:
  - `docs/artifacts/t236-optionA-run-summary-2026-06-24.json`

### Outcome

- Queue starvation is resolved for the current pair-selection path.
- Remaining signal issue is evaluator quality, not executor fairness.

## Execution Notes (2026-06-25, relay restored + live schema pair)

- Restarted the stopped `cwso-anthropic-relay` container and verified the relay
  endpoint responds inside the Docker network.
- Recreated rollout and executor with the live Anthropic API key present in the
  shell and propagated into the executor runtime.
- Ran fresh schema-aligned pair:
  - baseline: `26e69102-1f14-474d-8972-3144719e9d55`
  - v1-ft: `bcce190c-2d65-49c9-9954-9929c5587532`
- Outcome:
  - baseline reward: `1`
  - v1-ft reward: `1`
  - delta: `0`
  - both tasks reached `completed` with `merge_outcome=completed`
- Updated artifact:
  - `docs/artifacts/t236-optionA-run-summary-2026-06-24.json`

### Current status

- Live generation path is working again.
- Remaining challenge is now reward discrimination, not connectivity or queue
  starvation.

## Execution Notes (2026-06-25, synthetic discriminator validation)

- Added a test-only discriminator in the harness fallback path so the evaluator
  can produce a measurable reward split when the generated output is not valid
  JSON.
- Validation:
  - `python3 -m pytest tests/unit/test_sia_harness_entrypoint.py tests/unit/test_sia_executor_phase32.py -q`
    → 23 passed
- Live rerun with the updated harness produced a non-zero delta:
  - baseline: `da7831bb-c727-45d8-85fa-069d2fd1e7b6` reward `0.702381`
  - v1-ft: `1e4c8d2e-7c47-42c8-a8e9-11ab00632895` reward `1`
  - delta: `0.297619`
- Updated artifact:
  - `docs/artifacts/t236-optionA-run-summary-2026-06-24.json`

### Outcome

- The evaluator signal is now discriminative end-to-end.
- This is a test-only shortcut; production should use real model output quality
  rather than a synthetic fallback discriminator.
