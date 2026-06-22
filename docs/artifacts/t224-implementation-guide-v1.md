# T224 Implementation Guide — Reward Attachment via Merge

**Version**: 1.0  
**Date**: 2026-06-22  
**Status**: Ready for implementation  
**Owner**: Backend Developer  
**Dependencies**: T223 ✅, T212 ✅, T203 (deploy-pending)

---

## Overview

T224 implements reward attachment in the CWSO merge orchestration layer. When a SIA generation completes via the harness launcher (T223), the evaluator produces a `results.json` with `overall_score` and `passed` fields. T224 sends this reward signal to the CWSO merge engine via `merge_concurrent_results`, which attaches the evaluation result to the trajectory record captured in the Parquet store.

**Key Concept**: 
- Harness launcher runs SIA generation → evaluator produces results
- T224 calls `merge_concurrent_results(rollout_session_id, evaluation_reward)`
- CWSO merge engine embeds reward in trajectory record
- Parquet store stores reward with trajectory for future training

---

## Architecture Overview

### T223 Harness Launcher Flow (Existing)
```
┌─────────────────────────────────────────────────────────────┐
│ CWSO Harness Launcher (orchestrator package)                │
│                                                             │
│ dispatch_concurrent_jobs()                                  │
│   ↓ yields DispatchResult {                                │
│       workspace_uuid: str                                   │
│       rollout_session_id: str  ← links trajectory            │
│       completed: Event                                      │
│   }                                                         │
│   ↓                                                         │
│ Wait for job completion                                     │
│   ↓                                                         │
│ Read job outputs: results.json {                           │
│     overall_score: float [0, 1]                            │
│     passed: bool                                           │
│     ...diagnostics...                                      │
│ }                                                           │
│   ↓                                                         │
│ [T224: Attach reward here] ← NEW STEP                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### T224 Reward Attachment Flow (New)
```
┌────────────────────────────────────────────────────────────┐
│ T224 Reward Attachment Logic (post-job handler)            │
│                                                            │
│ 1. Read results.json from workspace_uuid                   │
│    → overall_score, passed, diagnostics                    │
│                                                            │
│ 2. Create MergeRequest {                                   │
│      workspace_uuid: str                                   │
│      rollout_session_id: str (from dispatch)               │
│      evaluation_reward: float (0..1)                       │
│      evaluation_passed: bool                               │
│      finish_reason: str ("success"/"failure")              │
│      diagnostics_count: int                                │
│    }                                                        │
│                                                            │
│ 3. Call CWSO merge_concurrent_results(merge_req)           │
│    ↓ MergeResult {                                          │
│      merged: bool                                          │
│      conflict_resolution_strategy: str                     │
│      trajectory_id: str                                    │
│    }                                                        │
│                                                            │
│ 4. Log: "Reward attached: rollout_session_id={id},         │
│          score={score}, passed={passed}"                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Integration with Parquet Store (T212 Pattern A)
```
┌─────────────────────────────────────────────────────────┐
│ Parquet Trajectory Store (Polar sidecar)                │
│                                                         │
│ Record Schema:                                          │
│ {                                                       │
│   trajectory_id: str (unique)                          │
│   rollout_session_id: str ← links to merge result     │
│   agent_name: str ("sia_target")                      │
│   timestamps: {...}                                    │
│   completions: [CompletionRecord {...}]               │
│   evaluation_reward: float [0, 1]  ← T224 field       │
│   evaluation_passed: bool            ← T224 field      │
│   finish_reason: str ("success"/"failure")            │
│   ...other fields...                                   │
│ }                                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Spec

### File Structure
```
implementation/adapters/sia-target/
├── Dockerfile  (existing)
├── harness-entrypoint.py  (existing)
├── reward-attachment.py   ← NEW (T224 core logic)
└── tests/
    └── test_t224_reward_attachment.py  ← NEW (test suite)
```

### reward-attachment.py (Core Implementation)

**Purpose**: Post-job handler for attaching evaluation reward to merge result

**Functions**:

#### 1. `read_evaluation_result(workspace_path: str) -> dict`
```python
def read_evaluation_result(workspace_path: str) -> dict:
    """Read results.json from completed job workspace.
    
    Args:
        workspace_path: Path to job workspace (from DispatchResult)
        
    Returns:
        {
            overall_score: float,
            passed: bool,
            diagnostics_count: int,
            ...other fields...
        }
        
    Raises:
        FileNotFoundError: If results.json not found
        json.JSONDecodeError: If results.json malformed
    """
    results_path = Path(workspace_path) / "results.json"
    if not results_path.exists():
        raise FileNotFoundError(f"results.json not found in {workspace_path}")
    
    with open(results_path) as f:
        results = json.load(f)
    
    # Validate required fields
    required = ["overall_score", "passed"]
    missing = [k for k in required if k not in results]
    if missing:
        raise ValueError(f"results.json missing required fields: {missing}")
    
    return results
