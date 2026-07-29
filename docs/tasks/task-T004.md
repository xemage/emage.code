**Status:** done
**Completed:** 2026-05-11
# Task T004 — Implement Orchestration Trajectory Benchmarks

## Objective
Implement trajectory-quality benchmarks inspired by AgentBench and general assistant reasoning benchmarks.

## Inputs
- tests/fixtures/benchmarks/trajectory_cases.json
- tests/_baselines/benchmark-thresholds-v1.json

## Expected outputs
- tests/performance/test_orchestration_trajectory_quality.py

## Acceptance criteria
- Validates plan coverage, dependency consistency, blocker routing correctness, and status transition discipline.
- Computes rubric-based score with explicit sub-metric breakdown.
- Thresholded and deterministic in CI.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
