# T228 Infrastructure Unblocking Summary

**Date:** 2026-06-23
**Status:** Phase 2 Infrastructure Gaps Identified & Partially Resolved
**Evidence:** Diagnostic JSON + Deployment Configuration Fix

---

## Problem Statement

The SIA dispatch test (`dispatch-test-sia.py`) was successfully dispatching tasks to CWSO's rollout API but tasks remained in `running` state indefinitely. Diagnostic evidence revealed the Phase 2 execution chain was incomplete: **no executor nodes were registered** because the **execution gateway was disabled by default** in the orchestrator configuration.

## Root Cause

CWSO v3 orchestrator has three Phase 2 feature flags that default to `false`:

| Feature | Flag | Purpose | Was Disabled |
|---------|------|---------|:----------:|
| **Execution Gateway** | `CWSO_ROLLOUT_GATEWAY_STAGING_ENABLED` | Creates INIT/READY/RUNNING/POSTRUN session pools; routes tasks to executors | ✅ Yes |
| **Evaluator Registry** | `CWSO_ROLLOUT_EVALUATOR_REGISTRY_ENABLED` | Registers post-run evaluation callbacks | ✅ Yes |
| **Trajectory Builder** | `CWSO_ROLLOUT_TRAJECTORY_BUILDER_ENABLED` | Captures LLM calls as Parquet files | ✅ Yes |

**Impact:**
- Tasks created successfully via `POST /rollout/task/submit` ✅
- Tasks assigned to sessions ✅
- **Sessions never executed** ❌ (no gateway to route them)
- **Tasks stuck in `running` indefinitely** ❌ (no executor, no callback)
- **Zero registered nodes** (0/0) ❌ (gateway disabled)
- **Zero partial results / trajectories / parquet files** ❌ (no execution)

## Evidence

### Diagnostic Signals Before Fix

```json
{
  "blocker_assessment": "incomplete_phase2_runtime",
  "missing_progression_signals": [
    "task_running_without_partial_results",
    "task_running_without_trajectories",
    "task_running_without_parquet_capture",
    "no_registered_rollout_nodes"
  ],
  "signals": {
    "registered_nodes": 0,
    "running_sessions": 6,
    "task_status": "running",
    "has_merge_concurrent_results": true,
    "parquet_file_count_for_session": 0
  }
}
```

### Orchestrator Startup Logs After Fix

```
cwso-orchestrator | rollout gateway staging enabled (INIT/READY/RUNNING/POSTRUN pools)
cwso-orchestrator | rollout evaluator registry enabled
cwso-orchestrator | rollout trajectory builder v2 enabled
cwso-orchestrator | rollout Polar REST API enabled (/rollout/*)
```

## Fix Applied

### 1. Enable Gateway in Docker Compose

**File:** `deploy/docker-compose-t226.yml`

```yaml
orchestrator:
  environment:
    # Phase 2: Execution gateway & trajectory builder (T146, T149)
    CWSO_ROLLOUT_GATEWAY_STAGING_ENABLED: "${CWSO_ROLLOUT_GATEWAY_STAGING_ENABLED:-true}"
    CWSO_ROLLOUT_EVALUATOR_REGISTRY_ENABLED: "${CWSO_ROLLOUT_EVALUATOR_REGISTRY_ENABLED:-true}"
    CWSO_ROLLOUT_TRAJECTORY_BUILDER_ENABLED: "${CWSO_ROLLOUT_TRAJECTORY_BUILDER_ENABLED:-true}"
    CWSO_ROLLOUT_TRAJECTORY_BUILDER_STRATEGY: "${CWSO_ROLLOUT_TRAJECTORY_BUILDER_STRATEGY:-per_request}"
```

### 2. Document Phase 2 Feature Flags

**File:** `deploy/t226-phase2.env`

```bash
# ==============================================================================
# Phase 2: Execution Gateway & Trajectory Builder
# ==============================================================================

# Enable session execution gateway (INIT/READY/RUNNING/POSTRUN pools)
CWSO_ROLLOUT_GATEWAY_STAGING_ENABLED=true

# Enable post-run evaluator registry (required for rewards + evaluation)
CWSO_ROLLOUT_EVALUATOR_REGISTRY_ENABLED=true

# Enable trajectory builder for Parquet capture (required for Phase 4 data collection)
CWSO_ROLLOUT_TRAJECTORY_BUILDER_ENABLED=true

# Trajectory builder strategy: "per_request" or "prefix_merge" (default: prefix_merge)
CWSO_ROLLOUT_TRAJECTORY_BUILDER_STRATEGY=per_request
```

### 3. Create Minimal Executor Service (PoC)

**File:** `implementation/scripts/sia-executor.py`

A Python service that:
- Registers as an executor node with the gateway
- Receives READY sessions from the gateway
- Simulates SIA execution
- Reports partial_results back to gateway
- Captures trajectories for Parquet

This is a PoC to unblock testing while the full T223 harness launcher is being implemented.

