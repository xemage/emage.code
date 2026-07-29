# Task T279 — Add the registry check to the FINAL GATE (plan text)

**ID:** T279
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T278
**Created:** 2026-07-28
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § Part 5 — Final gate (registry-drift follow-up, 2026-07-28)

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `docs/plans/plan-014-task-ledger-hardening.md`
- This file uses **CRLF** line endings. Do **NOT** reformat or convert line endings.
- The registry command is folded **into existing check 1**. Do **NOT** create a
  "check 5". Do **NOT** change the sentence `All four checks must pass before this
  plan is marked complete.` The check count stays four.
- Do **NOT** touch the lines added by T276, T277, T278.
- **R5** If the exact find-text below is not found, STOP and report
  `PRECONDITION FAILED: T279`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `docs(plan): T279 add registry check to plan-014 final gate`

## Objective
Make the FINAL GATE fail when the knowledge registry is stale.

## Edit — replace two lines with four

**FIND these two consecutive lines (they occur exactly once in the file):**
```
1. make sync && make verify
   → exit 0
```

**REPLACE WITH exactly these four lines:**
```
1. make sync && make verify
   → exit 0
   python3 implementation/scripts/check.py --registry --root implementation
   → exit 0
```

Keep the 3-space indentation on the `→` lines and on the new command line, exactly
as shown. Do not touch any other line in the file.

## Expected outputs
- `docs/plans/plan-014-task-ledger-hardening.md` modified: exactly 2 lines added.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -Fc "python3 implementation/scripts/check.py --registry --root implementation" docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected output: `4`
2. Verify command — the check count wording must be untouched:
   ```bash
   grep -Fc "All four checks must pass before this plan is marked complete." docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected output: `1`
3. Verify command — no "check 5" was invented:
   ```bash
   grep -Fc "5. python3 implementation/scripts/check.py" docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected output: `0`
4. Verify command — exactly two lines added, zero removed:
   ```bash
   git diff --numstat docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected output starts with: `2	0`
5. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- docs/plans/plan-014-task-ledger-hardening.md
```
then STOP and report. **Warning:** this also reverts T276, T277 and T278. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Folded registry check into check 1 in FINAL GATE in `docs/plans/plan-014-task-ledger-hardening.md` while preserving CRLF line endings.
Committed with exact message `docs(plan): T279 add registry check to plan-014 final gate`.

