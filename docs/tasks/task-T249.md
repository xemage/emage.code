# Task T249 — W1-06 Tighten the installed Task Protocol (D1, post-install)

**ID:** T249
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T248
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 1 / W1-06

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**: `implementation/AGENTS.md`
  > Do **NOT** edit the repository-root `AGENTS.md`. The canonical source is
  > `implementation/AGENTS.md`.
- **R5** If the FIND text is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T249`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T249 add ledger invariant to installed task protocol`

## Objective
`implementation/AGENTS.md` is the only conventions file that ships into target
projects. Its Task Protocol currently describes a vague 4-column table and states no
archival invariant, so target projects have no rule to follow.

## Edit — replace one line with three lines

FIND (exact, currently line 14):
```
- Task list: `docs/tasks/active-tasks.md` (table: ID, status, owner, dependencies)
```

REPLACE WITH (exact, three bullet lines):
```
- Task list: `docs/tasks/active-tasks.md` — columns: `ID | Title | Owner | Status | Priority | Depends on | Last update`
- **INVARIANT:** `active-tasks.md` MUST NEVER hold a `done` or `cancelled` row. Terminal rows move to `docs/tasks/completed-tasks.md` (columns: `ID | Title | Owner | Done on | Outcome / artifact`) in the same edit.
- Archival is orchestrator-only and immediate. See skill `task-management` § "Complete a Task".
```

Leave every other bullet in the `## Task Protocol` section unchanged.

## Expected outputs
- `implementation/AGENTS.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "INVARIANT" implementation/AGENTS.md
   ```
   Expected output: `1`
2. Verify command:
   ```bash
   grep -c "table: ID, status, owner, dependencies" implementation/AGENTS.md
   ```
   Expected output: `0`
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/AGENTS.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Replaced the single Task Protocol bullet in `implementation/AGENTS.md` with the
three required lines:
1. explicit 7-column `active-tasks.md` schema,
2. invariant forbidding terminal rows in active ledger,
3. orchestrator-only immediate archival reference to `task-management`.

Verification results:

```bash
$ grep -c "INVARIANT" implementation/AGENTS.md
1
$ grep -c "table: ID, status, owner, dependencies" implementation/AGENTS.md
0
$ git status --porcelain
 M implementation/AGENTS.md
```

Outcome: PASS.
