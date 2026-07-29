# Task T264 — W4-03 Regression tests for T262 / T263

**ID:** T264
**Owner:** qa-engineer
**Status:** done
**Priority:** P1
**Depends on:** T263
**Created:** 2026-07-27
**Completed:** 2026-07-28
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 4 / W4-03

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `tests/functional/test_merge_task_docs.py`
- Do **NOT** modify `scripts/merge-task-docs.py` in this task. If a test fails because
  the script is wrong, STOP and report — do not fix the script here.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `test(tasks): T264 add merge-task-docs regression tests`

## Objective
Lock in the T262 and T263 behaviour so a future edit cannot silently reintroduce
ledger data loss.

## Action — add exactly two test methods

Add these to the existing test class in `tests/functional/test_merge_task_docs.py`
(match the file's existing test style, fixtures, and import conventions):

### 1. `test_four_digit_ids_survive_merge`
- Build an existing-ledger string containing a row `| T1001 | four digit id | owner | pending | P1 | — | 2026-07-27 |`.
- Run the merge path used by the other tests in this file.
- Assert `T1001` is present in the merged output.

### 2. `test_bug_prefixed_row_warns`
- Build an existing-ledger string containing a row `| BUG-7 | bad row | owner | pending | P1 | — | 2026-07-27 |`.
- Capture stderr.
- Assert the row is **dropped** from the merged output (`BUG-7` not in output).
- Assert stderr contains the substring `warning: dropping non-conforming`.

If the file has no existing test class, create one named `TestMergeTaskDocs`
following the conventions of the other files in `tests/functional/`.

## Expected outputs
- `tests/functional/test_merge_task_docs.py` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   python3 tests/run.py --suite functional -v
   ```
   Expected: `0` failures, `0` errors.
2. Verify command:
   ```bash
   grep -c "test_four_digit_ids_survive_merge\|test_bug_prefixed_row_warns" tests/functional/test_merge_task_docs.py
   ```
   Expected output: `2`
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- tests/functional/test_merge_task_docs.py
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Added `test_four_digit_ids_survive_merge` and `test_bug_prefixed_row_warns` to the
existing `TestMergeTaskDocs` class in `tests/functional/test_merge_task_docs.py`,
reusing the file's `merge_ledger` import and template-reading conventions.

**First attempt was reverted.** The initial run of criterion 1 failed on two
pre-existing failures unrelated to this task (docker CLI unusable in WSL, and
registry generation drift). Per the revert rule the test file was restored and
the blocker was reported. The baseline was then repaired separately:

- `chore(registry): regenerate after task ledger hardening knowledge updates` (80eb725)
- `test(functional): skip docker availability check when CLI unusable outside CI` (53e737b)

T264 was then re-applied unchanged and verified on the green baseline.

Verification results:

```bash
$ python3 tests/run.py --suite functional
Ran 243 tests in 6.811s
OK (skipped=14)

$ grep -c "test_four_digit_ids_survive_merge\|test_bug_prefixed_row_warns" tests/functional/test_merge_task_docs.py
2

$ git status --porcelain
 M tests/functional/test_merge_task_docs.py
```

`scripts/merge-task-docs.py` was not modified by this task.

Outcome: PASS.