**Added to docker-compose-t226.yml:**
```yaml
sia-executor:
  image: python:3.11-slim
  container_name: cwso-sia-executor
  working_dir: /workspace
  entrypoint: /bin/bash
  command:
    - -c
    - |
      JWT_SECRET=$$(cat /run/secrets/jwt_secret)
      python3 sia-executor.py \
        --cwso-url http://orchestrator:8080 \
        --node-id sia-executor-1 \
        --jwt-secret "$$JWT_SECRET" \
        --mock-delay 1.5 \
        --poll-interval 1.0
  depends_on:
    orchestrator:
      condition: service_healthy
```

## Expected Outcomes After Fix

### Immediate (Gateway Enabled)

With `CWSO_ROLLOUT_GATEWAY_STAGING_ENABLED=true`:
- ✅ Orchestrator creates gateway on startup
- ✅ `registered_nodes` > 0 (when executor nodes connect)
- ✅ Task lifecycle advances: QUEUED → READY → RUNNING → COMPLETED
- ✅ Evaluation callbacks can be invoked

### With Executor Registered

Once executor service connects:
- ✅ Sessions routed to READY pool
- ✅ Executor receives READY sessions
- ✅ Sessions execute and report `partial_results`
- ✅ Trajectories written to Parquet store

### With Trajectory Builder Enabled

- ✅ LLM call traces captured
- ✅ Parquet files written to `/tmp/t226-parquet-store`
- ✅ Phase 4 merge engine can consume trajectory data

## Remaining Work

### Level 1: Executor Service Integration
- [ ] Test executor node registration with gateway
- [ ] Verify READY session delivery to executor
- [ ] Confirm partial_results reporting works
- [ ] Validate Parquet trajectory capture

### Level 2: Full T223 Harness Implementation
- [ ] Replace mock executor with real SIA harness
- [ ] Integrate actual LLM calls (OpenAI, etc.)
- [ ] Support full SIA target ecosystem
- [ ] Production hardening (security, error handling, monitoring)

### Level 3: Role Authorization Fix
- **Issue:** Reward attachment fails with "role worker may not invoke merge_concurrent_results"
- **Options:**
  1. Use orchestrator role for merge operations
  2. Implement role-based operation dispatch in executor
  3. Update CWSO MCP tool authorization rules

### Level 4: Testing & Validation
- [ ] E2E test: dispatch → execute → evaluate → parquet capture
- [ ] Load test: multiple concurrent sessions
- [ ] Failure scenarios: executor crash, timeout, invalid task spec
- [ ] Parquet schema validation

## Deployment Steps

To deploy the infrastructure fix on a clean system:

```bash
# 1. Navigate to project root
cd /home/emage/Code/emage/emage.code

# 2. Source environment variables
source deploy/t226-phase2.env

# 3. Stop old deployment (if running)
docker compose -f deploy/docker-compose-t226.yml down

# 4. Start services with fixed configuration
docker compose -f deploy/docker-compose-t226.yml up -d

# 5. Verify gateway is enabled
sleep 5
docker compose -f deploy/docker-compose-t226.yml logs orchestrator | grep "gateway staging enabled"

# 6. Verify executor registered (once sia-executor service completes startup)
sleep 5
docker compose -f deploy/docker-compose-t226.yml logs sia-executor | grep "Registered node"

# 7. Re-run dispatch test
python3 implementation/scripts/dispatch-test-sia.py \
  --rollout-timeout 30 \
  --diagnostic-output t228-diagnostics-post-fix.json
```

## References

- **Diagnosis Artifact:** `docs/artifacts/infrastructure-phase2-diagnosis-v1.md`
- **Dispatch Test Script:** `implementation/scripts/dispatch-test-sia.py`
- **Executor Service:** `implementation/scripts/sia-executor.py`
- **Configuration Files:**
  - `deploy/docker-compose-t226.yml`
  - `deploy/t226-phase2.env`
- **CWSO Source:**
  - `orchestrator/internal/config/config.go` (feature flags)
  - `orchestrator/internal/server/server.go` (gateway wiring)
  - `orchestrator/internal/rollout/api_handler.go` (API endpoints)

## Summary

**What Was Broken:** Three critical Phase 2 features were disabled by default, preventing task execution and trajectory capture.

**Why It Happened:** CWSO defaults are conservative (features disabled), and deployment config didn't enable them.

**What We Fixed:** Updated deployment to enable `CWSO_ROLLOUT_GATEWAY_STAGING_ENABLED`, `CWSO_ROLLOUT_EVALUATOR_REGISTRY_ENABLED`, and `CWSO_ROLLOUT_TRAJECTORY_BUILDER_ENABLED`.

**How to Validate:** Orchestrator logs show "rollout gateway staging enabled" on startup; executor node successfully registers; tasks progress from RUNNING to COMPLETED; Parquet files are written.

**Next Steps:** Integrate real executor (T223), validate E2E flow, resolve role authorization for merge operations.
