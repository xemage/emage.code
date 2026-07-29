# Task T268 — W6-01a Archive orphan T214 into completed-tasks.md (D6) — **STOP FIRST**

**ID:** T268
**Owner:** orchestrator
**Status:** done
**Priority:** P0
**Depends on:** T267
**Created:** 2026-07-27
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 6 / W6-01

## ⛔ STOP FIRST — mandatory user confirmation
Before modifying **any** file, ask the user this exact question and **wait for the
answer**:

> "T214 (Pattern A Integration Test, 3 Agents, Deterministic Merge) exists as a brief
> with Status `Pending` but is in neither ledger. Plan 014 assumes it was superseded
> by T228 (live integration). Confirm: should T214 be archived as **CANCELLED —
> superseded by T228**, or is it still live work?"

Do **NOT** guess. Do **NOT** proceed on silence.

## STOP-RULES (read before touching anything)
- **R2** After confirmation, this task touches **EXACTLY ONE FILE**:
  `docs/tasks/completed-tasks.md`
- Do **NOT** edit `docs/tasks/task-T214.md` in this task — that is T269.
- **R4** Append only. Delete no existing row. Reorder nothing.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T268 archive orphan T214 as cancelled`

## Action (only after the user confirms CANCELLED)
APPEND this exact row at the **bottom** of the data table in
`docs/tasks/completed-tasks.md`:
```
| T214 | Pattern A Integration Test (3 Agents, Deterministic Merge) | qa-engineer | 2026-07-27 | CANCELLED: superseded by T228 live integration; docs/tasks/task-T214.md |
```

If the user says T214 is **still live** instead: do not touch
`completed-tasks.md`. Add T214 to `docs/tasks/active-tasks.md` using the 7-column
schema with Status `pending`, then report the deviation to the orchestrator.

## Expected outputs
- One new row in `docs/tasks/completed-tasks.md` (or one new row in
  `active-tasks.md` under the alternative branch).

## Acceptance criteria
1. The user's answer is recorded verbatim in `## Execution notes`.
2. Verify command:
   ```bash
   grep -c "^| T214 |" docs/tasks/completed-tasks.md
   ```
   Expected output: `1` (CANCELLED branch) or `0` (still-live branch).
3. `git diff --stat` shows exactly one file changed and exactly one line added.

## Revert rule
```bash
git checkout -- docs/tasks/completed-tasks.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

User confirmed via prompt: T214 is **STILL LIVE** work.
Action taken: Added T214 to `docs/tasks/active-tasks.md` using the 7-column schema with Status `pending`.

