# PoC Plan: Local full-text note search

**Status:** draft — awaiting approval (Phase 0)
**Timebox:** 3 working days, hard stop 2026-10-06
**PoC token budget:** 150k

## Hypothesis

```
HYPOTHESIS: SQLite's built-in FTS5 index can serve ranked full-text search over a
            200,000-note synthetic corpus fast enough for search-as-you-type on a
            developer laptop, with no separate search service.
VALIDATION: Load the synthetic corpus into a single SQLite file with an FTS5 table,
            replay a fixed 1,000-query prefix workload, and record per-query latency.
SUCCESS CRITERIA: p95 query latency < 50 ms and index build < 120 s over 3 consecutive runs
FAILURE CRITERIA: p95 query latency > 150 ms OR index file > 2x the raw corpus size
```

## Validation path
Evidence that proves the hypothesis: the latency histogram from the replayed workload meeting the
success criteria on all three runs. Evidence that disproves it: any run crossing a failure criterion.
Results between the two thresholds mean the success criteria were not met, and the PoC fails
(time-boxed, binary outcome — a refined follow-up PoC would be needed).

## 3-step plan
1. (a) Feasibility check — confirm the bundled SQLite build has FTS5 enabled and the 200k-note
   synthetic corpus generates within budget; stop and reframe if either fails.
2. (b) Core build — schema + loader + query replayer; nothing beyond what the measurement needs.
3. (c) Evaluate & demo — run the workload three times, record the histogram, package the demo.

## Key risks and assumptions
- The synthetic corpus's term distribution is representative enough of real notes.
- Laptop thermal throttling skews a run; mitigated by three consecutive runs.
