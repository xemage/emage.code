# Task T244 — W1-01 Fix the self-contradicting File Locations table (D1)

**ID:** T244
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T243
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 1 / W1-01

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
  Those are generated. The canonical file is the one named below.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/knowledge/skills/task-management/SKILL.md`
- **R5** If the FIND text is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T244`. Do NOT look for something similar.
- **R6** Do NOT run `make sync` in this task. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T244 remove self-contradicting file locations row`

## Objective
`active-tasks.md` is documented as holding tasks "pending through done", which directly
contradicts the archival rule and the CI guard. Replace that row and add an explicit
INVARIANT block.

## Edit 1 — replace one line

FIND (exact, currently line 24):
```
| `docs/tasks/active-tasks.md` | All tasks not yet archived (pending through done) |
```

REPLACE WITH (exact):
```
| `docs/tasks/active-tasks.md` | Tasks in `pending`, `in_progress`, `blocked`, `in_review` ONLY |
```

## Edit 2 — insert a block

Insert the following text **immediately after** the `## File Locations` table
(i.e. after the `completed-tasks.md` row and the blank line that follows it),
and **before** the `## Task Table Format` heading:

```markdown
> ## INVARIANT (never violate)
> `active-tasks.md` MUST NEVER contain a row whose Status is `done` or `cancelled`.
> The row is removed in the SAME edit that sets the terminal status.
> Writing `done` into `active-tasks.md` is a protocol violation.
```

## Expected outputs
- `implementation/knowledge/skills/task-management/SKILL.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "pending through done" implementation/knowledge/skills/task-management/SKILL.md
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   grep -c "INVARIANT (never violate)" implementation/knowledge/skills/task-management/SKILL.md
   ```
   Expected output: `1`
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/knowledge/skills/task-management/SKILL.md
```
then STOP and report the failure. Do not retry with a different edit.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Applied exactly the two required edits in
`implementation/knowledge/skills/task-management/SKILL.md`:
1. Replaced the `active-tasks.md` file-location purpose line to restrict statuses
  to `pending`, `in_progress`, `blocked`, `in_review`.
2. Inserted the `INVARIANT (never violate)` block immediately before
  `## Task Table Format`.

Verification results:

```bash
$ grep -c "pending through done" implementation/knowledge/skills/task-management/SKILL.md
0
$ grep -c "INVARIANT (never violate)" implementation/knowledge/skills/task-management/SKILL.md
1
$ git status --porcelain
 M implementation/knowledge/skills/task-management/SKILL.md
```

Outcome: PASS.
