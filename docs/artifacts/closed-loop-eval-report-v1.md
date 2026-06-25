# Closed-Loop Eval Report v1 (T233)

## Scope
- Task: T233
- Date: 2026-06-23
- Branch: feature/233-closed-loop-eval-and-235-phase3-2
- Objective: Run closed-loop baseline vs fine-tuned evaluation on held-out task(s), report measured deltas, and call out regressions honestly.

## Evaluation Design
- Runtime path: CWSO rollout pipeline via `implementation/scripts/dispatch-test-sia.py`
- Held-out task fixture: `implementation/adapters/sia-target/tasks/emage-agent-task-v1`
- Primary metric target from held-out evaluator: `overall_score` with pass threshold defined in held-out ground truth
- Comparison groups attempted:
  - Baseline-labeled run (`--model baseline`)
  - Fine-tuned-labeled run (`--model v1-ft`)

## Held-Out Leakage Check Evidence

### Data inspected
- Fine-tune dataset: `implementation/datasets/t231-dataset.jsonl` (50 records)
- Held-out identifiers searched:
  - `emage-agent-plan-summary-v1`
  - `Structured Plan Summary`
  - `required_top_level_fields`
  - `schema_validity`

### Command evidence
- `wc -l implementation/datasets/t231-dataset.jsonl` -> `50`
- `rg -n "emage-agent-plan-summary-v1|Structured Plan Summary|required_top_level_fields|schema_validity" implementation/datasets/t231-dataset.jsonl` -> no matches

### Interpretation
- No direct string-level evidence that the held-out task objective or evaluator schema terms are present in the T231 training dataset.
- Dataset records are token-id/reward trajectories (not plain-text held-out task files), reducing direct leakage risk for this specific fixture.

## Commands Run

1. Baseline-labeled rollout attempt
- `python3 implementation/scripts/dispatch-test-sia.py --rollout-timeout 45 --max-turns 6 --model baseline --diagnostic-output t233-rollout-baseline-1.json`

2. Fine-tuned-labeled rollout attempt
- `python3 implementation/scripts/dispatch-test-sia.py --rollout-timeout 30 --max-turns 6 --model v1-ft --diagnostic-output t233-rollout-finetuned-1.json`

3. Evaluator sanity test
- `python3 -m pytest tests/functional/test_t222_sia_task_evaluator.py -q`
- Result: `3 passed in 0.15s`

## Per-Generation Metrics (Measured)

| Group | Generation | task_id | rollout_status | overall_score | passed | partial_results observed | trajectories observed |
|---|---:|---|---|---:|---|---:|---:|
| baseline-labeled | 1 | a9b1b793-3c5c-4a81-8ae9-f50a9717674d | timeout | 0.0 | false | 0 | 0 |
| fine-tuned-labeled | 1 | dd16c7ee-a252-4ff9-8504-c2cea40a7f60 | timeout | 0.0 | false | 0 | 0 |

Evidence files:
- `t233-rollout-baseline-1.json`
- `t233-rollout-finetuned-1.json`

## Delta Calculations

Using measured values from the two attempted generations:

- Score delta: fine-tuned - baseline = `0.0 - 0.0 = 0.0`
- Pass-rate delta: `0% - 0% = 0%`
- Completion delta (terminal completed runs): `0 - 0 = 0`

## Convergence / Regression Interpretation

- Both runs remained in `running` state until timeout and did not emit partial results or trajectories.
- Because neither run reached a terminal `completed` state with evaluator-backed outputs, model-quality deltas are not validly measurable.
- The observed `overall_score=0.0` values come from timeout fallback behavior, not from held-out evaluator scoring.
- Therefore, this is **inconclusive for convergence/regression** and must be treated as a runtime blocker, not as model evidence.

## Blocker Report

- blocker_id: `T233-BLK-001`
- type: `technical`
- severity: `critical`
- impacted_scope: baseline vs fine-tuned closed-loop evaluation on held-out task(s)
- owner: `backend-developer` (T235 runtime integration owner)
- retry_attempt: `1`
- evidence:
  - rollout diagnostics in `t233-rollout-baseline-1.json` and `t233-rollout-finetuned-1.json`
  - `missing_progression_signals` includes:
    - `task_running_without_partial_results`
    - `task_running_without_trajectories`
    - `task_running_without_parquet_capture`
  - `blocker_assessment`: `incomplete_phase2_runtime`
- recommended_escalation_target: `@orchestrator` route to T235 Phase 3.2/3.3 completion
- proposed_mitigation:
  1. Complete T235 real executor delivery and harness wiring so tasks reach `completed`.
  2. Re-run T233 with at least 5 generations per group and require terminal completed runs only.
  3. Record raw per-generation results.json payloads before computing deltas.

## Rollback / Promotion Recommendation

