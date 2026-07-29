# Task T276 — Add the registry check to GATE 1

**ID:** T276
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T264 (done)
**Created:** 2026-07-28
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § GATE 1 (registry-drift follow-up, 2026-07-28)

## Why this task exists (read once, then stop thinking about it)
Gates 1, 2 and 3 ran `make sync` and `make verify` only. `make verify` checks
**projection drift only** — it does NOT check the knowledge registry. Because of
that, Waves 1–3 edited knowledge files, the registry went stale, and no gate
caught it. These tasks add the missing command to each gate.

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `docs/plans/plan-014-task-ledger-hardening.md`
- This file uses **CRLF** line endings. Do **NOT** reformat, re-indent, convert
  line endings, or "clean up" anything. Insert one line and nothing else.
- Do **NOT** edit `docs/tasks/task-T250.md`, `task-T255.md`, or `task-T261.md`.
  Those are completed gate records. Rewriting them would falsify history.
- **R5** If the exact find-text below is not found, STOP and report
  `PRECONDITION FAILED: T276`. Do not search for something similar.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `docs(plan): T276 add registry check to plan-014 gate 1`

## Objective
Make GATE 1 fail when the knowledge registry is stale.

## Edit — insert exactly one line

**FIND this line (it occurs exactly once in the file):**
```
> git diff --stat implementation/.github implementation/.cursor → shows changes
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
   Expected output: `1`
2. Verify command — the line must sit inside the GATE 1 block:
   ```bash
   grep -FnA1 "> git diff --stat implementation/.github implementation/.cursor → shows changes" docs/plans/plan-014-task-ledger-hardening.md
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
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Added registry check command (`python3 implementation/scripts/check.py --registry --root implementation`) to GATE 1 in `docs/plans/plan-014-task-ledger-hardening.md` while preserving CRLF line endings.
Committed with exact message `docs(plan): T276 add registry check to plan-014 gate 1`.

