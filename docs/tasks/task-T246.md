# Task T246 — W1-03 Replace the archive procedure with the atomic 4-step (D4, D5)

**ID:** T246
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T245
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 1 / W1-03

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/knowledge/skills/task-management/SKILL.md`
- **R5** If `### 4. Archive a Task` is not present, STOP and report
  `PRECONDITION FAILED: T246`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T246 replace archive procedure with atomic four-step`

## Objective
The current archive procedure references non-existent `Blocks`/`BlockedBy` columns,
falsely claims "preserving all fields", and tells agents to delete dependency
references — destroying the audit trail. Replace it with the atomic 4-step procedure.

## Edit — replace one whole section

DELETE everything from the line:
```
### 4. Archive a Task
```
down to **but NOT including** the next `## ` heading (which is `## Examples`).

INSERT in its place, **exactly** this content:

````markdown
### 4. Complete a Task (ATOMIC — all 4 steps in one edit session)

Performed by the ORCHESTRATOR ONLY. Other agents report completion; they never move rows.

1. Verify acceptance criteria are met (skill: `verification-before-completion`).
2. APPEND one row to `docs/tasks/completed-tasks.md` using the 5-column schema
   and the field mapping above. Append at the BOTTOM.
3. DELETE the task's row from `docs/tasks/active-tasks.md`.
4. In `docs/tasks/task-<ID>.md`, set the header lines to:
       **Status:** done
       **Completed:** YYYY-MM-DD

Never do step 3 without step 2. Never do step 2 without step 4.

### 5. Cancel a Task

Same 4 steps, except step 2's `Outcome / artifact` MUST start with
`CANCELLED: <reason>;` and step 4 sets `**Status:** cancelled`.

### 6. Dependency bookkeeping

When T-x is completed, for every active row whose `Depends on` contains T-x,
rewrite that cell as `T-x (done)`. NEVER delete the reference — it is the audit trail.
````

Keep exactly one blank line before `## Examples`.

## Expected outputs
- `implementation/knowledge/skills/task-management/SKILL.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "Blocks/BlockedBy" implementation/knowledge/skills/task-management/SKILL.md
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   grep -c "ATOMIC — all 4 steps" implementation/knowledge/skills/task-management/SKILL.md
   ```
   Expected output: `1`
3. Verify command:
   ```bash
   grep -c "### 4. Archive a Task" implementation/knowledge/skills/task-management/SKILL.md
   ```
   Expected output: `0`
4. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/knowledge/skills/task-management/SKILL.md
```
then STOP and report. **Warning:** this also reverts T244 and T245. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Replaced the whole section from `### 4. Archive a Task` down to (but not including)
`## Examples` with the exact atomic completion/cancellation/dependency block.

Verification results:

```bash
$ grep -c "Blocks/BlockedBy" implementation/knowledge/skills/task-management/SKILL.md
0
$ grep -c "ATOMIC — all 4 steps" implementation/knowledge/skills/task-management/SKILL.md
1
$ grep -c "### 4. Archive a Task" implementation/knowledge/skills/task-management/SKILL.md
0
$ git status --porcelain
 M implementation/knowledge/skills/task-management/SKILL.md
```

Outcome: PASS.