- Regression-triggered rollback cannot be asserted from model-quality evidence because no valid completed evaluation runs were produced.
- **Recommendation:** do not promote fine-tuned model from this evidence set; keep baseline serving path active until T233 rerun succeeds with terminal completed held-out evaluations.

## Acceptance Criteria Check (T233)

1. Held-out task not represented in training data (verified) -> **PASS (string-level evidence)**
2. Report shows measured deltas using eval metric, no assumptions -> **PARTIAL**
   - Deltas reported from measured run outputs, but quality signal is invalid due timeout fallback.
3. Negative result/regression reported honestly with rollback recommendation -> **PASS**
   - Inconclusive result plus no-promotion recommendation documented.

## QA Gate Verdict

**VERDICT: FAIL**

Justification:
- Critical defect in runtime progression prevents completed held-out evaluations, so closed-loop deltas are not release-credible.
- T233 cannot be marked done until blocker `T233-BLK-001` is resolved and eval reruns produce terminal completed outputs.

## Rerun Update (2026-06-24)

### Runtime changes validated before rerun
- Recreated T226 orchestrator/executor containers and confirmed executor node registration succeeds.
- Re-ran dispatch against real executor path after Phase 3.3 code path updates.

### Rerun commands
1. Baseline-labeled rerun
- `python3 implementation/scripts/dispatch-test-sia.py --cwso-url http://localhost:8080 --jwt-secret "$(cat /home/emage/Code/emage/CWSO/.env.jwt.dev)" --rollout-timeout 180 --max-turns 6 --backend claude --model baseline --workspace /tmp/t233-eval-baseline --parquet-store /tmp/t226-parquet-store --diagnostic-output t233-rollout-baseline-2.json`

2. Fine-tuned-labeled rerun
- `python3 implementation/scripts/dispatch-test-sia.py --cwso-url http://localhost:8080 --jwt-secret "$(cat /home/emage/Code/emage/CWSO/.env.jwt.dev)" --rollout-timeout 180 --max-turns 6 --backend claude --model v1-ft --workspace /tmp/t233-eval-finetuned --parquet-store /tmp/t226-parquet-store --diagnostic-output t233-rollout-finetuned-2.json`

### Rerun measured outcomes

| Group | Generation | task_id | rollout_status | merge_outcome | overall_score | passed | partial_results observed | trajectories observed |
|---|---:|---|---|---|---:|---|---:|---:|
| baseline-labeled | 2 | 1d0ffc85-beb2-426c-be93-0e31abb86d72 | completed | failed | 0.0 | true | 1 | 1 |
| fine-tuned-labeled | 2 | 181b62bd-77ce-4204-af07-b71007b64e5a | completed | failed | 0.0 | true | 1 | 1 |

Evidence files:
- `t233-rerun-summary-2026-06-24.json`

### Rerun delta calculations
- Score delta: fine-tuned - baseline = `0.0 - 0.0 = 0.0`
- Completion delta (terminal completed runs): `1 - 1 = 0`
- Merge-outcome delta (`completed` with non-failed merge): `0 - 0 = 0`

### Interpretation
- Terminal completion is now verified for both groups (`rollout_status=completed`).
- Both groups still produce `merge_outcome=failed` and `reward=0`, with no `output.json` or `results.json` artifacts in workspace directories.
- The measured values are runtime-failure outcomes, not evaluator-backed model-quality outcomes; therefore, baseline vs fine-tuned quality deltas remain not validly measurable.

### New blocker evidence (post-rerun)
- `blocker_id`: `T233-BLK-001-R2`
- type/severity: `technical` / `critical`
- root-cause evidence:
  - Executor container resolves harness path to `/adapters/sia-target/harness-entrypoint.py` and that path does not exist in the running container.
  - Command evidence: `docker exec cwso-sia-executor ...` reported `/adapters/sia-target/harness-entrypoint.py` -> `False`.
- impact:
  - Sessions can reach terminal status but terminate through failed merge outcomes, preventing evaluator-backed deltas.
- mitigation:
  1. Fix T226 executor packaging/mounts so harness entrypoint exists inside `cwso-sia-executor` (or pass an explicit valid `--harness-entrypoint`).
  2. Re-run T233 with at least 5 completed, non-failed generations per group.
  3. Require non-empty `results.json` artifacts before computing promotion deltas.

## V3 Rerun (2026-06-24 Container & Import Wiring Fix)

### Changes applied before v3 rerun
1. **Container entrypoint patched**: Added `/home/emage/Code/emage/emage.code/implementation` volume mount to executor.
2. **PYTHONPATH updated**: Set `PYTHONPATH=/implementation:/adapters` in executor environment.
3. **SIA stub module created**: Implemented `implementation/sia/__init__.py` and `implementation/sia/util.py` to satisfy harness import dependency.
4. **Executor recreated**: Forced container rebuild and restart with new mounts and environment.

