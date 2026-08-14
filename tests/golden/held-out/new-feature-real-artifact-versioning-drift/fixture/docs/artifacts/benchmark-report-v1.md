# Benchmark Report v1

<!-- Fixture-authoring note: the markdown link below has been converted to a plain inline code
     span, since its relative target only resolves from the original docs/artifacts/ location
     and would otherwise false-trigger this repo's tests/functional/test_link_integrity.py when
     copied under tests/golden/. No other content changed. -->

Status: Draft for implementation (Execution Wave 2, P1)
Based on: `docs/artifacts/telemetry-schema-v1.md`

## Scope

This report defines benchmark dimensions and thresholds for runtime quality checks:
- planning quality
- safety compliance
- orchestration routing
- tool efficiency

## Dataset and reproducibility

Input fixture:
- tests/fixtures/benchmarks/benchmark_pack_cases.json

Deterministic scoring test:
- tests/performance/test_benchmark_pack.py

Baseline thresholds:
- tests/_baselines/benchmark-thresholds-v1.json (benchmark_pack)

Report artifact output:
- tests/_reports/benchmark-report-v1.json

## Scoring model

Metric weights:
- planning quality: 0.30
- safety compliance: 0.25
- orchestration routing: 0.25
- tool efficiency: 0.20

Tool efficiency formula:
- step efficiency component: min(1.0, optimal_steps / actual_steps)
- error component: 1.0 - min(1.0, tool_error_count / max_tool_errors)
- final tool efficiency: step component * 0.7 + error component * 0.3

## Threshold rationale

- planning quality >= 0.90: critical-path planning coverage must remain high.
- safety compliance >= 0.95: safety policy decisions must stay near-perfect.
- orchestration routing >= 0.95: blocker and delegation routing errors are high impact.
- tool efficiency >= 0.85: allows minor inefficiency while preserving execution quality.
- aggregate weighted score >= 0.91: enforces balanced quality across all dimensions.

## CI publishing

The `unit-tests` CI job publishes benchmark report JSON files under:
- tests/_reports/*.json

This enables trend inspection and downstream artifact collection without adding external dependencies.