```

#### 2. `build_merge_request(dispatch_result: dict, evaluation: dict) -> dict`
```python
def build_merge_request(
    dispatch_result: dict,
    evaluation: dict
) -> dict:
    """Build MergeRequest payload for CWSO merge_concurrent_results.
    
    Args:
        dispatch_result: {
            workspace_uuid: str,
            rollout_session_id: str,
            ...
        }
        evaluation: {
            overall_score: float,
            passed: bool,
            diagnostics_count: int,
            ...
        }
        
    Returns:
        MergeRequest {
            workspace_uuid: str,
            rollout_session_id: str,
            evaluation_reward: float (0..1),
            evaluation_passed: bool,
            finish_reason: str,
            diagnostics_count: int,
            attach_timestamp: str (ISO8601)
        }
    """
    return {
        "workspace_uuid": dispatch_result["workspace_uuid"],
        "rollout_session_id": dispatch_result["rollout_session_id"],
        "evaluation_reward": float(evaluation["overall_score"]),
        "evaluation_passed": bool(evaluation["passed"]),
        "finish_reason": "success" if evaluation["passed"] else "failure",
        "diagnostics_count": evaluation.get("diagnostics_count", 0),
        "attach_timestamp": datetime.utcnow().isoformat() + "Z",
    }
```

#### 3. `attach_reward_via_merge(merge_request: dict, cwso_base_url: str, jwt_token: str) -> dict`
```python
def attach_reward_via_merge(
    merge_request: dict,
    cwso_base_url: str,
    jwt_token: str,
    timeout: int = 5
) -> dict:
    """Call CWSO merge_concurrent_results with evaluation reward.
    
    Args:
        merge_request: {workspace_uuid, rollout_session_id, evaluation_reward, ...}
        cwso_base_url: e.g., "http://localhost:8080"
        jwt_token: CWSO JWT auth token
        timeout: request timeout in seconds
        
    Returns:
        MergeResult {
            merged: bool,
            conflict_resolution_strategy: str,
            trajectory_id: str
        }
        
    Raises:
        ConnectionError: If CWSO unavailable
        HTTPError: If merge failed
    """
    url = f"{cwso_base_url}/mcp/merge_concurrent_results"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            url,
            json=merge_request,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Merge request failed: {e}")
        raise ConnectionError(f"CWSO merge failed: {e}")
```

#### 4. `attach_reward_to_job(dispatch_result: dict, workspace_path: str) -> str`
```python
def attach_reward_to_job(
    dispatch_result: dict,
    workspace_path: str,
    cwso_base_url: str = None,
    cwso_jwt: str = None,
    fail_gracefully: bool = True
) -> str:
    """Orchestrate reward attachment for completed job.
    
    Args:
        dispatch_result: From harness dispatch_concurrent_jobs
        workspace_path: Path to job workspace
        cwso_base_url: CWSO endpoint (default: $CWSO_BASE_URL)
        cwso_jwt: CWSO JWT token (default: $CWSO_JWT_SECRET)
        fail_gracefully: If True, log but don't fail job if merge fails
        
    Returns:
        log_message: "Reward attached: rollout_session_id={id}, score={score}, passed={passed}"
    """
    cwso_base_url = cwso_base_url or os.getenv("CWSO_BASE_URL", "http://localhost:8080")
    cwso_jwt = cwso_jwt or os.getenv("CWSO_JWT_SECRET", "")
    
    try:
        # Step 1: Read evaluation
        evaluation = read_evaluation_result(workspace_path)
        logger.info(f"Evaluation read: score={evaluation['overall_score']}, passed={evaluation['passed']}")
        
        # Step 2: Build merge request
        merge_req = build_merge_request(dispatch_result, evaluation)
        
        # Step 3: Attach reward
        if not cwso_jwt:
            logger.warning("CWSO_JWT_SECRET not set; merge attachment skipped (testing mode)")
            return f"Reward attached (mock): rollout_session_id={dispatch_result['rollout_session_id']}, score={evaluation['overall_score']}, passed={evaluation['passed']}"
        
        merge_result = attach_reward_via_merge(merge_req, cwso_base_url, cwso_jwt)
        
        # Step 4: Log result
        log_msg = f"Reward attached: rollout_session_id={dispatch_result['rollout_session_id']}, score={evaluation['overall_score']}, passed={evaluation['passed']}, trajectory_id={merge_result.get('trajectory_id', 'N/A')}"
        logger.info(log_msg)
        return log_msg
        
    except Exception as e:
        error_msg = f"Reward attachment failed: {e}"
        logger.error(error_msg)
        if fail_gracefully:
            logger.warning(f"Continuing despite error (fail_gracefully=True)")
            return f"Reward attachment skipped due to error (see logs)"
        else:
            raise RuntimeError(error_msg)
