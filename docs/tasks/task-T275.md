# Task T275 — FINAL GATE: four checks

**ID:** T275
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T273, T274
**Created:** 2026-07-27
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § Part 5 — Final gate

## STOP-RULES (read before touching anything)
- This is a **GATE**. Do **NOT** edit any canonical source file here.
- Allowed write actions: `make sync`, and creating/removing `/tmp/emage-final` only.
- Do NOT run `git push`.
- Do NOT edit anything inside `/tmp/emage-final` to make a check pass.

## Objective
Prove Plan 014 is complete: the knowledge base builds, the repo test suite is green,
a virgin install passes the ledger validator, and an `--update` round-trip does not
corrupt or delete live ledger data.

## Steps (do exactly this, in this order — all four must pass)

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

### Check 2 — full test suite
```bash
python3 tests/run.py -v
```
Expected: `0` failures, `0` errors.
> The T266 validator test must now **pass** — Wave 6 fixed the repository data.

### Check 3 — virgin install
```bash
rm -rf /tmp/emage-final
bash scripts/install.sh --target /tmp/emage-final --platform all
cd /tmp/emage-final && python3 docs/tasks/validate-tasks.py; echo "exit=$?"
```
Expected: `exit=0`.

### Check 4 — update round-trip (regression proof for D11 and D16)
```bash
cd <repo root>
bash scripts/install.sh --target /tmp/emage-final --platform all --update
cd /tmp/emage-final && python3 docs/tasks/validate-tasks.py; echo "exit=$?"
```
Expected: `exit=0`.

## Expected outputs
- A VERDICT: `PASS` | `CONDITIONAL_PASS` | `FAIL`.
- The raw output of all four checks recorded in `## Execution notes`.

## Acceptance criteria
1. All four checks pass as specified above.
2. `git status --porcelain` shows no unexpected modifications caused by this task
   (regenerated platform folders from `make sync` are acceptable).

## Stop conditions
- Any check fails → VERDICT `FAIL`. Report which check, the full output, and the
  first `FAIL C<n>` line if applicable. Do **not** weaken the validator, delete
  ledger rows, or skip tests to force a pass.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

VERDICT: PASS
- Check 1 (Projections & Registry): `make sync && make verify` exited 0; `python3 implementation/scripts/check.py --registry --root implementation` reported `OK - 158 checks passed, 0 errors`.
- Check 2 (Full Test Suite): `python3 tests/run.py -v` ran successfully with 0 failures, 0 errors. `TestShippedTaskValidator` passed.
- Check 3 (Virgin Install): `bash scripts/install.sh --target /tmp/emage-final --platform all` completed successfully; `/tmp/emage-final/docs/tasks/validate-tasks.py` exited 0 (`TASK LEDGER: PASS`).
- Check 4 (Update Round-Trip): `bash scripts/install.sh --target /tmp/emage-final --platform all --update` completed successfully; validator re-run exited 0.

