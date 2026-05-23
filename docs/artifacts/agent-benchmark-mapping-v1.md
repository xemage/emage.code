# Agent Benchmark Mapping v1

Based on: docs/plans/plan-001-agent-benchmark-expansion-v2.md

## Purpose

Define deterministic, offline benchmark additions inspired by the AI Agent Benchmark Compendium, mapped to metrics that can be executed in CI using only local fixtures and repository scripts.

## Design Constraints

- Deterministic and offline: no network calls, no external APIs, no remote datasets.
- Lightweight CI runtime: default benchmark execution should remain within a practical test budget.
- Machine-checkable scoring only: no subjective/manual grading.
- Reproducible thresholds: all pass/fail minima and runtime ceilings are versioned in committed baseline JSON.

## Benchmark Mapping

| Benchmark | Compendium inspiration | Dataset | Primary metrics | Pass criteria source |
|---|---|---|---|---|
| Tool-use complexity | Function calling and tool-use evaluation families | tests/fixtures/benchmarks/tool_use_cases.json | tool_selection_accuracy, argument_key_accuracy, step_efficiency, aggregate_weighted_score | tests/_baselines/benchmark-thresholds-v1.json |
| Orchestration trajectory quality | Multi-turn planning/orchestration quality tracks | tests/fixtures/benchmarks/trajectory_cases.json | plan_coverage_score, dependency_validity_score, blocker_routing_score, lifecycle_transition_score, aggregate_weighted_score | tests/_baselines/benchmark-thresholds-v1.json |
| Scaling and throughput envelope | Agent-system throughput/stability tracks | tests/fixtures/benchmarks/scaling_cases.json | p50_seconds, p95_seconds, coefficient_of_variation | tests/fixtures/benchmarks/scaling_cases.json + tests/_baselines/benchmark-thresholds-v1.json |

## Metric Definitions

### 1) Tool-use complexity

Per case:
- tool_selection_accuracy: Jaccard similarity between expected tool set and used tool set.
- argument_key_accuracy: average per-tool key coverage where each expected argument key must appear in at least one call for that tool.
- step_efficiency: min(1.0, optimal_steps / actual_steps).

Suite aggregate:
- mean metric values across cases.
- weighted aggregate:
  - tool_selection_accuracy: 0.50
  - argument_key_accuracy: 0.30
  - step_efficiency: 0.20

### 2) Orchestration trajectory quality

Per case:
- plan_coverage_score: fraction of required plan items covered by candidate plan items.
- dependency_validity_score: fraction of candidate dependency edges that exist in allowed dependency edges.
- blocker_routing_score: fraction of blocker routes matching policy map.
- lifecycle_transition_score: fraction of transitions that are valid according to lifecycle rules.

Suite aggregate:
- mean metric values across cases.
- weighted aggregate:
  - plan_coverage_score: 0.30
  - dependency_validity_score: 0.25
  - blocker_routing_score: 0.25
  - lifecycle_transition_score: 0.20

### 3) Scaling and throughput

Per workload case:
- Runtime samples in seconds from repeated local script runs.
- p50_seconds and p95_seconds from sorted samples.
- coefficient_of_variation = stdev(samples) / mean(samples), 0.0 when mean is 0.

Threshold enforcement:
- p95_seconds must satisfy both case and baseline maximums (stricter effective ceiling).
- coefficient_of_variation must satisfy both case and baseline maximums (stricter effective ceiling).
- BENCH_STRESS=1 increases iteration counts for deeper stress checks.

## Governance Notes

- Threshold changes require intentional baseline updates and justification in review.
- Fixture updates should preserve deterministic behavior and avoid introducing environmental coupling.
- New benchmark versions should be added as new files (`*-v2`) rather than overwriting this mapping contract.
