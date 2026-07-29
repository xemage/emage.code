# Task T260 — W3-05 Wire the self-check into the mandatory skill workflow

**ID:** T260
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T259
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 3 / W3-05

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**: `implementation/AGENTS.md`
  > Do **NOT** edit the repository-root `AGENTS.md`.
- **R5** If the section `## Skill Workflow (mandatory)` and its table are not present,
  STOP and report `PRECONDITION FAILED: T260`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `feat(tasks): T260 require validate-tasks before checkpoints and releases`

## Edit — append one table row

In the `## Skill Workflow (mandatory)` section, find the table with the header:
```
| Situation | Required skill |
```

APPEND this row as the **last** row of that table:
```
| Before any checkpoint, release, or after `install --update` | run `/validate-tasks` |
```

Change no existing row.

## Expected outputs
- `implementation/AGENTS.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "validate-tasks" implementation/AGENTS.md
   ```
   Expected output: `1`
2. Verify command:
   ```bash
   grep -c "^| " implementation/AGENTS.md
   ```
   Expected output must be exactly **one greater** than before the edit.
   Record both numbers in Execution notes.
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/AGENTS.md
```
then STOP and report. **Warning:** this also reverts T249. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Appended the required row as the final entry in the
`## Skill Workflow (mandatory)` table in `implementation/AGENTS.md`:

`| Before any checkpoint, release, or after `install --update` | run `/validate-tasks` |`

Verification results:

```bash
pre_table_rows=21
pre_validate_tasks=0

$ grep -c "validate-tasks" implementation/AGENTS.md
1
$ grep -c "^| " implementation/AGENTS.md
22
$ git status --porcelain
 M implementation/AGENTS.md
```

Outcome: PASS.
