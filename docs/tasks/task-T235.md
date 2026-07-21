# Task T235 - SIA Executor Production Integration

**Status:** done
**Owner:** backend-developer
**Priority:** P1
**Depends on:** T226 ✅, T228 ✅
**Created:** 2026-06-23
**Context checkpoint:** docs/artifacts/t226-sia-executor-403-debug-report-v1.md

## Phase 3.1 ✅ — Task Assignment Mechanism (merged 2026-06-23)
## Phase 3.2 ✅ — Executor Delivery (merged 2026-06-23)
## Phase 3.3 ✅ — Real Harness Wiring (merged 2026-06-24)

**Phase 3.3 Evidence (2026-06-24):**
- Executor container patched with `/implementation` volume mount and `PYTHONPATH=/implementation:/adapters`
- `implementation/sia/__init__.py` and `implementation/sia/util.py` stub created to satisfy harness import
- `docker exec cwso-sia-executor cat /tmp/t233-eval-baseline/output.json` shows `status=success`
- Executor logs confirm: "SIA agent execution completed successfully" for v3 baseline and fine-tuned runs
- 19/19 Python unit tests pass (`tests/unit/test_sia_executor_phase32.py`)
- MR48 CI green (#324 branch + #325 MR pipeline both success) and merged to develop

**Phase 3.4 status:** Completed via downstream T236 remediation evidence and merged runtime path validation

## Completion Update (2026-06-25)

- Task status transitioned from `in_review` to `done` after T236 delivered non-zero discriminative reward signal over the integrated executor+harness path.
- Executor/runtime path remains green in merged CI lineage (MR48 for Phase 3.3 and MR55 for discriminative scoring follow-up).
- Remaining production-hardening work has been split into follow-up task T237.

## Objective

Implement the production SIA executor integration for CWSO Phase 3. T226 validated the E2E dispatch → reward flow in mock execution mode and established the sia-executor template. This task bridges the gap: implement task assignment, executor delivery mechanism, real LLM-based SIA execution, and full end-to-end with Parquet trajectory capture.

## Background

T226 Phase 2 infrastructure is complete. The following was confirmed working:
- ✅ Dispatch via `/rollout/task/submit`
- ✅ Executor node registration via `/nodes/register` (CORS fix applied)
- ✅ Role-based JWT authorization (worker vs orchestrator)
- ✅ Reward attachment via `merge_concurrent_results`
- ✅ Mock execution mode (E2E flow validated)

Phase 2 has a design gap that defers to this task:
- ❌ Task assignment algorithm (no mechanism to assign submitted tasks to registered executors)
- ❌ Task delivery mechanism (executor has no way to receive tasks)
- ❌ Real LLM-based SIA execution in executor
- ❌ End-to-end Parquet capture from real executor output

## Inputs

- `implementation/scripts/sia-executor.py` — PoC executor reference template (T226)
- `implementation/scripts/dispatch-test-sia.py` — E2E test harness with mock mode (T226)
- `deploy/docker-compose-t226.yml` — Current infrastructure baseline (T226)
- `docs/artifacts/t226-sia-executor-403-debug-report-v1.md` — Phase 2 design gap analysis
- CWSO orchestrator source at `/home/emage/Code/emage/CWSO` — internal API reference
- `docs/artifacts/cwso-mcp-contract-v1.md` — MCP contract (T201)
- `docs/artifacts/sia-target-adapter-v1.md` — SIA target adapter reference (T220)

## Work Items

### Phase 3.1: Task Assignment Mechanism (backend-developer)

**Goal:** Enable the orchestrator to route submitted tasks to registered executor nodes.

**Scope:**
- Add `/nodes/{node_id}/tasks` polling endpoint to CWSO orchestrator OR implement a push callback mechanism
- Implement task assignment algorithm (round-robin or least-loaded for PoC)
- When a task enters RUNNING state, assign it to an available registered node
- Track assignment in execution pool state machine (INIT → READY → RUNNING → POSTRUN)

**Acceptance criteria:**
- POST `/rollout/task/submit` creates task AND assigns to an available executor within 1 poll cycle
- GET `/nodes/{node_id}/tasks` returns assigned tasks for the requesting executor
- Task assignment is logged in orchestrator at info level
- If no executors available, task stays in INIT and a warning is logged (no silent drop)

### Phase 3.2: Executor Delivery in sia-executor.py (backend-developer)

**Goal:** Update `sia-executor.py` to actively receive and process tasks.

**Scope:**
- Replace placeholder `get_ready_sessions()` (currently returns `[]`) with actual task fetch from `/nodes/{node_id}/tasks`
- Add retry/backoff for transient network errors
- Add heartbeat to `/nodes/{node_id}/heartbeat` to signal executor liveness
- Report result via `/rollout/session/{session_id}/result` after execution

**Acceptance criteria:**
- `get_ready_sessions()` returns real tasks from the orchestrator
- Executor processes assigned task within 2 poll cycles of dispatch
- Heartbeat sent every 30s; orchestrator deregisters unresponsive nodes after 90s

### Phase 3.3: Real LLM-Based SIA Execution (backend-developer)

**Goal:** Replace mock delay in `execute_session()` with real SIA harness invocation.

**Scope:**
- Wire `execute_session()` to call the SIA harness adapter (T220: `implementation/adapters/sia-target/`)
- Pass task_spec (description, workspace_id, max_steps) to harness
- Capture harness output: generated code, evaluation results, trace
- Map harness output → `partial_results` + `trajectories` for result reporting

**Reference:**
- `implementation/adapters/sia-target/harness-entrypoint.py` — real harness execution path
- `implementation/adapters/sia-target/reward_attachment.py` — reward flow reference (T224)
- T223 test report: `docs/artifacts/test-report-t223-v1.md` — expected output format

**Acceptance criteria:**
- `execute_session()` invokes real SIA harness (not sleep delay)
- Results include actual generated code or error artifact from harness
- Execution completes within configurable timeout (default 120s)
- Partial results and trajectories populated with real harness output

### Phase 3.4: Full End-to-End with Parquet Capture (qa-engineer)

**Goal:** Validate full E2E flow from dispatch to Parquet trajectory storage.

**Scope:**
- Run `dispatch-test-sia.py` without `--mock-execution` flag
- Confirm task progresses: submitted → running → completed
- Confirm Parquet file written to `/tmp/t226-parquet-store`
- Confirm reward attachment succeeds with real evaluation data
- Update `dispatch-test-sia.py` diagnostics to reflect real execution signals

**Acceptance criteria:**
- Task status transitions from `running` to `completed` (not timeout)
- At least one Parquet file found matching the session ID
- Reward attachment returns success (not RPC error)
- `dispatch-test-sia.py` reports `✓` for all four phases (dispatch, eval, reward, parquet)

## Expected Outputs

- Updated `implementation/scripts/sia-executor.py` with real task delivery + LLM execution
- CWSO orchestrator changes: task assignment endpoint + algorithm (in `/home/emage/Code/emage/CWSO`)
- Updated `deploy/docker-compose-t226.yml` (if new env vars needed)
- E2E test run log showing all four phases passing (no mock mode)
- Updated `dispatch-test-sia.py` test harness confirming real execution
- At least one Parquet trajectory file captured from a real SIA run

## Acceptance Criteria

1. `dispatch-test-sia.py` without `--mock-execution` completes without timeout
2. Task status reaches `completed` (not `timeout` or `running`)
3. sia-executor processes assigned tasks from the orchestrator delivery mechanism
4. Parquet file(s) present in parquet store after E2E run
5. Reward attachment succeeds with real evaluation score (not RPC error)
6. No mocks in critical path; all executor-side logic uses real SIA harness calls

## Constraints

- **Scope boundary:** This task owns executor-side changes and task assignment API only. Do NOT change the reward shaping logic (T225), trainer bridge (T230), or release gate (T232).
- **Infrastructure boundary:** Changes to CWSO orchestrator source are in `/home/emage/Code/emage/CWSO` (separate repo). Infrastructure-as-code changes stay in `deploy/`.
- **PoC acceptable:** Phase 3.1 task assignment can be simple round-robin. No complex scheduling required.
- **Token budget:** 120k (implementation phase)

## Blocker Protocol

Report blockers with type, severity, and one proposed mitigation:
- `technical / critical` — task assignment API not extensible → propose alternative delivery mechanism (webhook callback)
- `dependency / major` — CWSO orchestrator doesn't expose task query endpoint → implement pull-based polling with full task spec in status response
- `unclear_requirements / major` → escalate to orchestrator

## Reference Commits (T226)

- `d748a62` — fix(docker-compose): add orchestrator hostname to ALLOWED_ORIGINS
- `174f0fa` — feat(dispatch-test-sia): add mock execution mode for E2E testing
- `c2c2fe3` — fix(dispatch-test-sia): use orchestrator role for reward attachment
