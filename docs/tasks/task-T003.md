**Status:** done
**Completed:** 2026-05-11
# Task T003 — Implement Tool-Use Complexity Benchmarks

## Objective
Implement benchmark tests inspired by function-calling/tool-use benchmarks (BFCL, ToolBench, ComplexFuncBench, Tau-Bench).

## Inputs
- tests/fixtures/benchmarks/tool_use_cases.json
- tests/_baselines/benchmark-thresholds-v1.json

## Expected outputs
- tests/performance/test_tool_use_complexity.py

## Acceptance criteria
- Measures selection correctness for single, parallel, nested, and multi-turn tool decisions.
- Produces aggregate score and validates against configured threshold.
- Fails deterministically when score is below baseline.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
