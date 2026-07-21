# Checkpoint v3-007: T235/T231 Parallel Workstream Kickoff

**Phase:** Phase 3 Implementation Kickoff (Production Executor & Fine-tuning)
**Session:** Parallel workstream initialization
**Date:** 2026-06-23
**Token usage:** 28k / 200k (86% remaining)

## Summary

Completed T226 infrastructure debugging and sprint closure. Now activating two parallel workstreams:

1. **T235 Phase 3.1** — Task assignment algorithm (orchestrator-side)
2. **T231** — Model fine-tuning & HAL redeploy

Both ready to start immediately with detailed implementation guides.

## Completed This Cycle

### T226 Sprint Closure
- ✅ CORS fix applied (orchestrator hostname in allowlist)
- ✅ E2E mock execution validated (dispatch → evaluate → reward → Parquet)
- ✅ sia-executor registration working
- ✅ Role-based authorization confirmed (orchestrator role for merge_concurrent_results)
- ✅ Design gap documented (task assignment deferred to Phase 3.1)
- ✅ sia-executor template published with POC-DEBT markers
- ✅ 6 commits: c2c2fe3...ae4e313

### Artifacts Created
1. **t226-sia-executor-403-debug-report-v1.md**
   - Root cause analysis (CORS origin allowlist)
   - Phase 2 design gap analysis
   - Path forward options

2. **t235-phase3.1-task-assignment-design-v1.md** 🆕
   - Round-robin algorithm specification
   - Node registry implementation (orchestrator changes)
   - sia-executor integration (polling changes)
   - Phase 3.1a/3.1b/3.1c checklist
   - API endpoints (register, GET /tasks, heartbeat)
   - Risk mitigation and success criteria

3. **t231-fine-tuning-implementation-guide-v1.md** 🆕
   - T230 dataset prerequisites check
   - LoRA fine-tuning setup (5 implementation scripts)
   - HAL redeploy procedure
   - Rollback documentation
   - Testing & validation
   - Hyperparameter log for reproducibility

## Active Task Status

```
T226: Infrastructure deployed ............................ ✅ DONE (moved to completed)
T228: Phase 2 live integration ........................... ✅ DONE (moved to completed)

T230: Trainer bridge dataset ............................. ✅ DONE
  └─ Output: Parquet trajectories + trainer_bridge.py functions

T235: SIA executor production integration ................ 🔄 IN_PROGRESS
  ├─ Phase 3.1: Task assignment (ready to start)
  ├─ Phase 3.2: Real executor delivery (blocked by 3.1)
  ├─ Phase 3.3: Real LLM execution (blocked by 3.2)
  └─ Phase 3.4: Full E2E (blocked by 3.3)
  Owner: backend-developer
  Estimated: 2-3 weeks total (3.1: 3-4 days)

T231: Fine-tuning & HAL redeploy ......................... 🔄 IN_PROGRESS
  Depends on: T230 ✅
  Unblocks: T233 → T234
  Owner: backend-developer
  Estimated: 3-5 days
  Critical path: T231 → T233 (eval delta) → T234 (telemetry)

T233: Closed-loop eval (blocked by T231) ................ ⏳ WAITING (T231→3.1)
T234: Telemetry & cost (blocked by T233) ............... ⏳ WAITING (T233)
```

## Architecture Overview

```
                    Development
                         |
         +-------+--------+--------+-------+
         |       |                 |       |
       T235    T231              T232    T236
      Executor Fine-tune         (Eval)  (Improvements)
         |       |                 |
    Phase 3.1   3-5 days          T233
      Assign      |            Closed-loop
    (3-4 days)    +-----→        (blocked)
         |              |
    Phase 3.2      T234 Cost+Telemetry
      Delivery    (blocked)
         |
    Phase 3.3
    Real LLM
         |
    Phase 3.4
    E2E Validation

Critical path: T231 (3-5d) → T233 (2d) → T234 (1d) = ~8 days total
Parallel path: T235 Phase 3.1 (3-4d) independent
```

