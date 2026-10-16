# PoC Evaluation: Local full-text note search

## Hypothesis Restatement
SQLite FTS5 can serve ranked search-as-you-type over a 200,000-note corpus on a developer laptop with
p95 query latency < 50 ms and an index build < 120 s over 3 consecutive runs, without a separate search
service.

## Evidence Summary
- Three consecutive replays of the fixed `prefix-1000` workload: p95 = 31 ms, 34 ms, 29 ms.
- Index build: 74 s, 71 s, 73 s. Index size 1.4x the raw corpus (failure threshold was 2x).
- Not tested: concurrent writes; a real (non-synthetic) term distribution.

## Verdict
Validated — all three runs met both success criteria and none crossed a failure criterion.

## Recommended Next Step
Run a writer-under-load benchmark before committing the v1 design to FTS5.

## Production Recommendation
proceed_with_constraints — adopt FTS5 for v1 read paths, conditional on the concurrent-write benchmark.

## Production Refactoring Backlog
1. Replace the throwaway loader with the production ingestion pipeline and its retry semantics
2. Add a concurrent-write benchmark and an index-rebuild strategy for online writes
3. Move the hardcoded database path into configuration
4. Add input validation and query-length limits on the search endpoint
5. Replace the terminal UI with the product search component
6. Add latency telemetry to production dashboards

## Technical Debt Scorecard Summary
Five debt items: two CRITICAL (no input validation on the query path; no strategy for online writes),
two MEDIUM, one LOW — see the Debt Summary table below for severity, effort, risk and owner per item.

## Residual Risks and Assumptions
1. Concurrent write throughput is unknown and may force a read replica.
2. The synthetic corpus may under-represent long-tail terms in real notes.

## POC VERDICT

- **Hypothesis**: SQLite FTS5 can serve ranked search-as-you-type over 200,000 notes on a laptop with p95 < 50 ms, without a search service
- **Status**: VALIDATED
- **Production recommendation**: proceed_with_constraints
- **Evidence strength**: moderate
- **Debt items**: 5 (CRITICAL: 2, MEDIUM: 2, LOW: 1)
- **Residual risks**: 2
- **Evaluator**: poc-orchestrator
- **Timestamp**: 2026-10-01T16:40:00Z

## Production Handoff Checklist

- [x] All CRITICAL debt items have remediation plans with owners
- [ ] Architecture decisions documented in `docs/decisions/`
- [ ] Security audit completed (or scheduled for Phase 1)
- [x] Performance baselines established
- [ ] Test coverage plan defined for production code
- [ ] Data migration/seeding strategy defined (if applicable)
- [ ] Monitoring and alerting requirements captured
- [ ] Production infrastructure requirements documented

## Debt Summary

| # | Debt Item | Severity | Effort | Risk | Owner | Production Impact |
|---|-----------|----------|--------|------|-------|-------------------|
| 1 | No input validation or length limit on search queries | CRITICAL | S | Query-based denial of service | backend-developer | blocks |
| 2 | Index built once; no strategy for online writes | CRITICAL | L | Stale or blocked search under write load | backend-developer | blocks |
| 3 | Hardcoded database path | MEDIUM | S | Misconfigured deploys | devops-engineer | degrades |
| 4 | Loader has no retry or partial-failure handling | MEDIUM | M | Silent gaps in the index | backend-developer | degrades |
| 5 | Throwaway terminal UI | LOW | M | None in production if not carried over | frontend-developer | cosmetic |
