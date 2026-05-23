---
title: Performance Benchmarks
---

# Performance Benchmarks

This page documents the v2 benchmark suite that validates agent-team quality and
runtime health.

## Scope

The benchmark suite is deterministic, offline, and CI-safe.

- Tool-use quality
- Orchestration trajectory quality
- Runtime scaling and throughput envelope

## Benchmark topology

```mermaid
flowchart LR
    A[tests/performance] --> B[test_tool_use_complexity.py]
    A --> C[test_orchestration_trajectory_quality.py]
    A --> D[test_scaling_and_throughput.py]

    B --> E[tool_use_cases.json]
    C --> F[trajectory_cases.json]
    D --> G[scaling_cases.json]

    B --> H[benchmark-thresholds-v1.json]
    C --> H
    D --> H
```

## Quality metric diagram

```mermaid
flowchart TD
    Q[Tool-use complexity] --> Q1[tool_selection_accuracy]
    Q --> Q2[argument_key_accuracy]
    Q --> Q3[step_efficiency]

    T[Trajectory quality] --> T1[plan_coverage_score]
    T --> T2[dependency_validity_score]
    T --> T3[blocker_routing_score]
    T --> T4[lifecycle_transition_score]
```

## Runtime envelope diagram

Latest local baseline run snapshot:

```mermaid
flowchart TD
    V[verify.mjs] --> V1[p95: 0.320s]
    V --> V2[budget: 5.0s]
    V --> V3[cv: 0.041]

    S[sync.mjs] --> S1[p95: 0.352s]
    S --> S2[budget: 10.0s]
    S --> S3[cv: 0.006]
```

## Threshold policy

Thresholds are versioned in:

- `tests/_baselines/benchmark-thresholds-v1.json`

Fixtures are versioned in:

- `tests/fixtures/benchmarks/tool_use_cases.json`
- `tests/fixtures/benchmarks/trajectory_cases.json`
- `tests/fixtures/benchmarks/scaling_cases.json`

## Running benchmarks

```bash
# Default CI-equivalent benchmark run
python3 tests/run.py --suite performance -v

# Stress mode for deeper local checks
BENCH_STRESS=1 python3 tests/run.py --suite performance -v
```

## Related pages

- [Architecture](architecture)
- [Contributing Workflow](contributing-workflow)
- [Home](home)
