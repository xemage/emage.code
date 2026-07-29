# Task T252 — W2-02 Fix the `/new-project` lifecycle (D14)

**ID:** T252
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T251
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 2 / W2-02

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/knowledge/commands/new-project.md`
- **R5** If the FIND text is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T252`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T252 correct new-project task lifecycle states`

## Why this matters (do not skip)
`/new-project` is the first command a new user runs. It teaches a fourth, wrong
lifecycle: `review` instead of `in_review`, and no `cancelled` state.

## Edit — replace one line with two lines

FIND (exact, currently line 53, note the **four leading spaces**):
```
    - Track states: `pending → in_progress → review → done` (or `blocked`)
```

REPLACE WITH (exact, preserve the four-space indentation on both lines):
```
    - Track states: `pending → in_progress → blocked → in_review → done | cancelled`
    - The state is spelled `in_review`, NOT `review`.
```

## Expected outputs
- `implementation/knowledge/commands/new-project.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "→ review →" implementation/knowledge/commands/new-project.md
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   grep -c "NOT \`review\`" implementation/knowledge/commands/new-project.md
   ```
   Expected output: `1`
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/knowledge/commands/new-project.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Applied the required replacement in
`implementation/knowledge/commands/new-project.md`:
- Replaced wrong chain `pending → in_progress → review → done`.
- Added canonical chain including `blocked`, `in_review`, and `cancelled`.
- Added explicit spelling note: `in_review`, not `review`.

Verification results:

```bash
$ grep -c "→ review →" implementation/knowledge/commands/new-project.md
0
$ grep -c "NOT `review`" implementation/knowledge/commands/new-project.md
1
$ git status --porcelain
 M implementation/knowledge/commands/new-project.md
```

Outcome: PASS.
