**Status:** done
**Completed:** 2026-05-11
# Task T002 — Dataset and Baseline Design

## Objective
Define fixture datasets and baseline thresholds for the new benchmark dimensions.

## Inputs
- docs/artifacts/agent-benchmark-mapping-v1.md
- tests/_baselines/sync-timings.json

## Expected outputs
- tests/_baselines/benchmark-thresholds-v1.json
- tests/fixtures/benchmarks/tool_use_cases.json
- tests/fixtures/benchmarks/trajectory_cases.json
- tests/fixtures/benchmarks/scaling_cases.json

## Acceptance criteria
- Fixtures include passing and failing examples.
- Thresholds define minimum pass values and runtime envelopes.
- File schema is JSON and validated by test loaders.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
