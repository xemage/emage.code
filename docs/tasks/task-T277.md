# Task T277 — Add the registry check to GATE 2

**ID:** T277
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T276
**Created:** 2026-07-28
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § GATE 2 (registry-drift follow-up, 2026-07-28)

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `docs/plans/plan-014-task-ledger-hardening.md`
- This file uses **CRLF** line endings. Do **NOT** reformat, re-indent, convert
  line endings, or "clean up" anything. Insert one line and nothing else.
- Do **NOT** edit `docs/tasks/task-T250.md`, `task-T255.md`, or `task-T261.md`.
- Do **NOT** touch the GATE 1 line added by T276.
- **R5** If the exact find-text below is not found, STOP and report
  `PRECONDITION FAILED: T277`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `docs(plan): T277 add registry check to plan-014 gate 2`

## Objective
Make GATE 2 fail when the knowledge registry is stale.

## Edit — insert exactly one line

**FIND this line (it occurs exactly once in the file):**
```
> grep -rn "BUG-<id>\|→ review →" implementation/knowledge/      → no output
```

**INSERT this new line DIRECTLY BELOW the found line:**
```
> python3 implementation/scripts/check.py --registry --root implementation → exit 0
```

Do not change the found line. Do not touch any other line in the file.

## Expected outputs
- `docs/plans/plan-014-task-ledger-hardening.md` modified: exactly 1 line added.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -Fc "python3 implementation/scripts/check.py --registry --root implementation" docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected output: `2`
   > It is `2`, not `1`, because T276 already added the GATE 1 line.
2. Verify command — the line must sit inside the GATE 2 block:
   ```bash
   grep -FnA1 '> grep -rn "BUG-<id>\|→ review →" implementation/knowledge/      → no output' docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected: the second line printed is the new `--registry` line.
3. Verify command — exactly one line added, zero removed:
   ```bash
   git diff --numstat docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected output starts with: `1	0`
4. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- docs/plans/plan-014-task-ledger-hardening.md
```
then STOP and report. **Warning:** this also reverts T276. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Added registry check command (`python3 implementation/scripts/check.py --registry --root implementation`) to GATE 2 in `docs/plans/plan-014-task-ledger-hardening.md` while preserving CRLF line endings.
Committed with exact message `docs(plan): T277 add registry check to plan-014 gate 2`.

