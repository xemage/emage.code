# Task T284 — Remove the stale T266 and T267 rows from the active ledger

**ID:** T284
**Owner:** orchestrator
**Status:** done
**Priority:** P0
**Depends on:** T282
**Created:** 2026-07-29
**Based on:** incomplete archival during T266 and T267

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `docs/tasks/active-tasks.md`
- **R4** Delete **only** the two rows named below. Delete nothing else.
  This is an authorised deletion under R4 — the rows are duplicates, and their
  archived copies in `docs/tasks/completed-tasks.md` are the surviving record.
- **R5** If either FIND line is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T284`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `docs(tasks): T284 remove duplicate T266 and T267 rows from active ledger`

## Why this matters (do not skip)
T266 and T267 were archived: their briefs are `Status: done` and they were appended to
`docs/tasks/completed-tasks.md` (lines 111 and 112). But their rows were never removed
from `docs/tasks/active-tasks.md`. Both IDs therefore exist in **both** ledgers.

`test_task_ids_are_unique_and_well_formed` scans both files and is failing right now:

```
AssertionError: {'T267', 'T266'} is not false : duplicate task ids: ['T266', 'T267']
```

This failure only became visible because T267 removed the `dupes.discard("T001")`
exemption — the check is working exactly as intended.

The rows are also **stale**: they still say `pending`, contradicting the briefs.

## Edit — delete two rows

DELETE these two exact lines (they appear once each, currently lines 5 and 6):

```
| T266 | W5-01 Reuse the shipped checker in CI | qa-engineer | pending | P1 | T265 (done) | 2026-07-28 |
```

```
| T267 | W5-02 Remove the over-broad duplicate exemption | qa-engineer | pending | P1 | T266 (done) | 2026-07-29 |
```

Do not touch the header rows, the separator row, any other task row, or the footer notes.
Do not renumber anything. Leave `docs/tasks/completed-tasks.md` alone.

## Expected outputs
- `docs/tasks/active-tasks.md` loses exactly 2 lines.
- Nothing else changed.

## Acceptance criteria

1. Verify command:
   ```bash
   grep -cE '^\| T26[67] \|' docs/tasks/active-tasks.md
   ```
   Expected output: `0`

2. The archived copies still exist. Verify command:
   ```bash
   grep -cE '^\| T26[67] \|' docs/tasks/completed-tasks.md
   ```
   Expected output: `2`

3. Exactly two lines removed, none added. Verify command:
   ```bash
   git diff --numstat docs/tasks/active-tasks.md
   ```
   Expected: insertions `0`, deletions `2` (output looks like `0	2	docs/tasks/active-tasks.md`).

4. No duplicate task IDs remain. Verify command:
   ```bash
   python3 -m unittest tests.performance.test_team_health.TestTaskLifecycle -v
   ```
   Expected: `OK`

5. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any acceptance criterion fails:
```bash
git checkout -- docs/tasks/active-tasks.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.
