# Task T253 — W2-03 Make `/sprint-status` read both ledgers (D15, D2)

**ID:** T253
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T252
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 2 / W2-03

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/knowledge/commands/sprint-status.md`
- **R5** If the FIND texts are not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T253`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T253 make sprint-status read both task ledgers`

## Why this matters (do not skip)
`/sprint-status` renders `done` nodes but reads only `active-tasks.md`, which by the
archival invariant can **never** contain a `done` row. Every sprint report therefore
silently under-reports the project.

## Edit 1 — replace `TASK-0` IDs with `T0` in the Mermaid example

In the Mermaid code block (currently around lines 24–35), replace **every** occurrence:

| FIND | REPLACE |
|------|---------|
| `TASK-001` | `T001` |
| `TASK-002` | `T002` |
| `TASK-003` | `T003` |
| `TASK-004` | `T004` |

This affects both the edge definitions and the `class ...` lines. Change nothing else
inside the code block.

## Edit 2 — replace the data-source line

FIND (exact, currently line 38):
```
- Read from `docs/tasks/active-tasks.md` for current task states
```

REPLACE WITH (exact, three bullet lines):
```
- Read `docs/tasks/active-tasks.md` for pending/in_progress/blocked/in_review nodes
- Read `docs/tasks/completed-tasks.md` for `done` nodes — `active-tasks.md` NEVER contains `done`
- Reconstruct dependency edges for done nodes from the `Depends on` cells of active rows
```

## Expected outputs
- `implementation/knowledge/commands/sprint-status.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "TASK-0" implementation/knowledge/commands/sprint-status.md
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   grep -c "NEVER contains" implementation/knowledge/commands/sprint-status.md
   ```
   Expected output: `1`
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/knowledge/commands/sprint-status.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Applied both required edits in
`implementation/knowledge/commands/sprint-status.md`:
1. Replaced all `TASK-001..004` identifiers with `T001..004` in the Mermaid
  example (both edge lines and class lines).
2. Replaced the single active-ledger read bullet with three bullets covering
  active nodes, completed `done` nodes, and dependency-edge reconstruction.

Verification results:

```bash
$ grep -c "TASK-0" implementation/knowledge/commands/sprint-status.md
0
$ grep -c "NEVER contains" implementation/knowledge/commands/sprint-status.md
1
$ git status --porcelain
 M implementation/knowledge/commands/sprint-status.md
```

Outcome: PASS.
