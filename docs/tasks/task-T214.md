# Task T214: Pattern A Integration Test (3 Agents, Deterministic Merge)

**ID**: T214
**Owner**: qa-engineer
**Priority**: P0 (Critical Path)
**Status**: Pending
**Depends on**: T212 (Concurrent merge orchestrator) ✓, T213 (AST conflict pre-check) ✓

---

## Objective

Validate Pattern A end-to-end orchestration with three concurrent worker agents editing a shared file. Confirm that the AST conflict pre-check correctly routes to appropriate merge heuristics and deterministic merges succeed without data loss or corruption.

---

## Context

### Pattern A (CWSO Orchestration)
```
N agents → isolated shadow workspaces → concurrent edits → semantic merge via AST heuristics
```

### Dependencies Met
- **T212** ✓: `ConcurrentMergeOrchestrator` ready (N workers → fanout → merge)
- **T213** ✓: `AstConflictChecker` ready (pre-check routing)
- **T210** ✓: `CwsoClient` library (JWT, rate limiting, tool calls)

---

## Acceptance Criteria

### Test Scenario 1: Independent Edits (LOW Severity → Merge Success)
```
Baseline:
  def foo(): pass
  def bar(): pass

Agent A edits:
  def foo(): return 1  # modify existing function
  def bar(): pass

Agent B edits:
  def foo(): pass
  def baz(): return 2  # add new function

Agent C edits:
  def foo(): pass
  def bar(): pass
  def qux(): return 3  # add another new function
```

**Expected**:
- Pre-check severity: LOW
- Merge heuristic: AST_SEMANTIC_ONLY
- Merge result: All 4 functions present, no conflicts
- Final state: `foo`, `bar`, `baz`, `qux` all present and non-interfering

### Test Scenario 2: Simultaneous Symbol Addition (MEDIUM Severity → Merge Blocked)
```
Baseline:
  def foo(): pass

Agent A edits:
  def foo(): pass
  def helper(): return 1  # add helper

Agent B edits:
  def foo(): pass
  def helper(): return 2  # same name, different body
```

**Expected**:
- Pre-check severity: MEDIUM (both add same symbol)
- Merge heuristic: FAIL_RAPIDLY_ON_CONFLICT
- Merge result: Conflict detected, merge blocked
- Error reason: "Simultaneous add of symbol 'helper'"

### Test Scenario 3: Diverging Function Signatures (HIGH Severity → Merge Blocked)
```
Baseline:
  def compute(x): return x * 2

Agent A edits:
  def compute(x, y): return x * y  # signature diverges

Agent B edits:
  def compute(x): return x + 1  # different but same arity
```

**Expected**:
- Pre-check severity: HIGH (diverging signatures)
- Merge heuristic: FAIL_RAPIDLY_ON_CONFLICT
- Merge result: Conflict detected, merge blocked
- Error reason: "Diverging signatures for 'compute'"

### Test Scenario 4: Multi-File with Mixed Severities
- File 1: Independent edits (LOW) → passes
- File 2: Simultaneous add (MEDIUM) → blocked
- Overall result: Merge fails on File 2, succeeds on File 1

---

## Outputs

### Required Deliverables
1. **Test Module**: `tests/functional/test_pattern_a_integration.py`
   - Implement 4 test cases above (Scenario 1-4)
   - Each test:
     - Creates 3 worker agents with edit sets
     - Invokes ConcurrentMergeOrchestrator.run()
     - Optionally calls AstConflictChecker.run() if run_ast_precheck=True
     - Asserts merge result matches expected outcome
   - Use mock CwsoClient if live endpoint unavailable

2. **Test Report**: `tests/_reports/pattern-a-integration-report-v1.json`
   - Summary of test scenarios
   - Pass/fail status for each
   - Merge heuristic routing trace
   - Per-file conflict analysis

3. **Documentation**: Create `implementation/runtime/cwso/README.md`
   - Pattern A workflow description
   - Conflict severity and heuristic mapping
   - Example: 3-agent scenario
   - Usage guide

### Success Criteria
- ✓ All 4 test scenarios pass
- ✓ Merge heuristics correctly routed per severity
- ✓ No data loss or corruption in successful merges
- ✓ Conflicts correctly detected and reported
- ✓ Full test suite (99+) passes, no regressions
- ✓ Test deterministically reproduces same merge results on re-run

---

## Inputs

### Provided Artifacts
- `implementation/runtime/cwso/concurrent_merge.py` (T212) ✓
- `implementation/runtime/cwso/ast_conflict_check.py` (T213) ✓
- `implementation/runtime/cwso/client.py` (T210) ✓
- CWSO MCP endpoint contract (docs/artifacts/cwso-mcp-contract-v1.md)

### Test Environment
- Python 3.12
- CWSO endpoint on http://127.0.0.1:8080
- Mock or staging instance (can use in-memory repo or Git sandbox)

---

## Constraints

### Token Budget
- Max 120k tokens (Implementation phase)

### File Ownership
- Tests: `tests/` directory (qa-engineer)
- Implementation: CWSO module (backend-developer)
- Documentation: `implementation/runtime/cwso/README.md` (shared)

### Technology
- Python 3.12, unittest/pytest
- CWSO MCP client (CwsoClient from T210)
- Mock patterns for testing

---

## Blocker Protocol

If blocked, report blocker type and severity with one proposed mitigation:
- **Technical**: CWSO endpoint unreachable → mock with in-memory shadow workspace simulator
- **Dependency**: merge_concurrent_results behavior undefined → escalate to T212 owner
- **Unclear Requirements**: Heuristic routing semantics → review ADR-001

---

## References

- [Checkpoint T213](../checkpoints/checkpoint-v3-007-t213-completion.md)
- [ADR-001: CWSO×SIA Integration](../decisions/ADR-001-cwso-sia-integration.md)
- [CWSO MCP Contract](../artifacts/cwso-mcp-contract-v1.md)
- [ConcurrentMergeOrchestrator](../../implementation/runtime/cwso/concurrent_merge.py)
- [AstConflictChecker](../../implementation/runtime/cwso/ast_conflict_check.py)

---

**Next Task**: T220 (SIA harness adapter) — after T214 passes
**Team**: @qa-engineer (lead); @backend-developer (support)