## Implementation Guides Ready

### T235 Phase 3.1 Design
**File:** `docs/artifacts/t235-phase3.1-task-assignment-design-v1.md`

**Key decisions:**
- Round-robin task assignment (simple, sufficient for PoC)
- Node registry with `sync.RWMutex` for thread-safety
- New endpoint: `GET /nodes/{node_id}/tasks` (worker role)
- Heartbeat mechanism for node health
- Three sub-phases: 3.1a (registry), 3.1b (executor), 3.1c (testing)

**CWSO changes required:**
- `node_registry.go` — Node tracking + round-robin selection
- `task_assignment.go` — Task-to-node mapping
- `gateway.go` — Call assignment on READY transition
- `api_handler.go` — Add /nodes/{node_id}/tasks endpoint

**sia-executor changes:**
- Replace `get_ready_sessions()` placeholder (now returns real tasks)
- Add heartbeat mechanism
- Deregister cleanly on shutdown

### T231 Fine-tuning Guide
**File:** `docs/artifacts/t231-fine-tuning-implementation-guide-v1.md`

**Key decisions:**
- LoRA fine-tuning recommended (faster, lower resources than full)
- 5 implementation scripts (setup, lora, merge, deploy, rollback)
- Hyperparameters logged for reproducibility (seed=42)
- Rollback procedure documented
- HAL redeploy via docker-compose or new port

**Scripts to create:**
1. `fine-tune-setup.py` — Load T230 dataset + validation
2. `fine-tune-lora.py` — LoRA training loop
3. `merge-lora.py` — Adapter merge to full weights
4. Redeploy via HAL config update
5. Rollback doc: `docs/releases/model-v1-fine-tune-rollback.md`

## Parallel Workstream Sequencing

### Workstream A: T235 Phase 3.1 Task Assignment
**Start immediately** — No external dependencies
**Steps:**
1. backend-developer explores CWSO orchestrator codebase
2. Design node registry + round-robin algorithm
3. Implement CWSO changes (3 files)
4. Update sia-executor.py polling
5. Integration test + E2E validation
**Blocker:** None
**Unblocks:** Phase 3.2 (executor delivery)

### Workstream B: T231 Fine-tuning
**Start immediately** — Depends only on T230 ✅
**Steps:**
1. Verify T230 dataset output format + structure
2. Run fine-tune-setup.py validation
3. Launch LoRA training (2-3 hours wall time)
4. Merge adapter to full weights
5. Deploy behind HAL
6. Test inference + rollback
**Blocker:** None
**Unblocks:** T233 (closed-loop eval)

**Timeline:** Both can run in parallel (separate engineers recommended)

## Key Decisions

### Decision 1: Parallel execution
- ✅ T235 and T231 are independent (no cross-dependencies)
- ✅ Can run in parallel to maximize throughput
- ✅ T235 Phase 3.1 ready to start immediately
- ✅ T231 ready to start immediately (T230 ✅ done)

### Decision 2: Task assignment algorithm
- ✅ Round-robin (simple, sufficient for PoC)
- ⏸ Load balancing deferred to Phase 4
- ⏸ Priority queues deferred to Phase 4

### Decision 3: Fine-tuning approach
- ✅ LoRA (faster, lower resources)
- ⏸ Full model fine-tuning deferred to Phase 4 (if needed)

## Validation Gates Passed

- ✅ **Architecture Gate:** T226 infrastructure stable
- ✅ **Security Gate:** JWT role-based auth working
- ✅ **Integration Gate:** Mock E2E successful
- ⏳ **Implementation Gate:** Awaiting T235 Phase 3.1 + T231 start

## Technical References

### CWSO Orchestrator Code
- Main: `/home/emage/Code/emage/CWSO/orchestrator/`
- Rollout gateway: `/home/emage/Code/emage/CWSO/orchestrator/internal/rollout/`
- Key files: api_handler.go, gateway.go, gateway_session.go

### sia-executor Template
- File: `implementation/scripts/sia-executor.py`
- POC-DEBT tags: get_ready_sessions() (line TBD), execute_session() (line TBD)

