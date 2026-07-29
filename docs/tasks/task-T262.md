# Task T262 — W4-01 Fix the row-preservation regex (D2, D11)

**ID:** T262
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T261
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 4 / W4-01

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `scripts/merge-task-docs.py`
- **R5** If the FIND text is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T262`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T262 widen task row regex to T<NNN+> and tolerant spacing`

## Why this matters (do not skip)
The current regex requires **exactly three digits** and **exactly one space** on each
side of the ID. A `| T1001 | ... |` row or a `|T042| ... |` row is not matched, so
`install.sh --update` silently deletes it from a live project's ledger.

## Edit — replace one line

FIND (exact, currently line 19):
```python
TASK_ROW_RE = re.compile(r"^\| T\d{3} \|")
```

REPLACE WITH (exact):
```python
TASK_ROW_RE = re.compile(r"^\|\s*T\d{3,}\s*\|")
```

Change nothing else in the file. `SEPARATOR_RE` and `EXAMPLE_ROW_RE` stay as they are.

## Expected outputs
- `scripts/merge-task-docs.py` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   python3 -c "import re;r=re.compile(r'^\|\s*T\d{3,}\s*\|');print(bool(r.match('| T1001 | x |')), bool(r.match('|T042| x |')))"
   ```
   Expected output: `True True`
2. Verify command:
   ```bash
   python3 -m py_compile scripts/merge-task-docs.py && echo OK
   ```
   Expected output: `OK`
3. Verify command:
   ```bash
   grep -c 'r"\^\\| T\\d{3} \\|"' scripts/merge-task-docs.py
   ```
   Expected output: `0`
4. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- scripts/merge-task-docs.py
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Applied one-line regex replacement in `scripts/merge-task-docs.py`:

- From: `TASK_ROW_RE = re.compile(r"^\| T\d{3} \|")`
- To:   `TASK_ROW_RE = re.compile(r"^\|\s*T\d{3,}\s*\|")`

Verification results:

```bash
$ python3 -c "import re;r=re.compile(r'^\|\s*T\d{3,}\s*\|');print(bool(r.match('| T1001 | x |')), bool(r.match('|T042| x |')))"
True True

$ python3 -m py_compile scripts/merge-task-docs.py && echo OK
OK

$ grep -c 'r"\^\\| T\\d{3} \\|"' scripts/merge-task-docs.py
0

$ git status --porcelain
 M scripts/merge-task-docs.py
```

Outcome: PASS.
