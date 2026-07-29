# Task T248 — W1-05 Fix Scrum Master archival ownership (D4)

**ID:** T248
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T247
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 1 / W1-05

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/knowledge/agents/scrum-master.md`
- **R5** If the FIND text is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T248`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T248 make archival orchestrator-only in scrum-master`

## Objective
Three different archival triggers exist across the knowledge base. The Scrum Master
agent claims archival happens "at sprint close", which contradicts the orchestrator's
"immediately on completion" rule and allows `done` rows to sit in the active queue.

## Edit — replace one line

FIND (exact, currently line 25 — keep the leading `4. ` list numbering intact):
```
4. Move completed tasks to `docs/tasks/completed-tasks.md` at sprint close
```

REPLACE WITH (exact):
```
4. Report task completion to the orchestrator. NEVER move rows between ledgers — archival is orchestrator-only and happens immediately on completion, not at sprint close
```

## Expected outputs
- `implementation/knowledge/agents/scrum-master.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "Move completed tasks to" implementation/knowledge/agents/scrum-master.md
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   grep -c "archival is orchestrator-only" implementation/knowledge/agents/scrum-master.md
   ```
   Expected output: `1`
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/knowledge/agents/scrum-master.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Applied the one-line replacement in
`implementation/knowledge/agents/scrum-master.md` under **Task Board Management**:

- Replaced `Move completed tasks ... at sprint close`
- With orchestrator-only immediate archival wording.

Verification results:

```bash
$ grep -c "Move completed tasks to" implementation/knowledge/agents/scrum-master.md
0
$ grep -c "archival is orchestrator-only" implementation/knowledge/agents/scrum-master.md
1
$ git status --porcelain
 M implementation/knowledge/agents/scrum-master.md
```

Outcome: PASS.
