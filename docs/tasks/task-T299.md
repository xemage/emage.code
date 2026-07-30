# Task T299 — Fix task-brief `**Status:**` headers for completed T285-T298

**ID:** T299
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T298
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md (follow-up fix,
discovered during T295's second gate attempt); `docs/tasks/validate-tasks.py`
check `C8`; `tests/performance/test_team_health.py::TestShippedTaskValidator::test_shipped_validator_passes`
(the shipped-validator regression test that caught this).

## Why this task exists
T295's second gate run failed at Step 4 (`python3 tests/run.py`) with:
```
FAIL C8: completed ID T285 has brief status 'pending' (expected done or cancelled)
```
...repeated for T286, T287, T288, T289, T290, T291, T292, T293, T294, and
T298. Root cause: none of the T285-T294/T298 task briefs' STOP-RULES/edit
instructions ever told the executing agent to update the brief file's own
`**Status:** pending` header to `**Status:** done` — only to move the row in
`docs/tasks/active-tasks.md`/`docs/tasks/completed-tasks.md`. The shipped
ledger validator (`docs/tasks/validate-tasks.py`, check `C8`) cross-checks
that every ID marked done in `completed-tasks.md` also shows `done` (or
`cancelled`) in its own `task-T<ID>.md` file — this is a systemic gap across
every brief in this plan, not a defect in any one task's execution.

## STOP-RULES (read before touching anything)
- Confirm T298 is `done` (check `docs/tasks/completed-tasks.md`). If not,
  STOP and report `PRECONDITION FAILED: T299 (missing dependency)`.
- **R2** This task touches **EXACTLY 11 FILES**, and ONLY the `**Status:**`
  header line in each — no other content in any of these files may change:
  `docs/tasks/task-T285.md`, `task-T286.md`, `task-T287.md`, `task-T288.md`,
  `task-T289.md`, `task-T290.md`, `task-T291.md`, `task-T292.md`,
  `task-T293.md`, `task-T294.md`, `task-T298.md`.
- Do NOT touch `docs/tasks/task-T295.md`, `task-T296.md`, `task-T297.md` — those
  are not yet done (T295 itself is what this task unblocks; do not mark it
  done pre-emptively).
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `docs: T299 mark T285-T294/T298 briefs done (fix C8 ledger check)`

## Edit — for each of the 11 files, change the Status header

**FIND (in each of the 11 files listed above, occurs exactly once per file):**
```
**Status:** pending
```

**REPLACE WITH exactly:**
```
**Status:** done
```

Also update each file's `**Completed:**` line (currently `—`) to the date
recorded for that task in `docs/tasks/completed-tasks.md` (all `2026-07-30`
for this batch):

**FIND (in each of the 11 files, occurs exactly once per file):**
```
**Completed:** —
```

**REPLACE WITH exactly:**
```
**Completed:** 2026-07-30
```

## Expected outputs
- The 11 files listed above, each with exactly 2 lines changed
  (`**Status:**` and `**Completed:**`).

## Acceptance criteria
1. Verify command — no more `pending` headers among the 11 completed briefs:
   ```bash
   grep -l "^\*\*Status:\*\* pending$" docs/tasks/task-T285.md docs/tasks/task-T286.md docs/tasks/task-T287.md docs/tasks/task-T288.md docs/tasks/task-T289.md docs/tasks/task-T290.md docs/tasks/task-T291.md docs/tasks/task-T292.md docs/tasks/task-T293.md docs/tasks/task-T294.md docs/tasks/task-T298.md
   ```
   Expected output: empty (no matches, exit code `1` from `grep -l` finding
   nothing is fine/expected here).
2. Verify command — all 11 now show `done`:
   ```bash
   grep -c "^\*\*Status:\*\* done$" docs/tasks/task-T285.md docs/tasks/task-T286.md docs/tasks/task-T287.md docs/tasks/task-T288.md docs/tasks/task-T289.md docs/tasks/task-T290.md docs/tasks/task-T291.md docs/tasks/task-T292.md docs/tasks/task-T293.md docs/tasks/task-T294.md docs/tasks/task-T298.md
   ```
   Expected output: `1` for each of the 11 files.
3. **This is the real gate** — run the shipped validator directly:
   ```bash
   python3 docs/tasks/validate-tasks.py
   ```
   Expected: `TASK LEDGER: PASS` (or equivalent success line — read the
   script's own output format), exit code `0`, with zero `C8` failures.
4. Confirm `task-T295.md`, `task-T296.md`, `task-T297.md` were NOT touched:
   ```bash
   git diff --quiet docs/tasks/task-T295.md docs/tasks/task-T296.md docs/tasks/task-T297.md && echo UNTOUCHED_OK
   ```
   Expected output: `UNTOUCHED_OK`
5. `git status --porcelain` lists exactly the 11 files named in STOP-RULES,
   all modified (no additions/deletions).

## Revert rule
If any verify command fails:
```bash
git checkout -- docs/tasks/task-T285.md docs/tasks/task-T286.md docs/tasks/task-T287.md docs/tasks/task-T288.md docs/tasks/task-T289.md docs/tasks/task-T290.md docs/tasks/task-T291.md docs/tasks/task-T292.md docs/tasks/task-T293.md docs/tasks/task-T294.md docs/tasks/task-T298.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
</content>
