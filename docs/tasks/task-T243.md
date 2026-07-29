# Task T243 — W0-02 Record the pre-change test result

**ID:** T243
**Owner:** orchestrator
**Status:** done
**Priority:** P0
**Depends on:** T242
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 0 / W0-02

## STOP-RULES (read before touching anything)
- This task modifies **NO source files**. It records a baseline only.
- Do **NOT** fix any failing test in this task. Failures are expected and are data.
- Do NOT run `make sync`. Do NOT run `git push`. Do NOT run `git commit`.

## Objective
Capture the performance-suite pass/fail counts **before** Plan 014 changes, so later
waves can prove whether a failure is pre-existing or newly introduced.

## Steps (do exactly this, nothing more)
1. Change directory to the repository root.
2. Run:
   ```bash
   python3 tests/run.py --suite performance -v
   ```
3. Copy the final summary line (test counts, failures, errors) into the
   `## Execution notes` section of this file.

## Expected outputs
- `## Execution notes` in this file contains the raw summary line and the exit code.

## Acceptance criteria
1. The pass count, fail count, error count, and exit code are recorded verbatim.
2. **No test file and no source file was modified.**

## Stop conditions
- `tests/run.py` cannot be executed at all (missing interpreter, import crash)
  → report `PRECONDITION FAILED: T243` with the traceback, then STOP.
- Test failures alone are **not** a stop condition. Record them and finish.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed 2026-07-27 on branch `develop`.

```bash
$ python3 tests/run.py --suite performance -v
...
Ran 17 tests in 3.785s

FAILED (failures=1)
$ echo "EXIT_CODE=$?"
EXIT_CODE=1
```

Recorded baseline failure without fixes, per task rules.
Failure source:
`tests.performance.test_team_health.TestPlanCoverage.test_every_active_task_has_a_plan`

VERDICT: PASS (baseline captured verbatim).
