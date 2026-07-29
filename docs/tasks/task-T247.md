# Task T247 — W1-04 Add `cancelled` to the lifecycle (D7)

**ID:** T247
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T246
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 1 / W1-04

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/knowledge/skills/task-management/SKILL.md`
- **R5** If `## Status Lifecycle` or its `Valid transitions` table is not present,
  STOP and report `PRECONDITION FAILED: T247`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T247 add cancelled state to task lifecycle`

## Objective
`cancelled` is a valid status in `AGENTS.md` and in the CI guard, but the skill's
lifecycle omits it entirely, leaving agents with no defined destination for
abandoned work.

## Edit 1 — extend the transitions table

In the `## Status Lifecycle` section, find the transitions table whose last row is:
```
| `in_review` | `in_progress` | Review rejected, rework needed |
```

APPEND these two rows directly **below** that row:
```
| any | `cancelled` | Work abandoned — orchestrator decision |
| `in_review` | `cancelled` | Rejected outright |
```

## Edit 2 — add the terminal-state note

Directly below the ASCII lifecycle diagram code fence (the one starting with
```` ``` ```` and containing `pending → in_progress → blocked`), insert this line
followed by a blank line:
```
`done` and `cancelled` are TERMINAL → archive immediately (see § "Complete a Task").
```

## Expected outputs
- `implementation/knowledge/skills/task-management/SKILL.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "cancelled" implementation/knowledge/skills/task-management/SKILL.md
   ```
   Expected output: `3` or greater.
2. Verify command:
   ```bash
   grep -c "are TERMINAL" implementation/knowledge/skills/task-management/SKILL.md
   ```
   Expected output: `1`
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/knowledge/skills/task-management/SKILL.md
```
then STOP and report. **Warning:** this also reverts T244–T246. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Applied exactly the two required lifecycle edits in
`implementation/knowledge/skills/task-management/SKILL.md`:
1. Added the terminal-state line immediately below the ASCII lifecycle diagram:
   `done` and `cancelled` are TERMINAL → archive immediately (see § "Complete a Task").
2. Appended two transitions directly below the `in_review → in_progress` row:
   - `any` → `cancelled`
   - `in_review` → `cancelled`

Verification results:

```bash
$ grep -c "cancelled" implementation/knowledge/skills/task-management/SKILL.md
6
$ grep -c "are TERMINAL" implementation/knowledge/skills/task-management/SKILL.md
1
$ git status --porcelain
 M implementation/knowledge/skills/task-management/SKILL.md
```

Outcome: PASS.
