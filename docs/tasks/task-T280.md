# Task T280 — Add the registry check to the executable FINAL GATE brief

**ID:** T280
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T279
**Created:** 2026-07-28
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § Part 5 — Final gate (registry-drift follow-up, 2026-07-28)

## Why this task exists
T279 fixed the **plan text**. The plan text is not what an agent executes — the
agent executes `docs/tasks/task-T275.md`. Without this task, the FINAL GATE would
still run without the registry check.

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `docs/tasks/task-T275.md`
- This file uses **LF** line endings. Keep them.
- T275 is still `pending`. Do **NOT** execute T275 in this task. Do **NOT** run
  `make sync`, `install.sh`, or the test suite here. You are only editing text.
- Do **NOT** change the T275 title, its `Status`, or its check count wording
  ("four checks"). The registry command is folded into existing Check 1.
- **R5** If the exact find-text below is not found, STOP and report
  `PRECONDITION FAILED: T280`.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `docs(tasks): T280 add registry check to T275 final gate brief`

## Objective
Make the executable FINAL GATE brief run the registry check.

## Edit — replace the Check 1 block

**FIND this block (it occurs exactly once in the file):**

````text
### Check 1 — projections build
```bash
make sync && make verify
```
Expected: exit `0`.
````

**REPLACE WITH exactly this block:**

````text
### Check 1 — projections and registry build
```bash
make sync && make verify
python3 implementation/scripts/check.py --registry --root implementation
```
Expected: both commands exit `0`.
> `make verify` checks projection drift ONLY. The registry is a separate artifact
> and needs its own check. If it reports `registry: generation drift detected`,
> STOP and report it as a blocker. The remedy is a separate task: run
> `python3 implementation/scripts/generate-registry.py --root implementation` and
> commit as `chore(registry): regenerate <reason>`. Do NOT weaken or skip the check.
````

Do not touch Check 2, Check 3, Check 4, or any other part of the file.

## Expected outputs
- `docs/tasks/task-T275.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -Fc "python3 implementation/scripts/check.py --registry --root implementation" docs/tasks/task-T275.md
   ```
   Expected output: `1`
2. Verify command — the title and check count must be untouched:
   ```bash
   grep -Fc "FINAL GATE: four checks" docs/tasks/task-T275.md
   ```
   Expected output: `1`
3. Verify command — the task must still be pending:
   ```bash
   grep -m1 "^\*\*Status:\*\*" docs/tasks/task-T275.md
   ```
   Expected output: `**Status:** done`
4. Verify command — the other three checks must still exist:
   ```bash
   grep -Fc "### Check 2 — full test suite" docs/tasks/task-T275.md
   grep -Fc "### Check 3 — virgin install" docs/tasks/task-T275.md
   grep -Fc "### Check 4 — update round-trip (regression proof for D11 and D16)" docs/tasks/task-T275.md
   ```
   Expected output: `1` for each.
5. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- docs/tasks/task-T275.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Added registry check command to Check 1 in `docs/tasks/task-T275.md`.
Committed with exact message `docs(tasks): T280 add registry check to T275 final gate brief`.

