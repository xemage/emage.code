# Benchmark Validation Report v1

Based on: docs/plans/plan-001-agent-benchmark-expansion-v2.md

## Scope

Validation of newly added benchmark files and fixtures:

- tests/performance/test_tool_use_complexity.py
- tests/performance/test_orchestration_trajectory_quality.py
- tests/performance/test_scaling_and_throughput.py
- tests/fixtures/benchmarks/*.json
- tests/_baselines/benchmark-thresholds-v1.json

## Executions

### 1) Performance suite

Command:

python3 tests/run.py --suite performance

Outcome:

- PASS
- Key metrics printed:
  - tool-use-complexity: selection=1.000, args=1.000, efficiency=1.000, aggregate=1.000
  - orchestration-trajectory-quality: plan=0.917, dependency=0.889, blocker=1.000, lifecycle=1.000, aggregate=0.947
  - scaling-and-throughput (default mode):
    - verify-throughput: p95 well below 5.0s, cv below 0.35
    - sync-throughput: p95 well below 10.0s, cv below 0.45

### 2) Full suite

Command:

python3 tests/run.py

Outcome:

- PASS
- No regressions introduced in existing functional or performance tests

## Threshold Review

Thresholds in tests/_baselines/benchmark-thresholds-v1.json are currently strict enough to catch meaningful degradations while leaving headroom for normal CI variance.

- Tool-use thresholds enforce high correctness for tool selection and arguments.
- Trajectory thresholds enforce planning and orchestration discipline.
- Scaling thresholds are bounded by both case-level and baseline-level ceilings (stricter value used at runtime).

## Determinism

No network calls, no external datasets, and no non-deterministic sources are used.

- Fixtures are committed JSON files under tests/fixtures/benchmarks/.
- Stress mode is opt-in via BENCH_STRESS=1.

## Verdict

PASS

The benchmark expansion is validated for local and CI execution and ready for merge/release flow.
