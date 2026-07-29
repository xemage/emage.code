# Task T266 — W5-01 Reuse the shipped checker in CI — do not reimplement

**ID:** T266
**Owner:** qa-engineer
**Status:** done
**Priority:** P1
**Depends on:** T265
**Created:** 2026-07-27
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 5 / W5-01

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `tests/performance/test_team_health.py`
- **DO NOT duplicate any check logic.** The validator is the single source of truth.
  This test only **executes** it and asserts the exit code.
- **THIS TEST IS EXPECTED TO FAIL WHEN FIRST ADDED.** That is correct. Wave 6
  (T268–T272) fixes the repository's own ledger data. Do **NOT** weaken, skip, or
  `xfail` the test to make it pass.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `test(tasks): T266 run shipped ledger validator in CI`

## Action — add exactly one test class

Add one test class to `tests/performance/test_team_health.py` that:
1. Resolves the repository root.
2. Runs `implementation/docs/tasks/validate-tasks.py` via `subprocess.run`
   with `cwd=<repo root>` and `capture_output=True, text=True`.
3. Asserts `result.returncode == 0`.
4. On failure, includes `result.stdout` in the assertion message so CI shows every
   `FAIL C<n>` line.

Follow the file's existing class/import style. Do **not** add third-party test deps.

## Expected outputs
- `tests/performance/test_team_health.py` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   python3 tests/run.py --suite performance -v
   ```
   Expected at this point in the plan: the **new test FAILS** and every previously
   passing test still passes. Record the exact failure output in Execution notes.
2. Verify command:
   ```bash
   grep -c "validate-tasks.py" tests/performance/test_team_health.py
   ```
   Expected output: `1`
3. Verify command — no duplicated logic:
   ```bash
   grep -c "in_review\|completed-tasks.md" tests/performance/test_team_health.py
   ```
   Record the number. The new class must not add any ledger-parsing code of its own.
4. `git status --porcelain` lists exactly one modified file.

## Stop conditions
- A **previously passing** test now fails → revert and report:
  ```bash
  git checkout -- tests/performance/test_team_health.py
  ```
- `implementation/docs/tasks/validate-tasks.py` does not exist → report
  `PRECONDITION FAILED: T266` (T258 was not completed).

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Added `TestShippedTaskValidator` class running `implementation/docs/tasks/validate-tasks.py`
via `subprocess.run` inside `tests/performance/test_team_health.py`.

As specified in the stop rules, the test correctly failed upon addition because repository
ledger data (orphans, missing briefs, status mismatches) is cleaned up later in Wave 6 (T268–T272).

Verification results:

```bash
$ python3 tests/run.py --suite performance -v
...
FAIL: test_shipped_validator_passes (tests.performance.test_team_health.TestShippedTaskValidator.test_shipped_validator_passes)
...
TASK LEDGER: FAIL (87 violations)
```
- `grep -c "validate-tasks.py" tests/performance/test_team_health.py` → `1`
- `grep -c "in_review\|completed-tasks.md" tests/performance/test_team_health.py` → `0` (no duplicated check logic)
- `git status --porcelain` → `M tests/performance/test_team_health.py`

Outcome: PASS (expected test failure correctly captured).
