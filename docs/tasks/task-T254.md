# Task T254 — W2-04 Make `/team-status` read both ledgers (D15, D2)

**ID:** T254
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T253
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 2 / W2-04

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/knowledge/commands/team-status.md`
- **R5** If the FIND texts are not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T254`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T254 make team-status read both task ledgers`

## Why this matters (do not skip)
Identical defect to T253: `/team-status` renders `done` nodes from a ledger that can
never contain them.

## Edit 1 — replace `TASK-0` IDs with `T0` in the Mermaid example

In the Mermaid code block (currently around lines 29–40), replace **every** occurrence:

| FIND | REPLACE |
|------|---------|
| `TASK-001` | `T001` |
| `TASK-002` | `T002` |
| `TASK-003` | `T003` |
| `TASK-004` | `T004` |

This affects both the edge definitions and the `class ...` lines. Change nothing else
inside the code block.

## Edit 2 — replace the data-source line

FIND (exact, currently line 43):
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
- `implementation/knowledge/commands/team-status.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "TASK-0" implementation/knowledge/commands/team-status.md
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   grep -c "NEVER contains" implementation/knowledge/commands/team-status.md
   ```
   Expected output: `1`
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/knowledge/commands/team-status.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Applied both required edits in
`implementation/knowledge/commands/team-status.md`:
1. Replaced all `TASK-001..004` identifiers with `T001..004` in the Mermaid
  example (edge lines and class lines).
2. Replaced the active-only read bullet with three bullets for:
  - active pending/in_progress/blocked/in_review nodes,
  - completed `done` nodes,
  - dependency-edge reconstruction for done nodes.

Verification results:

```bash
$ grep -c "TASK-0" implementation/knowledge/commands/team-status.md
0
$ grep -c "NEVER contains" implementation/knowledge/commands/team-status.md
1
$ git status --porcelain
 M implementation/knowledge/commands/team-status.md
```

Outcome: PASS.
