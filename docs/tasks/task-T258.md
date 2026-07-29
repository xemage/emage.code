# Task T258 — W3-03 Ship a self-check script into target projects (D10, D16, D18)

**ID:** T258
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T257
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 3 / W3-03

> **This is the highest-leverage task in Plan 014.** Every other enforcement guard
> lives in `tests/`, which is never installed. This script is the only mechanical
> check that reaches a productive target project.

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task creates **EXACTLY ONE NEW FILE**:
  `implementation/docs/tasks/validate-tasks.py`
- If that file already exists, STOP and report `PRECONDITION FAILED: T258`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `feat(tasks): T258 ship task ledger validator into target projects`

## Hard constraints (violating any of these fails the task)
1. **Python standard library ONLY.** No `pip install`. No third-party imports.
   Allowed: `re`, `sys`, `os`, `pathlib`, `datetime`, `collections`, `argparse` (unused).
2. **NO network access** of any kind.
3. **Writes NO files.** Read-only. No logging to disk.
4. **Takes NO command-line arguments.**
5. Reads **only** `./docs/tasks/` relative to the current working directory.
   If `./docs/tasks/` does not exist, fall back to the directory containing the
   script itself.
6. Exit code `1` if any check fails, `0` otherwise.
7. Must run on Python 3.8+ with no syntax warnings.

## Checks to implement (implement ALL ten)

| Code | Check |
|------|-------|
| C1 | `active-tasks.md` contains no row whose Status is `done` or `cancelled` |
| C2 | Every active data row has exactly 7 cells; every completed data row exactly 5 |
| C3 | Every ID matches `^T\d{3,}$` |
| C4 | Every Status ∈ {`pending`,`in_progress`,`blocked`,`in_review`,`done`,`cancelled`} and every Priority ∈ {`P0`,`P1`,`P2`} |
| C5 | No ID appears in both ledgers; no ID appears twice within either ledger |
| C6 | Every `docs/tasks/task-T*.md` has its ID in exactly one ledger (orphan guard) |
| C7 | Every ledger ID has a matching `docs/tasks/task-<ID>.md` |
| C8 | Every `task-<ID>.md` whose header says `**Status:** done` is in `completed-tasks.md`; and every `completed-tasks.md` ID has a brief saying `done` or `cancelled` |
| C9 | `completed-tasks.md` `Done on` values are non-decreasing from top to bottom |
| C10 | Every date cell is a valid `YYYY-MM-DD` (parseable by `datetime.date.fromisoformat`) |

## Row parsing rules (important — get this right)
- A **data row** is a line that starts with `|` after stripping leading whitespace.
- **Ignore** the header row: its first cell (after stripping) is exactly `ID`.
- **Ignore** separator rows: the first cell consists only of the characters `-` and `:`.
- Split cells on `|`, then drop the empty first and last fragments produced by the
  leading and trailing pipes, then `.strip()` each remaining cell.
- Cell count = number of remaining cells after that drop.

## Output contract (exact)
- One line per violation, prefixed exactly `FAIL C<n>: ` (e.g. `FAIL C1: T042 ...`).
- After the violation lines, one summary count line.
- On full success print exactly:
  ```
  TASK LEDGER: PASS (<n> active, <m> completed)
  ```
  and exit `0`.

## Expected outputs
- `implementation/docs/tasks/validate-tasks.py` created, executable is not required.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   cd implementation/docs/tasks && python3 validate-tasks.py; echo "exit=$?"
   ```
   Expected output ends with: `exit=0`
2. Verify command (from repo root):
   ```bash
   python3 -m py_compile implementation/docs/tasks/validate-tasks.py && echo OK
   ```
   Expected output: `OK`
3. Verify command — no third-party imports:
   ```bash
   grep -nE "^\s*(import|from)\s+" implementation/docs/tasks/validate-tasks.py
   ```
   Every listed module must be in the Python standard library. Record the list in
   Execution notes.
4. Verify command — no file writes and no network:
   ```bash
   grep -nE "open\(|write|requests|urllib|socket|http" implementation/docs/tasks/validate-tasks.py
   ```
   `open(` used in **read mode only** is acceptable. Any `write`, `requests`,
   `urllib`, `socket`, or `http` occurrence is a FAIL.
5. `git status --porcelain` lists exactly one new file.

## Revert rule
If any verify command fails:
```bash
rm -f implementation/docs/tasks/validate-tasks.py
```
then STOP and report. Do not weaken a check to make it pass.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Created `implementation/docs/tasks/validate-tasks.py` using only Python standard
library imports, with C1..C10 checks implemented and PASS/FAIL output contract.

Verification evidence:

```bash
$ cd implementation/docs/tasks && python3 validate-tasks.py; echo "exit=$?"
TASK LEDGER: PASS (0 active, 0 completed)
exit=0

$ python3 -m py_compile implementation/docs/tasks/validate-tasks.py && echo OK
OK

$ grep -nE '^\s*(import|from)\s+' implementation/docs/tasks/validate-tasks.py
2:from __future__ import annotations
4:import datetime as dt
5:import re
6:import sys
7:from collections import Counter
8:from pathlib import Path

$ grep -nE 'open\(|write|requests|urllib|socket|http' implementation/docs/tasks/validate-tasks.py
# (no output)

$ git status --porcelain
?? implementation/docs/tasks/validate-tasks.py
```

Outcome: PASS.
