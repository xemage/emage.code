# Task T269 — W6-01b Set the T214 brief to cancelled (D6)

**ID:** T269
**Owner:** orchestrator
**Status:** done
**Priority:** P0
**Depends on:** T268
**Created:** 2026-07-27
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 6 / W6-01 (second step)

## STOP-RULES (read before touching anything)
- **Precondition:** T268 must be `done` and the user must have confirmed the
  CANCELLED outcome. If T268 took the "still live" branch, **skip this task** and
  report `SKIPPED: T269 (T214 remains live)`.
- **R2** This task touches **EXACTLY ONE FILE**: `docs/tasks/task-T214.md`
- **R5** If the FIND text is not present, STOP and report `PRECONDITION FAILED: T269`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T269 mark T214 brief cancelled`

## Objective
Make the brief header agree with the ledger so validator check C8 passes.

## Edit 1 — change the status line

FIND (exact — note the header in this file uses `**Status**:`, not `**Status:**`):
```
**Status**: Pending
```

REPLACE WITH (exact — the new form uses `**Status:**`):
```
**Status:** cancelled
```

If the file instead contains `**Status:** Pending`, replace that line with
`**Status:** cancelled` and record the deviation in Execution notes.

## Edit 2 — add the completion date

Insert this line directly **below** the status line:
```
**Completed:** 2026-07-27
```

If a `**Completed:**` line already exists, update its value instead of adding a
second one.

## Expected outputs
- `docs/tasks/task-T214.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "^\*\*Status:\*\* cancelled$" docs/tasks/task-T214.md
   ```
   Expected output: `1`
2. Verify command:
   ```bash
   grep -c "^\*\*Completed:\*\* 2026-07-27$" docs/tasks/task-T214.md
   ```
   Expected output: `1`
3. Verify command:
   ```bash
   python3 docs/tasks/validate-tasks.py 2>&1 | grep -c "T214"
   ```
   Expected output: `0`
   > If `docs/tasks/validate-tasks.py` does not exist in this repository, run
   > `python3 implementation/docs/tasks/validate-tasks.py` from the repo root instead
   > and record which path you used.
4. `git status --porcelain` lists exactly one modified file.

## Revert rule
```bash
git checkout -- docs/tasks/task-T214.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Skipped per T269 instruction: T268 took the "still live" branch (user confirmed T214 is live work). T214 remains active; T269 brief marked done/skipped.

