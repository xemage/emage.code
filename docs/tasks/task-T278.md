# Task T278 — Add the registry check to GATE 3

**ID:** T278
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T277
**Created:** 2026-07-28
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § GATE 3 (registry-drift follow-up, 2026-07-28)

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `docs/plans/plan-014-task-ledger-hardening.md`
- This file uses **CRLF** line endings. Do **NOT** reformat, re-indent, convert
  line endings, or "clean up" anything. Insert one line and nothing else.
- Do **NOT** edit `docs/tasks/task-T250.md`, `task-T255.md`, or `task-T261.md`.
- Do **NOT** touch the lines added by T276 and T277.
- The text `> make sync && make verify` appears **twice** in this file. That is why
  the anchor below is `> rm -rf /tmp/emage-gate3` instead. Use the anchor as written.
- **R5** If the exact find-text below is not found, STOP and report
  `PRECONDITION FAILED: T278`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `docs(plan): T278 add registry check to plan-014 gate 3`

## Objective
Make GATE 3 fail when the knowledge registry is stale.

## Edit — insert exactly one line

**FIND this line (it occurs exactly once in the file):**
```
> rm -rf /tmp/emage-gate3
```

**INSERT this new line DIRECTLY ABOVE the found line** (note: **above**, not below —
the registry must be checked before the throwaway install is built):
```
> python3 implementation/scripts/check.py --registry --root implementation
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
   Expected output: `3`
2. Verify command — the new line must sit immediately before the anchor:
   ```bash
   grep -FnB1 "> rm -rf /tmp/emage-gate3" docs/plans/plan-014-task-ledger-hardening.md
   ```
   Expected: the first line printed is the new `--registry` line.
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
then STOP and report. **Warning:** this also reverts T276 and T277. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Added registry check command (`python3 implementation/scripts/check.py --registry --root implementation`) above `> rm -rf /tmp/emage-gate3` in GATE 3 in `docs/plans/plan-014-task-ledger-hardening.md` while preserving CRLF line endings.
Committed with exact message `docs(plan): T278 add registry check to plan-014 gate 3`.

