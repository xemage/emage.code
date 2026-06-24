# T226: sia-executor 403 Debug Report

**Date:** 2026-06-23
**Issue:** sia-executor failing with 403 Forbidden on /nodes/register
**Status:** ✅ FIXED (403 resolved) | ⚠️ NEW BLOCKER: Task assignment mechanism missing

## Root Cause Analysis

### Issue 1: 403 Forbidden (FIXED)

**Symptom:** sia-executor exiting with "HTTP Error 403: Forbidden" on registration

**Investigation:**
1. JWT token generation verified correct (test-jwt-registration.py succeeds)
2. Orchestrator logs revealed: `"host":"orchestrator","level":"warn","msg":"origin/host not allowed"`
3. Root cause: sia-executor connecting as `http://orchestrator:8080` (Docker DNS hostname) but `orchestrator` not in ALLOWED_ORIGINS

**Solution Applied:**
```yaml
# Before (docker-compose-t226.yml)
CWSO_ALLOWED_ORIGINS: "http://localhost,http://127.0.0.1,http://localhost:8080,http://docker:8080"

# After
CWSO_ALLOWED_ORIGINS: "http://localhost,http://127.0.0.1,http://localhost:8080,http://docker:8080,http://orchestrator,http://orchestrator:8080"
```

**Result:** ✅ sia-executor now successfully registers
```
2026-06-23 09:40:32,893 - __main__ - INFO - ✓ Registered node sia-executor-1 with gateway
```

### Issue 2: Tasks Not Being Executed (NEW BLOCKER)

**Symptom:** After successful registration, sia-executor polls but never receives tasks to execute

**Root Cause:** Phase 2 execution gateway lacks task assignment/delivery mechanism

**Evidence:**
```python
# From sia-executor.py get_ready_sessions()
def get_ready_sessions(self) -> Optional[list]:
    """Poll gateway for READY sessions assigned to this node."""
    # For now, use a simple polling approach by checking task status
    # In production, this would use proper pub/sub or server-sent events
    url = f"{self.cwso_url}/rollout/status"
    ...
    # Return empty list for now; sessions would be delivered via callback
    return []  # ← Always returns empty list!
```

**Design Gap:**
- Phase 2 has execution pools (INIT/READY/RUNNING/POSTRUN) for task state tracking
- But NO mechanism to:
  1. Assign tasks to available executor nodes
  2. Deliver assigned tasks to executors (via callback, event, or query endpoint)
  3. Track executor capacity/availability

**E2E Test Result:**
```
Task Dispatch:      ✓ Created task (4382432f-51c3-4ab6-bf1d-0dc6cae9647a)
Task Status:        ✓ Queries work (status=running for 30s)
Executor Polling:   ✓ Executor running and polling
Task Assignment:    ✗ NO MECHANISM TO ASSIGN TASK TO EXECUTOR
Executor Reception: ✗ get_ready_sessions() always returns []
Task Execution:     ✗ Task never progresses (stuck in "running")
Parquet Capture:    ✗ No executor executed task, so no trajectories
Reward Attachment:  ✓ Works (uses orchestrator role)
```

## Technical Details

### Debug Path Followed

1. **JWT Validation** (✓ Working)
   - test-jwt-registration.py successfully registers from localhost
   - JWT token structure verified correct (HS256, all claims present)
   - Token generation matches golang-jwt/jwt/v5 expectations

2. **Orchestrator Auth Stack** (✓ Working)
   - CORS/origin validation working as designed
   - Orchestrator correctly rejecting unauthorized origins
   - Fix applied: Added Docker internal hostname to allowlist

3. **sia-executor Registration** (✓ Working)
   - After CORS fix, registration succeeds
   - Executor successfully registers as "sia-executor-1"
   - No auth errors after fix

4. **Task Delivery Mechanism** (✗ Not Implemented)
   - Orchestrator has no endpoint to assign tasks to executors
   - No pub/sub or event delivery system
   - Executor can only poll generic status, gets no task context
   - `get_ready_sessions()` is a placeholder, not production code

## Phase 2 Architecture Gap

### What Exists
- ✅ Task creation via `/rollout/task/submit`
- ✅ Task status tracking (INIT → RUNNING → timeout)
- ✅ Trajectory builder infrastructure (Parquet capture ready)
- ✅ Executor node registration (`/nodes/register`)
- ✅ Reward attachment via merge tools