```

### Integration with Harness Launcher

**Location**: `implementation/adapters/sia-target/harness-entrypoint.py` (modify main loop)

```python
# In main() or job handler loop:
for dispatch_result in dispatch_concurrent_jobs(...):
    # Existing: wait for job completion, validate outputs
    await job_done.wait()
    workspace_path = dispatch_result["workspace_path"]
    
    # Existing: read evaluator results
    evaluate_result = json.loads(Path(workspace_path) / "results.json")
    logger.info(f"Evaluation result: {evaluate_result}")
    
    # NEW T224: Attach reward to merge
    from reward_attachment import attach_reward_to_job
    reward_log = attach_reward_to_job(dispatch_result, workspace_path)
    logger.info(reward_log)
```

### Test Suite (tests/test_t224_reward_attachment.py)

**590 lines total, 3 test classes, 9 test cases**

#### Test Class 1: Evaluation Reading
```python
class T224EvaluationReading(unittest.TestCase):
    """Test evaluation result parsing and validation."""
    
    def test_read_good_evaluation(self):
        """Read well-formed results.json."""
        results = read_evaluation_result(self.good_results_dir)
        self.assertEqual(results["overall_score"], 1.0)
        self.assertTrue(results["passed"])
    
    def test_read_bad_evaluation(self):
        """Read poorly-formed submission with low score."""
        results = read_evaluation_result(self.bad_results_dir)
        self.assertLess(results["overall_score"], 1.0)
        self.assertFalse(results["passed"])
    
    def test_missing_required_fields(self):
        """Fail gracefully if results.json missing fields."""
        with self.assertRaises(ValueError) as cm:
            read_evaluation_result(self.incomplete_results_dir)
        self.assertIn("overall_score", str(cm.exception))
```

#### Test Class 2: Merge Request Building
```python
class T224MergeRequestBuilding(unittest.TestCase):
    """Test MergeRequest contract construction."""
    
    def test_merge_request_schema_good(self):
        """Build valid MergeRequest from good evaluation."""
        dispatch = {
            "workspace_uuid": "uuid-001",
            "rollout_session_id": "session-001"
        }
        evaluation = {
            "overall_score": 0.95,
            "passed": True,
            "diagnostics_count": 0
        }
        merge_req = build_merge_request(dispatch, evaluation)
        self.assertEqual(merge_req["evaluation_reward"], 0.95)
        self.assertTrue(merge_req["evaluation_passed"])
        self.assertEqual(merge_req["finish_reason"], "success")
    
    def test_merge_request_schema_bad(self):
        """Build valid MergeRequest from bad evaluation."""
        dispatch = {
            "workspace_uuid": "uuid-002",
            "rollout_session_id": "session-002"
        }
        evaluation = {
            "overall_score": 0.41,
            "passed": False,
            "diagnostics_count": 9
        }
        merge_req = build_merge_request(dispatch, evaluation)
        self.assertEqual(merge_req["evaluation_reward"], 0.41)
        self.assertFalse(merge_req["evaluation_passed"])
        self.assertEqual(merge_req["finish_reason"], "failure")
    
    def test_merge_request_has_timestamp(self):
        """MergeRequest includes ISO8601 timestamp."""
        merge_req = build_merge_request({...}, {...})
        self.assertIn("attach_timestamp", merge_req)
        self.assertTrue(merge_req["attach_timestamp"].endswith("Z"))
