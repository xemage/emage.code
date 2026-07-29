**Status:** done
**Completed:** 2026-05-11
# Task T006 — Runner and CI Integration

## Objective
Integrate newly added benchmark tests into local runner and GitLab CI execution flow.

## Inputs
- tests/run.py
- .gitlab-ci.yml
- New benchmark test files from T003-T005

## Expected outputs
- Updated tests/run.py (if needed)
- Updated .gitlab-ci.yml (if needed)

## Acceptance criteria
- New tests run in `python3 tests/run.py` and in CI unit-tests job.
- No increase in pipeline flakiness.
- Any optional heavy mode is gated behind environment variable.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
