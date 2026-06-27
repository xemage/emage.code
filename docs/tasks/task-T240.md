# Task T240 - Deploy Fine-Tuned Model to Production Rollout Path

**Status:** pending
**Owner:** devops-engineer / backend-developer
**Priority:** P0
**Depends on:** T233 (gate rerun PASS ✅), T238 (held-out batch ✅), T239 (aggregation ✅)
**Based on:** plan-011-t237-t233-production-credible-eval.md

## Objective
Deploy the fine-tuned v1-ft model to the production rollout service path, replacing or augmenting the baseline model endpoint based on T233 QA gate evidence and promotion recommendation.

## Inputs
- T233 closed-loop evaluation report (v2): `docs/artifacts/closed-loop-eval-report-v2.md` (PASS verdict)
- T238 held-out batch metrics: `docs/artifacts/t238-metrics-final.json` (5/5 baseline, 5/5 fine-tuned)
- T237 discriminator removal validation: MR!58 merged, harness updated
- Current production deployment config (deployment/docker-compose-t226.yml or equivalent)
- Fine-tuned model artifact path: implementation/models/v1-ft or registry reference

## Expected outputs
- Updated deployment configuration with v1-ft model active (or switchable via feature flag)
- Deployment log/validation confirming model endpoint healthy
- Production telemetry baseline established for T241 (monitoring)
- Updated docs/artifacts/t240-deployment-report-v1.md with deployment details
- Updated docs/tasks/task-T240.md with completion evidence

## Acceptance criteria
1. Fine-tuned model is accessible via production rollout service endpoint
2. Model responds to dispatch requests with zero errors over 5-minute validation window
3. Rollout status transitions complete without timeout
4. Telemetry collection active for v1-ft model path
5. Rollback plan documented and tested (ability to switch back to baseline if needed)
6. Deployment report signed off by devops-engineer

## Deployment strategy
- **Option A (Recommended):** Deploy v1-ft model as primary; keep baseline available as fallback
- **Option B (Conservative):** Deploy v1-ft with feature flag (default OFF); enable after monitoring window
- **Option C (Parallel):** Deploy both models; route small % of traffic to v1-ft for real-world validation

## Blocker protocol
If blocked, report blocker type + severity with one proposed mitigation.

## Execution Notes (TBD)
To be updated during T240 execution.
