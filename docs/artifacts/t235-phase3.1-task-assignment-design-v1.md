# T235 Phase 3.1 Design: Task Assignment Algorithm & Node Registry

**Phase:** Production Executor Integration - Phase 3.1
**Task:** T235
**Owner:** backend-developer
**Estimated effort:** 3-4 days (design + implementation)
**Depends on:** T226 ✅, T228 ✅

## Overview

Phase 3.1 implements the critical missing piece from Phase 2: **task assignment** — the mechanism for the CWSO orchestrator to route dispatched tasks to registered executor nodes.

Current state (Phase 2):
- ✅ Executors can register (`POST /nodes/register`)
- ✅ Tasks can be dispatched (`POST /rollout/task/submit`)
- ❌ No connection between them (tasks never reach executors)

Phase 3.1 goal: Bridge this gap with a simple assignment algorithm.

## Design: Round-Robin Task Assignment

### Algorithm Overview

```
When task enters RUNNING state:
  1. Fetch active node list from node registry
  2. Select next available node (round-robin)
  3. Mark task as "assigned" to node_id
  4. Executor polls /nodes/{node_id}/tasks and receives assignment
  5. Executor executes and reports result
```

### State Flow

```
INIT
  ↓
READY (assignment happens here)
  ↓ [assigned to node_id]
RUNNING
  ↓
POSTRUN (after result received)
```

### Implementation Points

#### 1. CWSO Orchestrator Changes

**Location:** `/home/emage/Code/emage/CWSO/orchestrator/internal/rollout/`

**Required changes:**
- **gateway.go:** Add task assignment logic when task transitions to READY
- **Implement new:** `node_registry.go` — track active nodes, implement round-robin selection
- **Implement new:** `task_assignment.go` — persist task→node mapping
- **api_handler.go:** Add new endpoint `GET /nodes/{node_id}/tasks`

**New endpoint signature:**
```go
// GET /nodes/{node_id}/tasks
// Returns: { "assigned_tasks": [ { "task_id": "...", "task_spec": {...} } ] }
// Worker role required
```

#### 2. Node Registry Structure

```go
type NodeRegistry struct {
  mu              sync.RWMutex
  nodes           map[string]*Node
  lastAssignedIdx int  // For round-robin
  cleanupInterval time.Duration
}

type Node struct {
  NodeID        string
  RegisteredAt   time.Time
  LastHeartbeat  time.Time
  Status        string // "active", "inactive", "deregistering"
  Capacity      int    // Number of concurrent tasks (default 1)
}
```

#### 3. Task Assignment Logic

```go
func (nr *NodeRegistry) AssignTask(taskID string, taskSpec interface{}) (string, error) {
  nr.mu.Lock()
  defer nr.mu.Unlock()

  activeNodes := nr.getActiveNodes()
  if len(activeNodes) == 0 {
    return "", ErrNoAvailableNodes
  }

  // Round-robin: select next node
  selected := activeNodes[nr.lastAssignedIdx % len(activeNodes)]
  nr.lastAssignedIdx++

  // Store assignment
  nr.assignments[taskID] = NodeAssignment{
    NodeID:      selected.NodeID,
    AssignedAt:  now(),
    Status:      "pending",
  }

  return selected.NodeID, nil
}

func (nr *NodeRegistry) GetAssignedTasks(nodeID string) []Task {
  nr.mu.RLock()
  defer nr.mu.RUnlock()

  var result []Task
  for taskID, assignment := range nr.assignments {
    if assignment.NodeID == nodeID && assignment.Status == "pending" {
      result = append(result, fetchTask(taskID))
    }
  }
  return result
}
```

### 4. Executor Integration (sia-executor.py)

**Changes required:**
- Replace `get_ready_sessions()` placeholder with real implementation
- Poll `/nodes/{node_id}/tasks` endpoint
- Mark tasks as "in_progress" after fetching
- Report result to `/rollout/session/{session_id}/result`

**Updated flow:**
```python
def get_ready_sessions(self):
  """Fetch assigned tasks from orchestrator"""
  url = f"{self.cwso_url}/nodes/{self.node_id}/tasks"
  token = self.generate_jwt_token("worker")
  headers = {"Authorization": f"Bearer {token}"}

  try:
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    data = response.json()
    return data.get("assigned_tasks", [])
  except Exception as e:
    log.warning(f"Failed to fetch tasks: {e}")
    return []
```

## Implementation Checklist

### Phase 3.1a: Node Registry (Orchestrator)

