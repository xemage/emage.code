# Task T250 — GATE 1: sync and verify Wave 1

**ID:** T250
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T244, T245, T246, T247, T248, T249
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § GATE 1

## STOP-RULES (read before touching anything)
- This is a **GATE**. Do **NOT** edit any canonical source file here.
- The only allowed write action is running `make sync`, which regenerates the
  platform folders (`.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`).
- Do NOT run `git push`.
- If the gate fails, follow the Revert rule exactly. Do NOT "fix" knowledge files here.

## Objective
Prove that the Wave 1 knowledge edits regenerate cleanly into every platform
projection and that repository verification still passes.

## Steps (do exactly this, in this order)
1. ```bash
   make sync
   ```
2. ```bash
   make verify
   ```
3. ```bash
   git diff --stat implementation/.github implementation/.cursor
   ```

## Expected outputs
- Regenerated platform folders under `implementation/`.
- A VERDICT: `PASS` | `CONDITIONAL_PASS` | `FAIL`.

## Acceptance criteria
1. `make verify` exits with code `0`.
2. Step 3 shows a non-empty diffstat (the Wave 1 changes propagated).
3. No file under `implementation/knowledge/` or `implementation/AGENTS.md` was
   modified by this task.

## Revert rule (only if `make verify` fails)
```bash
git checkout -- implementation/.github implementation/.cursor implementation/.gemini implementation/.opencode implementation/.pi
make sync
```
Then re-run `make verify`. If it fails a second time, emit VERDICT `FAIL`, report the
full error output, and STOP. Do not attempt a third fix.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Gate execution (in order):

```bash
$ make sync
Done - 416 files written.

$ make verify
OK - no drift across 416 files.

$ git diff --stat implementation/.github implementation/.cursor
implementation/.cursor/agents/scrum-master.mdc         |  2 +-
implementation/.cursor/skills/task-management/SKILL.md | 88 +++++++++++++++++++++++++++++++++---------------
implementation/.github/agents/scrum-master.agent.md    |  2 +-
implementation/.github/skills/task-management/SKILL.md | 88 +++++++++++++++++++++++++++++++++---------------
4 files changed, 124 insertions(+), 56 deletions(-)
```

Verdict: PASS.

Post-gate projection updates were committed as:
`87c47c5` (`chore(sync): regenerate installed projections for wave-1 gate`).
