# Task T263 — W4-02 Warn instead of silently dropping non-conforming rows (D11)

**ID:** T263
**Owner:** backend-developer
**Status:** done
**Priority:** P1
**Depends on:** T262
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 4 / W4-02

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `scripts/merge-task-docs.py`
- **Do NOT change the drop behaviour.** Non-conforming rows are still dropped.
  This task **only adds a stderr warning**.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T263 warn when merge drops non-conforming task rows`

## Objective
Make ledger-row loss visible during `install.sh --update` instead of silent.

## Edit — extend `_extract_task_rows`

Current function (lines 23–29):
```python
def _extract_task_rows(text: str) -> list[str]:
    rows: list[str] = []
    for line in text.splitlines():
        if TASK_ROW_RE.match(line) and not EXAMPLE_ROW_RE.search(line):
            rows.append(line)
    return rows
```

REPLACE WITH:
```python
def _extract_task_rows(text: str) -> list[str]:
    rows: list[str] = []
    for line in text.splitlines():
        if TASK_ROW_RE.match(line) and not EXAMPLE_ROW_RE.search(line):
            rows.append(line)
            continue
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if SEPARATOR_RE.match(stripped):
            continue
        if EXAMPLE_ROW_RE.search(line):
            continue
        first_cell = stripped.split("|")[1].strip() if stripped.count("|") > 1 else ""
        if first_cell == "ID":
            continue
        print(
            f"warning: dropping non-conforming task row (ID must match T<NNN>): {line}",
            file=sys.stderr,
        )
    return rows
```

`sys` is already imported at the top of the file — do not add a duplicate import.

## Expected outputs
- `scripts/merge-task-docs.py` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   python3 -m py_compile scripts/merge-task-docs.py && echo OK
   ```
   Expected output: `OK`
2. Verify command:
   ```bash
   grep -c "warning: dropping non-conforming task row" scripts/merge-task-docs.py
   ```
   Expected output: `1`
3. Verify command — header/separator rows must NOT warn:
   ```bash
   python3 -c "
import sys; sys.path.insert(0,'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('m','scripts/merge-task-docs.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
t = '| ID | Title |\n|----|-------|\n| T042 | ok |\n| BUG-7 | bad |\n'
print(m._extract_task_rows(t))
"
   ```
   Expected: stdout shows exactly one preserved row (`| T042 | ok |`), and stderr
   shows exactly one warning mentioning `BUG-7`.
4. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- scripts/merge-task-docs.py
```
then STOP and report. **Warning:** this also reverts T262. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Implemented the specified `_extract_task_rows` replacement in `scripts/merge-task-docs.py`.
Behavior is preserved for conforming rows, and non-conforming table rows are still
dropped, now with a stderr warning.

Verification results:

```bash
$ python3 -m py_compile scripts/merge-task-docs.py && echo OK
OK

$ grep -c "warning: dropping non-conforming task row" scripts/merge-task-docs.py
1

$ python3 -c "
import sys; sys.path.insert(0,'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('m','scripts/merge-task-docs.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
t = '| ID | Title |\n|----|-------|\n| T042 | ok |\n| BUG-7 | bad |\n'
print(m._extract_task_rows(t))
"
warning: dropping non-conforming task row (ID must match T<NNN>): | BUG-7 | bad |
['| T042 | ok |']

$ git status --porcelain
 M scripts/merge-task-docs.py
```

Outcome: PASS.