- [ ] Create `node_registry.go` with NodeRegistry struct and methods
  - [ ] `RegisterNode(node_id string) error`
  - [ ] `DeregisterNode(node_id string) error`
  - [ ] `HeartbeatNode(node_id string) error`
  - [ ] `GetAssignedTasks(node_id string) []Task`
  - [ ] `AssignTask(task_id string) (node_id string, error)`
  - [ ] `MarkTaskAssigned(task_id string, node_id string) error`

- [ ] Create `task_assignment.go` with assignment logic
  - [ ] Task-to-node mapping persistence
  - [ ] Round-robin selection algorithm
  - [ ] Node health check and deregistration

- [ ] Update `gateway.go`
  - [ ] Call assignment on task READY transition
  - [ ] Update task state to include "assigned_node_id"

- [ ] Update `api_handler.go`
  - [ ] Add `GET /nodes/{node_id}/tasks` endpoint
  - [ ] Add JWT role check (worker)
  - [ ] Return assigned task list with full task_spec

### Phase 3.1b: sia-executor.py Integration

- [ ] Update `get_ready_sessions()`
  - [ ] Remove placeholder (always returns [])
  - [ ] Implement real `/nodes/{node_id}/tasks` fetch
  - [ ] Add retry/backoff on transient errors

- [ ] Update `report_session_result()`
  - [ ] Confirm result posting works (already implemented, test)

- [ ] Update main loop
  - [ ] Add heartbeat mechanism (keep-alive to node registry)
  - [ ] Deregister cleanly on shutdown

### Phase 3.1c: Testing & Validation

- [ ] Integration test: dispatch → assign → execute → result
- [ ] Test round-robin with multiple executor nodes
- [ ] Test node deregistration on heartbeat timeout
- [ ] End-to-end with dispatch-test-sia.py (without --mock-execution)

## API Reference

### POST /nodes/register
**Request:**
```json
{
  "node_id": "sia-executor-1"
}
```
**Response:**
```json
{
  "node_id": "sia-executor-1",
  "registered_at": "2026-06-23T12:00:00Z",
  "status": "active"
}
```
**Auth:** Worker role required
**Status:** Already implemented (T226)

### GET /nodes/{node_id}/tasks
**Request:** No body
**Response:**
```json
{
  "assigned_tasks": [
    {
      "task_id": "uuid-1234",
      "task_spec": {
        "description": "...",
        "workspace_id": "...",
        "max_steps": 5
      },
      "assigned_at": "2026-06-23T12:00:00Z"
    }
  ]
}
```
**Auth:** Worker role required
**Status:** To be implemented (Phase 3.1a)

### POST /nodes/{node_id}/heartbeat
**Request:** No body
**Response:**
```json
{
  "status": "acknowledged",
  "next_heartbeat_interval_seconds": 30
}
```
**Auth:** Worker role required
**Status:** To be implemented (Phase 3.1a)

## Risk Mitigation

### Risk: Round-robin too simple for production
**Mitigation:** Current PoC acceptable. Add TODO comment for Phase 4: least-loaded selection, priority queues, etc.

### Risk: Node registry not thread-safe
**Mitigation:** Use `sync.RWMutex` for all access. Test concurrency with multiple executors.

### Risk: Executor misses assignment (network glitch)
**Mitigation:** Executor re-polls every 2s. Orchestrator keeps assignment in PENDING until executor reports result.

## Success Criteria

When Phase 3.1 complete:
- [ ] `dispatch-test-sia.py` (no --mock-execution) dispatches task successfully
- [ ] sia-executor receives task from `/nodes/{node_id}/tasks` within 2 poll cycles
- [ ] Task transitions from RUNNING to COMPLETED state
- [ ] Executor reports result to orchestrator
- [ ] Reward attachment succeeds with real task data
- [ ] No mocks in critical path

## References

- CWSO source: `/home/emage/Code/emage/CWSO/orchestrator/internal/rollout/`
- sia-executor: `implementation/scripts/sia-executor.py`
- E2E test: `implementation/scripts/dispatch-test-sia.py`
- Previous phase analysis: `docs/artifacts/t226-sia-executor-403-debug-report-v1.md`

## Next Phases (3.2+)

- **Phase 3.2:** Real LLM execution in sia-executor (replace mock delay)
- **Phase 3.3:** Wire to SIA harness adapter (`implementation/adapters/sia-target/`)
- **Phase 3.4:** Full E2E validation with Parquet capture
