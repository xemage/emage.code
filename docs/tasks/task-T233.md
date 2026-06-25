# Task T233 - Closed-loop eval on held-out task; measure deltas

**Status:** in_progress
**Owner:** qa-engineer
**Priority:** P0

## Objective
Run several SIA generations against a fixed held-out task using the fine-tuned model and measure performance
deltas versus the baseline model, validating that the loop improves outcomes.

## Inputs
- Fine-tuned + redeployed model (T231)
- Gated pipeline (T232)
- A held-out SIA task with ground truth (separate from training data)

## Expected outputs
- `docs/artifacts/closed-loop-eval-report-v1.md` with baseline vs fine-tuned metrics across generations
- Per-generation results and convergence/regression observations

## Acceptance criteria
- Held-out task is not represented in the training data (no leakage; verified).
- Report shows measured deltas (improvement or regression) with the eval metric, not assumed numbers.
- Negative result (regression) is reported honestly and triggers a rollback recommendation.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.

## Execution Notes (2026-06-23)
- Status moved to `blocked` after live rollout attempts did not progress to terminal completion.
- Evidence captured in `docs/artifacts/closed-loop-eval-report-v1.md`.
- Blocker: `technical` / `critical` (`T233-BLK-001`) with mitigation routed to T235 Phase 3.2/3.3 runtime completion.

## Validation Gate Update (2026-06-25)

- Status reclassified from `blocked` to `in_progress` based on merged T236 remediation evidence.
- Validation reviewer: qa-engineer
- Gate verdict: `CONDITIONAL_PASS`

### Evidence basis

- T236 produced a non-zero measured split (baseline `0.702381`, v1-ft `1`, delta `0.297619`).
- MR55 merged successfully and related pipelines are green.
- `docs/artifacts/closed-loop-eval-report-v1.md` updated with latest run context and gate rationale.

### Condition to close T233

- Complete a production-credible held-out evaluation pass that does not rely on the synthetic fallback discriminator path.
- Follow-up tracked as T237.
