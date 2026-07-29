# Task T267 — W5-02 Remove the over-broad duplicate exemption (D6 blind spot)

**ID:** T267
**Owner:** qa-engineer
**Status:** done
**Priority:** P1
**Depends on:** T266
**Created:** 2026-07-27
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 5 / W5-02

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `tests/performance/test_team_health.py`
- **R4** Delete only the one line named below.
- **R5** If the FIND text is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T267`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `test(tasks): T267 drop T001 duplicate-check exemption`

## Why this matters (do not skip)
The exemption existed only to tolerate the shipped `_Example:` seed row. T257 deleted
that row, so the exemption now hides **real** duplicate `T001` entries.

## Edit — delete one line

DELETE this exact line (currently line 163, preserve surrounding indentation of the
remaining code):
```python
        dupes.discard("T001")
```

Delete nothing else. Do not adjust the surrounding logic.

## Expected outputs
- `tests/performance/test_team_health.py` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c 'discard("T001")' tests/performance/test_team_health.py
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   python3 -m py_compile tests/performance/test_team_health.py && echo OK
   ```
   Expected output: `OK`
3. Verify command:
   ```bash
   python3 tests/run.py --suite performance -v
   ```
   Expected: no test that was passing before this edit now fails. The T266 validator
   test may still fail — that is expected until Wave 6.
4. `git status --porcelain` lists exactly one modified file.

## Revert rule
If acceptance criteria 1, 2, or 3 fails:
```bash
git checkout -- tests/performance/test_team_health.py
```
then STOP and report. **Warning:** this also reverts T266. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Removed `dupes.discard("T001")` from `tests/performance/test_team_health.py` as specified.

Verification results:

```bash
$ grep -c 'discard("T001")' tests/performance/test_team_health.py
0

$ python3 -m py_compile tests/performance/test_team_health.py && echo OK
OK

$ git status --porcelain
 M tests/performance/test_team_health.py
```

Outcome: PASS.