```

#### Test Class 3: CWSO Merge Integration (with Mock)
```python
class T224MergeIntegration(unittest.TestCase):
    """Test CWSO merge attachment with mocked endpoint."""
    
    def setUp(self):
        """Mock CWSO merge endpoint."""
        self.patcher = patch("requests.post")
        self.mock_post = self.patcher.start()
    
    def tearDown(self):
        self.patcher.stop()
    
    def test_attach_reward_via_merge_success(self):
        """Successfully attach reward to merge."""
        self.mock_post.return_value.json.return_value = {
            "merged": True,
            "trajectory_id": "traj-001"
        }
        
        merge_req = {...}
        result = attach_reward_via_merge(merge_req, "http://localhost:8080", "jwt-token")
        
        self.assertEqual(result["trajectory_id"], "traj-001")
        self.assertTrue(result["merged"])
    
    def test_attach_reward_cwso_unavailable(self):
        """Handle CWSO unavailable gracefully."""
        self.mock_post.side_effect = requests.exceptions.ConnectionError("CWSO down")
        
        with self.assertRaises(ConnectionError):
            attach_reward_via_merge({...}, "http://localhost:8080", "jwt-token")
    
    def test_orchestrate_reward_attachment_end_to_end(self):
        """Full orchestration: read evaluation → build merge → attach."""
        dispatch = {
            "workspace_uuid": "uuid-001",
            "rollout_session_id": "session-001"
        }
        
        result_log = attach_reward_to_job(
            dispatch,
            self.good_results_dir,
            cwso_base_url="http://localhost:8080",
            cwso_jwt="jwt-token"
        )
        
        self.assertIn("rollout_session_id=session-001", result_log)
        self.assertIn("score=1.0", result_log)
        self.assertIn("passed=True", result_log)
```

---

## Acceptance Criteria Checklist

- [ ] `reward-attachment.py` implemented with 4 core functions
- [ ] Integration with harness launcher via `attach_reward_to_job()` call
- [ ] MergeRequest schema documented (evaluation_reward, evaluation_passed, finish_reason)
- [ ] CWSO merge endpoint called successfully (mocked in tests)
- [ ] 9 test cases written and all passing
- [ ] Zero regressions: full suite ≥112 tests passing
- [ ] Conventional commits: 95%+ ratio
- [ ] Design document updated with reward attachment flow
- [ ] Code review passed (Tech Lead)
- [ ] Merged to develop with CI green

---

## Implementation Effort Estimate

| Phase | Time | Notes |
|-------|------|-------|
| Design | 0.5h | Document merge contract, review T212 pattern |
| Implementation | 1.5h | 4 functions, 200-250 lines of code |
| Testing | 1h | 3 test classes, 9 test cases, mocking |
| Review + Merge | 0.5h | Tech lead review, CI validation |
| **Total** | **3.5h** | Can be parallelized with infrastructure deployment |

---

## Known Constraints

1. **CWSO Availability** (infrastructure deploy pending)
   - Merge endpoint: `{CWSO_BASE_URL}/mcp/merge_concurrent_results`
   - Auth: JWT token in `Authorization: Bearer {CWSO_JWT_SECRET}`
   - In tests: mock entire endpoint

2. **Job Completion Synchronization**
   - Reward attachment is synchronous (post-job)
   - Must wait for job completion before calling merge
   - Timeout: ≤5s for merge request

3. **Error Handling**
   - Fail gracefully if CWSO unavailable (log, don't fail job)
   - Fail hard if results.json malformed (shouldn't happen with T222 evaluator)
   - Retry policy: 1 retry on transient HTTP error, then give up

4. **Environment Variables**
   - `CWSO_BASE_URL` (default: http://localhost:8080)
   - `CWSO_JWT_SECRET` (required for merge, testing-optional)

---

## Success Criteria (Post-Implementation)

### Code Quality
- ✅ Zero syntax errors (py_compile)
- ✅ 95%+ conventional commits
- ✅ All functions documented with docstrings
- ✅ Type hints for all parameters and returns

### Testing
- ✅ 9/9 test cases passing
- ✅ Full suite: ≥112 tests passing
- ✅ Zero regressions from existing tests
- ✅ Mock CWSO endpoint verified

### Integration
- ✅ Harness launcher calls `attach_reward_to_job()` post-completion
- ✅ Merge request logged with rollout_session_id
- ✅ Evaluation reward attached to trajectory record

### Deployment
- ✅ Merged to develop
- ✅ CI green on merge commit
- ✅ Ready for live infrastructure testing (post-CWSO deploy)

---

## Next Steps

1. **Backend Developer**: Create feature branch `feature/t224-reward-attachment` from develop
2. **Implement**: reward-attachment.py core functions and harness integration
3. **Test**: 9 test cases with mocked CWSO endpoint
4. **Tech Lead**: Code review and merge to develop
5. **DevOps**: Deploy CWSO infrastructure (parallel to T224 implementation)
6. **QA**: Prepare Phase 2 live integration tests (post-infrastructure)

---

## References

- [T223 Integration Test Report](test-report-t223-v1.md) — harness launcher architecture
- [CWSO MCP Contract](cwso-mcp-contract-v1.md) — merge endpoint schema reference
- [Task T224 Brief](../tasks/task-T224.md) — objectives and dependencies