### E2E Test Harness
- File: `implementation/scripts/dispatch-test-sia.py`
- Role parameter working: dispatch (worker), attach_reward (orchestrator)
- Mock execution mode: --mock-execution true

### T230 Trainer Bridge
- File: `implementation/adapters/sia-target/trainer_bridge.py`
- Functions: read_trajectories(), build_grpo_dataset(), build_sft_dataset()
- Dataset schema: workspace_uuid, session_id, token_ids, logprobs, rewards

## Token Budget Status

- **Used this cycle:** ~28k tokens
- **Remaining:** ~172k tokens (86%)
- **Phase budget remaining:** ~132k tokens (Implementation ~120k allocated)
- **Status:** ✅ On track

## Next Phase: Phase 3.2+

### T235 Phase 3.2: Executor Delivery
After Phase 3.1 ✓:
- Remove get_ready_sessions() placeholder mock
- Wire real task polling
- Add retry/backoff logic
- Test with dispatch-test-sia.py

### T235 Phase 3.3: Real LLM Execution
After Phase 3.2 ✓:
- Replace execute_session() 2s mock delay
- Wire to SIA harness adapter
- Real code generation + step tracing
- Trajectory capture

### T235 Phase 3.4: Full E2E
After Phase 3.3 ✓:
- dispatch-test-sia.py without --mock-execution
- Task reaches completion state
- Parquet files captured with real trajectories
- Reward attachment with real data

### T233: Closed-Loop Evaluation
After T231 ✓:
- Run SIA harness with fine-tuned model
- Compare reward scores vs T225 baseline
- Measure improvement delta
- Unblock T234 (cost/latency telemetry)

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Task assignment algorithm too complex | Low | Start simple (round-robin), iterate later |
| Node registry concurrency issues | Medium | Use sync.RWMutex, test with multi-executor |
| LoRA training diverges from base | Medium | Validate with inference tests, rollback if needed |
| HAL deployment breaks | High | Rollback procedure documented, test in dev first |
| Fine-tuning dataset too small | Low | ~50 examples sufficient for PoC validation |

## Handoff Information

For next agent/orchestrator:

1. **T235 Phase 3.1** is ready to start
   - Design: `docs/artifacts/t235-phase3.1-task-assignment-design-v1.md`
   - CWSO code location: `/home/emage/Code/emage/CWSO/orchestrator/internal/rollout/`
   - Executor code: `implementation/scripts/sia-executor.py`
   - E2E test: `implementation/scripts/dispatch-test-sia.py`

2. **T231** is ready to start
   - Guide: `docs/artifacts/t231-fine-tuning-implementation-guide-v1.md`
   - T230 dataset: Ready in `/tmp/t226-parquet-store`
   - Scripts to create: 5 Python scripts (detailed in guide)
   - HAL location: TBD (explore docker-compose or vLLM config)

3. **Both can run in parallel** (separate engineers recommended)

4. **Token budget:** 172k remaining (86% of 200k total)

## Previous Checkpoints

- checkpoint-001-gitlab-bootstrap.md
- checkpoint-001-planning-tdd-skills.md
- checkpoint-002-ci-templates-release-wiki.md
- checkpoint-003-tests.md
- checkpoint-004-benchmark-expansion.md
- checkpoint-005-v3-planning-approved.md
- checkpoint-v3-002-implementation-readiness.md
- checkpoint-v3-003-post-release-pilot-cycle.md
- checkpoint-v3-004-pilot-switch-validation.md
- checkpoint-v3-005-promotion-readiness.md
- checkpoint-v3-006-release-ready-execution.md

---

**Status:** ✅ Parallel workstreams ready to activate

**Recommended next actions:**
1. Delegate T235 Phase 3.1 to backend-developer (CWSO orchestrator work)
2. Delegate T231 to backend-developer (fine-tuning work)
3. Run in parallel (2-3 weeks expected for both)
4. Reconvene at Phase 3.2 / T233 validation gates