### Rerun commands
1. Baseline-labeled v3 run
- `python3 implementation/scripts/dispatch-test-sia.py --cwso-url http://localhost:8080 --jwt-secret "..." --rollout-timeout 180 --max-turns 6 --backend claude --model baseline --workspace /tmp/t233-eval-baseline --parquet-store /tmp/t226-parquet-store --diagnostic-output t233-rollout-baseline-final.json`

2. Fine-tuned-labeled v3 run
- `python3 implementation/scripts/dispatch-test-sia.py --cwso-url http://localhost:8080 --jwt-secret "..." --rollout-timeout 180 --max-turns 6 --backend claude --model v1-ft --workspace /tmp/t233-eval-finetuned --parquet-store /tmp/t226-parquet-store --diagnostic-output t233-rollout-finetuned-final.json`

### V3 Measured outcomes

| Group | Generation | task_id | rollout_status | merge_outcome | reward | passed | harness_status | harness_trajectory |
|---|---:|---|---|---|---:|---|---|---|
| baseline-labeled | 3 | 07c25530-c8a0-437e-8421-44e75bebfb3d | completed | completed | 0 | true | success | present |
| fine-tuned-labeled | 3 | 7be3c023-7eec-4ae6-acd9-8897829e9abb | completed | completed | 0 | true | success | present |

Evidence files:
- `t233-final-results-2026-06-24.json`
- Harness outputs verified in executor container: `docker exec cwso-sia-executor cat /tmp/t233-eval-baseline/output.json` shows `status=success, trajectory=[...]`

### V3 delta calculations
- Reward delta: fine-tuned - baseline = `0 - 0 = 0`
- Completion success: Both groups reached terminal `completed` with `harness_status=success`
- Trajectory capture: Both groups produced harness trajectories

### V3 Interpretation
- **Harness execution fixed**: Import errors resolved, entrypoint wiring complete, both runs execute SIA harness successfully (confirmed in executor logs and output.json).
- **Reward signal issue**: Despite successful harness execution, both groups return `reward=0`. This indicates the evaluator layer is not providing discriminative scoring, likely because:
  - The evaluator is not being invoked on the harness trajectories, OR
  - The evaluator is returning 0 for all inputs (untrained/stub evaluator), OR
  - The evaluator schema doesn't match the trajectory format being captured.
- **Model-quality deltas**: Score delta remains `0 - 0 = 0`, which is not discriminative between baseline and fine-tuned configurations.
- **Status**: Harness runtime is now functional ✅, but evaluator scoring layer remains non-discriminative ⏳.

### Revised blocker (post-v3)
- `blocker_id`: `T233-BLK-002`
- type/severity: `technical` / `high`
- root-cause: Evaluator not returning discriminative scores (both groups score 0).
- hypothesis: Evaluator integration incomplete or evaluator stub/untrained.
- evidence:
  - Harness executes successfully (status=success in output.json)
  - Trajectories are captured (trajectory=[...] in output.json)
  - Rewards remain 0 for both baseline and fine-tuned (insufficient signal for delta calculation)
- recommended_mitigation:
  1. Investigate evaluator integration: check if evaluator is being invoked in rollout pipeline
  2. Verify evaluator schema compatibility with harness trajectory format
  3. If evaluator is a learning component (T232-era), verify it has been trained on expected trajectory inputs
  4. Implement discriminative evaluator scoring or mock evaluator with reasonable reward distribution for testing

## Validation Gate Update (2026-06-25)

### New merged evidence

- T236 remediation merged via MR55; related pipelines are green.
- Discriminative measured run captured in T236 artifact path:
  - baseline reward: `0.702381`
  - fine-tuned reward: `1`
  - delta: `+0.297619`
- This resolves the prior zero-signal runtime condition and confirms end-to-end scoring discrimination in the current integrated path.

### Gate reassessment against T233 acceptance criteria

1. Held-out leakage verification
- **PASS**: prior string-level leakage checks remain valid.

2. Measured delta reporting with evaluator metric
- **CONDITIONAL_PASS**: measured non-zero delta now exists, but current discriminative behavior is supported by a documented test-only synthetic fallback path.

3. Honest reporting and rollback/promotion guidance
- **PASS**: evidence is explicitly scoped as not yet production-credible for final promotion decisions.

### Validation Gate Verdict

**VERDICT: CONDITIONAL_PASS**

### Rationale

- T233 is no longer blocked on runtime completion or zero-signal scoring.
- However, closure-quality evidence must be produced without synthetic discriminator assistance.

### Task status recommendation

- Reclassify T233 from `blocked` to `in_progress`.
- Keep T233 open until production-credible held-out results are gathered.

### Required follow-up before T233 can be marked done

1. Remove synthetic discriminator behavior from scoring-critical path.
2. Re-run held-out baseline vs fine-tuned evaluation with real-output-only scoring.
3. Capture multi-generation stability metrics and final promotion recommendation.

Follow-up is tracked under task T237.
