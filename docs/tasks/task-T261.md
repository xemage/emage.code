# Task T261 — GATE 3: the post-install proof

**ID:** T261
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T256, T257, T258, T259, T260
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § GATE 3

> **This is the most important gate in Plan 014.** It proves the guard actually
> reaches a productive target project instead of staying repo-only.

## STOP-RULES (read before touching anything)
- This is a **GATE**. Do **NOT** edit any canonical source file here.
- Allowed write actions: `make sync`, and creating/removing the throwaway directory
  `/tmp/emage-gate3` only.
- Do NOT run `git push`.
- Do NOT edit anything inside `/tmp/emage-gate3` to make the check pass.

## Steps (do exactly this, in this order)
1. ```bash
   make sync && make verify
   ```
2. ```bash
   rm -rf /tmp/emage-gate3
   ```
3. ```bash
   bash scripts/install.sh --target /tmp/emage-gate3 --platform github
   ```
4. ```bash
   cd /tmp/emage-gate3 && python3 docs/tasks/validate-tasks.py; echo "exit=$?"
   ```

## Expected outputs
- A VERDICT: `PASS` | `CONDITIONAL_PASS` | `FAIL`.
- The full stdout of step 4 recorded in Execution notes.

## Acceptance criteria
1. Step 1 exits `0`.
2. Step 3 completes without error.
3. Step 4 prints `TASK LEDGER: PASS (0 active, 0 completed)` and `exit=0`.
4. `/tmp/emage-gate3/docs/tasks/validate-tasks.py` exists — proving the installer
   actually copies the script.
5. `/tmp/emage-gate3/docs/tasks/_template.md` exists.

## Stop conditions
- `validate-tasks.py` is **missing** from the installed target → VERDICT `FAIL`,
  blocker type `technical`, severity `critical`. Root cause is `scripts/install.sh`
  not copying `.py` files from `implementation/docs/`. Report it; do not patch
  `install.sh` in this task.
- `exit=1` → VERDICT `FAIL`. Report every `FAIL C<n>` line verbatim and STOP.
  Do **not** weaken the validator.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Gate commands executed in order:

```bash
$ make sync && make verify
Done - 421 files written.
OK - no drift across 421 files.

$ rm -rf /tmp/emage-gate3

$ bash scripts/install.sh --target /tmp/emage-gate3 --platform github
Installed emage.code (github) into /tmp/emage-gate3

$ cd /tmp/emage-gate3 && ls docs/tasks
__pycache__  _template.md  active-tasks.md  completed-tasks.md  validate-tasks.py

$ test -f docs/tasks/validate-tasks.py; echo "validate_exists=$?"
validate_exists=0

$ test -f docs/tasks/_template.md; echo "template_exists=$?"
template_exists=0

$ python3 docs/tasks/validate-tasks.py; echo "exit=$?"
TASK LEDGER: PASS (0 active, 0 completed)
exit=0
```

Verdict: PASS.

Projection refresh artifacts from this gate were committed as:
`abdb3b5` (`chore(sync): regenerate projections for wave-3 gate`).