### What's Missing
- ❌ Task assignment to executor nodes
- ❌ Task delivery mechanism (callback/event/push/pull endpoint)
- ❌ Executor capacity management
- ❌ Health check / heartbeat mechanism
- ❌ Session context delivery to executors

### Where This Fits in Roadmap

**Phase 2 (Current - v0.1.0-dev):**
- Orchestrator core + rollout gateway basics
- Task state machines (INIT/READY/RUNNING/POSTRUN)
- Trajectory capture infrastructure
- NOT designed for live executor integration

**Phase 3 (Future - T223 Harness Launcher):**
- Full executor registration + lifecycle management
- Task assignment algorithm
- Session delivery mechanism (gRPC, WebSocket, or callback)
- Executor health/capacity tracking
- Real SIA harness integration

## Path Forward

### Option 1: Implement Task Delivery for T226 PoC (3-4 hours)
Minimal implementation to unblock live testing:
- Add `/nodes/{node_id}/tasks` endpoint (GET) to fetch assigned tasks
- Implement task assignment logic in orchestrator
- Update sia-executor to query this endpoint
- Expected result: Full E2E with mock SIA execution

### Option 2: Defer to T223 Production Implementation (Recommended)
Keep current state:
- Mock execution mode works (validates dispatch/reward flow)
- sia-executor template available for reference
- Document task assignment design for T223
- Focus T223 work on production harness + executor integration

### Option 3: Use Direct Task Status Query (Quick Hack)
Modify sia-executor to:
- Query `/rollout/task/{task_id}` directly (requires task discovery mechanism)
- If status=RUNNING, assume task is for this executor
- Execute immediately
- Limitation: All tasks would be executed by all executors (race condition)

## Files Modified

- `deploy/docker-compose-t226.yml`: Added orchestrator hostname to ALLOWED_ORIGINS
- `implementation/scripts/sia-executor.py`: Already has placeholder for task delivery

## Testing & Validation

**Test 1: JWT Generation** (✓ Pass)
```bash
python3 test-jwt-registration.py
# Result: Registration succeeds, JWT valid
```

**Test 2: sia-executor Registration** (✓ Pass)
```bash
docker compose logs sia-executor | grep "Registered"
# Result: ✓ Registered node sia-executor-1 with gateway
```

**Test 3: E2E with Mock Execution** (✓ Pass)
```bash
dispatch-test-sia.py --mock-execution true
# dispatch ✓, eval ✓, reward ✓, parquet ✗
```

**Test 4: E2E with Real Execution** (✗ Fail)
```bash
dispatch-test-sia.py  # Without mock mode
# dispatch ✓, polling ✓, task stuck in running, no executor engagement
```

## Recommendations

1. **For T226 Sprint Closure:**
   - Accept current state: dispatch + reward attachment working, real execution deferred
   - Mark task assignment as technical debt for T223
   - Publish sia-executor template as reference implementation
   - Use mock execution mode for PoC E2E validation

2. **For T223 Production Work:**
   - Implement task assignment + delivery mechanism
   - Add executor health/capacity tracking
   - Real SIA harness integration
   - Comprehensive E2E with LLM integration

3. **For Future Phases:**
   - Consider async delivery (gRPC streaming, WebSocket)
   - Add executor resource limits (GPU, memory)
   - Implement dynamic load balancing
   - Multi-executor coordination

## Summary

**Achieved:**
- ✅ Fixed 403 Forbidden (CORS/origin issue)
- ✅ sia-executor successfully registers
- ✅ Dispatch and reward attachment working
- ✅ Mock execution mode validates E2E flow
- ✅ Identified and documented Phase 2 architectural gap

**Blocked:**
- ❌ Real task execution (requires task assignment mechanism)
- ❌ Parquet trajectory capture from real execution
- ❌ Live SIA integration

**Next Phase:**
Task assignment + executor delivery mechanism implementation in T223

---

**Conclusion:** The 403 issue was a misconfiguration (CORS allowlist), not a fundamental problem. The real blocker is the missing task assignment mechanism in Phase 2 - that's a design decision, not a bug.

