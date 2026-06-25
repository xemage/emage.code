# Task T237 - Replace Synthetic Discriminator with Real Quality Discrimination

**Status:** pending
**Owner:** backend-developer
**Priority:** P0
**Depends on:** T233, T236 ✅
**Created:** 2026-06-25
**Origin:** Follow-up from T236 synthetic discriminator validation

## Objective

Remove the test-only synthetic discriminator path from held-out evaluation scoring and establish production-credible baseline vs fine-tuned discrimination using only real model output quality through the evaluator contract.

## Background

T236 unblocked end-to-end discriminative scoring with a documented test-only fallback in the harness output adaptation path. That result is acceptable for pipeline validation but not sufficient for production readiness decisions.

## Scope

1. Replace synthetic fallback discrimination in `implementation/adapters/sia-target/harness-entrypoint.py` with real-output-only evaluation behavior.
2. Ensure the evaluator receives schema-valid `solution.json` generated from actual model output, not model-label-conditioned synthetic shaping.
3. Run multi-generation held-out baseline vs fine-tuned evaluations and capture stable deltas.
4. Update `docs/artifacts/closed-loop-eval-report-v1.md` with production-credible evidence and promotion guidance.

## Expected Outputs

- Harness path update removing synthetic discriminator behavior from scoring-critical flow
- Validation tests covering real-output scoring path
- Updated held-out report with >= 5 completed generations per group and measured deltas
- Explicit gate recommendation for T233 closeout (PASS/CONDITIONAL_PASS/FAIL)

## Acceptance Criteria

1. No model-label-dependent synthetic scoring logic remains in production scoring path.
2. Held-out evaluation uses real model outputs and evaluator metrics only.
3. At least 5 completed baseline and 5 completed fine-tuned runs are captured with reported deltas.
4. Report includes stability summary (mean/median delta and variance) and clear promotion/rollback recommendation.
5. QA validation gate for T233 can be re-run with production-credible evidence.

## Risks

- Real model output may be intermittently non-schema-compliant, causing evaluator failures.
- Upstream API availability and relay connectivity can create noisy run outcomes.

## Mitigations

- Add strict output-contract validation with explicit retry and failure labeling.
- Run evaluations in bounded batches and keep full per-run artifacts for auditability.
