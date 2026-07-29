# Task T257 — W3-02 Remove the phantom seed task (D12)

**ID:** T257
**Owner:** backend-developer
**Status:** done
**Priority:** P1
**Depends on:** T256
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 3 / W3-02

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/docs/tasks/active-tasks.md`
  > Do **NOT** touch the repository's own `docs/tasks/active-tasks.md`.
- **R4** Delete only the one row named below. Delete nothing else.
- **R5** If the FIND line is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T257`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T257 remove phantom seed row from shipped active ledger`

## Why this matters (do not skip)
Fresh installs seed a fake row. The orchestrator's "next unblocked task, lowest ID
first" rule picks it up as real work, and the ID `T001` becomes ambiguous for the
first real task.

## Edit 1 — delete one line

DELETE this exact line (currently line 5):
```
| T001 | _Example: Define requirements_ | product-owner | pending | P0 | — | YYYY-MM-DD |
```

The table header and separator rows must remain. The table will have zero data rows.

## Edit 2 — add one note line

Add this line directly **below** the existing footer note block (the three lines
beginning `> Status values:`, `> Priority values:`, `> Owners are agent names`),
separated by a blank line:
```
> This ledger starts EMPTY. Do not treat any row here as a template. The first real task is `T001`.
```

## Expected outputs
- `implementation/docs/tasks/active-tasks.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "_Example:" implementation/docs/tasks/active-tasks.md
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   grep -c "starts EMPTY" implementation/docs/tasks/active-tasks.md
   ```
   Expected output: `1`
3. Verify command:
   ```bash
   grep -c "^| T" implementation/docs/tasks/active-tasks.md
   ```
   Expected output: `0`
4. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/docs/tasks/active-tasks.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Applied the one-file shipped-ledger fix in
`implementation/docs/tasks/active-tasks.md`:
- Deleted the phantom row:
   `| T001 | _Example: Define requirements_ | product-owner | pending | P0 | — | YYYY-MM-DD |`
- Added explicit guidance note below the footer notes:
   `This ledger starts EMPTY...`

Verification results:

```bash
$ grep -c "_Example:" implementation/docs/tasks/active-tasks.md
0
$ grep -c "starts EMPTY" implementation/docs/tasks/active-tasks.md
1
$ grep -c "^| T" implementation/docs/tasks/active-tasks.md
0
$ git status --porcelain
 M implementation/docs/tasks/active-tasks.md
```

Outcome: PASS.
