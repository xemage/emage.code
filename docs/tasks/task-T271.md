# Task T271 — W6-03 Re-sort `completed-tasks.md` by `Done on` (D8)

**ID:** T271
**Owner:** orchestrator
**Status:** done
**Priority:** P1
**Depends on:** T270
**Created:** 2026-07-27
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 6 / W6-03

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `docs/tasks/completed-tasks.md`
- **R4** Reorder rows ONLY. **Change NO cell content.** Add no row. Delete no row.
- Keep the `# ` heading, the table header row, the separator row, and every line of
  surrounding prose **exactly where they are**.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T271 sort completed ledger by done date`

## Why this matters (do not skip)
The file claims to be append-only, but T237/T238/T239 (2026-06-26/27) sit between
T045 and T046 (2026-06-06), and T233 lands after T240. Validator check C9 requires
non-decreasing `Done on` values.

## Action
1. Extract only the **data rows** (lines starting with `| T`).
2. Sort them by:
   - primary key: `Done on` (column 4), ascending, lexicographic on `YYYY-MM-DD`
   - tie-break: `ID` (column 1), ascending, numeric on the digits after `T`
3. Write them back in that order, in the same position in the file.

## Safety check (run BEFORE committing)
Prove no cell content changed:
```bash
git show HEAD:docs/tasks/completed-tasks.md | grep '^| T' | sort > /tmp/t271-before.txt
grep '^| T' docs/tasks/completed-tasks.md | sort > /tmp/t271-after.txt
diff /tmp/t271-before.txt /tmp/t271-after.txt && echo "CONTENT IDENTICAL"
```
Expected output: `CONTENT IDENTICAL`.
If `diff` prints anything, you changed content. **Revert immediately.**

## Expected outputs
- `docs/tasks/completed-tasks.md` rows reordered.
- Nothing else changed.

## Acceptance criteria
1. The safety check prints `CONTENT IDENTICAL`.
2. Verify command:
   ```bash
   python3 docs/tasks/validate-tasks.py 2>&1 | grep -c "FAIL C9"
   ```
   Expected output: `0`
3. Verify command — row count unchanged:
   ```bash
   grep -c '^| T' docs/tasks/completed-tasks.md
   ```
   Expected: the same number as before the edit. Record both numbers.
4. `git status --porcelain` lists exactly one modified file.

## Revert rule
```bash
git checkout -- docs/tasks/completed-tasks.md
```
then STOP and report. **Warning:** this also reverts T268. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Re-sorted `docs/tasks/completed-tasks.md` by `Done on` ascending, with tie-break on numeric task ID.
Safety check confirmed `CONTENT IDENTICAL` (zero row content changes).
Validator check C9 passes with 0 failures.

