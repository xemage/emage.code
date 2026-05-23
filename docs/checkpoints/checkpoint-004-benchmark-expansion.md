# Checkpoint 004 — Benchmark Expansion

Date: 2026-05-11
Phase: QA and benchmark hardening
Based on: docs/plans/plan-001-agent-benchmark-expansion-v2.md

## Completed tasks

- T001 Benchmark Mapping and Spec
- T002 Dataset and Baseline Design
- T003 Implement Tool-Use Complexity Benchmarks
- T004 Implement Orchestration Trajectory Benchmarks
- T005 Implement Scalability and Throughput Benchmarks
- T006 Runner and CI Integration
- T007 Validation and Threshold Tuning
- T008 Docs and Checkpoint

## Artifacts produced

- docs/artifacts/agent-benchmark-mapping-v1.md
- docs/artifacts/benchmark-validation-report-v1.md
- tests/_baselines/benchmark-thresholds-v1.json
- tests/fixtures/benchmarks/tool_use_cases.json
- tests/fixtures/benchmarks/trajectory_cases.json
- tests/fixtures/benchmarks/scaling_cases.json
- tests/performance/test_tool_use_complexity.py
- tests/performance/test_orchestration_trajectory_quality.py
- tests/performance/test_scaling_and_throughput.py
- tests/README.md (benchmark expansion section)

## Validation summary

- python3 tests/run.py --suite performance: PASS
- python3 tests/run.py: PASS

Observed benchmark metrics were above all configured thresholds.

## Decisions

- Keep benchmark suite offline and deterministic by using committed fixture datasets.
- Keep default CI mode lightweight; expose BENCH_STRESS=1 for deeper local stress checks.
- Use threshold JSON to separate benchmark policy from test logic.

## Risks and follow-up

- Current fixtures are intentionally conservative and deterministic; add a v2 fixture set with harder near-threshold cases to increase sensitivity.
- Track p95 and CV over time to detect slow drift before hard failures.

## Next steps

- Consider adding a holdout fixture pack for pre-merge local audits.
- Consider adding trend capture job for benchmark metrics over recent pipelines.
