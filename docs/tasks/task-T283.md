# Task T283 — Add a task ID index to plan-014 so active tasks trace to a plan

**ID:** T283
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T284
**Created:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md

## STOP-RULES (read before touching anything)
- **R1** This file is a plan document, not a generated platform file. Editing it is allowed.
- **R2** This task touches **EXACTLY ONE FILE**: `docs/plans/plan-014-task-ledger-hardening.md`
- **R4** Append only. Do **not** modify or delete any existing line.
- **R5** If the file does not have exactly 822 lines before you start, STOP and report
  `PRECONDITION FAILED: T283`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `docs(plans): T283 add task ID index to plan-014`
- **CRLF WARNING** This file uses Windows line endings (`\r\n`) on **all** 822 lines.
  If you append with a normal text editor or a plain heredoc you will create mixed
  line endings and break future exact-match edits. Use the command in STEP 1 verbatim.

## Why this matters (do not skip)
`tests/performance/test_team_health.py` contains `TestPlanCoverage.test_every_active_task_has_a_plan`.
It collects every active task ID and asserts each one appears somewhere in a
`docs/plans/plan-*.md` file. Plan-014 refers to its work items by wave labels
(`W4-01`, `W6-02`, …) and never by task ID, so **every** active task is reported as an
orphan and the test fails.

T275 (FINAL GATE) requires the full test suite to report zero failures. This test will
block that gate until the index exists.

This is a documentation gap, not a test bug. Do **not** weaken or skip the test.

## Precondition check

Run this first:
```bash
wc -l < docs/plans/plan-014-task-ledger-hardening.md
```
Expected output: `822`. If it is anything else, STOP and report `PRECONDITION FAILED: T283`.

## STEP 1 — Append the index

Run this command **verbatim** from the repository root. Do not retype the block by hand.

```bash
python3 - <<'PY'
from pathlib import Path

p = Path('docs/plans/plan-014-task-ledger-hardening.md')
lines = [
    "",
    "## Task ID index (traceability)",
    "",
    "This plan is executed by the task briefs listed below. The index exists so that every",
    "active task traces back to a plan, as required by the TestPlanCoverage check in",
    "`tests/performance/test_team_health.py`.",
    "",
    "T242, T243, T244, T245, T246, T247, T248, T249, T250, T251, T252, T253, T254,",
    "T255, T256, T257, T258, T259, T260, T261, T262, T263, T264, T265, T266, T267,",
    "T268, T269, T270, T271, T272, T273, T274, T275, T276, T277, T278, T279, T280,",
    "T281, T282, T283, T284",
]
with p.open('a', newline='') as f:
    for line in lines:
        f.write(line + "\r\n")
print("appended", len(lines), "lines")
PY
```

Expected output: `appended 11 lines`

## Expected outputs
- `docs/plans/plan-014-task-ledger-hardening.md` grows from 822 to 833 lines.
- All 833 lines end with `\r\n`.
- No existing line changed.

## Acceptance criteria

1. Verify command:
   ```bash
   wc -l < docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected output: `833`

2. Line endings are uniformly CRLF. Verify command:
   ```bash
   grep -c $'\r$' docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected output: `833`

3. No existing line was touched. Verify command:
   ```bash
   git diff --numstat docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected: the deletions column is `0` (output looks like `11	0	docs/plans/...`).

4. Every active task now traces to a plan. Verify command:
   ```bash
   python3 -m unittest tests.performance.test_team_health.TestPlanCoverage -v
   ```
   Expected: `OK`

5. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any acceptance criterion fails:
```bash
git checkout -- docs/plans/plan-014-task-ledger-hardening.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.
