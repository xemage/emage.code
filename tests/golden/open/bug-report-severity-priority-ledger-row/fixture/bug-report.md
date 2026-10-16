## Bug Report

### Title
`validate-tasks.py` silently accepts a `Depends on` cell naming a task ID that exists nowhere

### Severity
High — with justification: the validator is the only automated guard on ledger integrity and is run
at every checkpoint and release gate. A dependency pointing at a non-existent ID passes C1–C11
today, so a mistyped dependency survives every gate and is only noticed when an agent is dispatched
against a task whose stated precondition cannot be satisfied. It does not corrupt data, so it is not
Critical, but it defeats the guard's stated purpose for the class of error most likely to occur.

### Environment
Linux (kernel 6.8), Python 3.12, repository `em-age/emage.code` at branch `develop`; reproduced by
running the committed validator directly, no CI involvement.

### Steps to Reproduce
1. Copy `docs/tasks/active-tasks.md` and `docs/tasks/completed-tasks.md` to a scratch directory.
2. Edit one active row's `Depends on` cell to a task ID that appears in neither ledger, e.g. `T899`.
3. Create the matching `task-<ID>.md` brief for the edited row only, so C7 is satisfied.
4. Run `python3 docs/tasks/validate-tasks.py` against the scratch directory.

### Expected Behavior
The validator reports a failure naming the unresolvable dependency and exits non-zero, in the same
style as its existing C7 "missing brief file" check — a dependency on a task that does not exist is
exactly as unactionable as a task row with no brief.

### Actual Behavior
The validator prints `PASS` and exits 0. The unresolvable dependency is reported nowhere.

### Root Cause Analysis
`main()` collects `active_ids` and `completed_ids` and uses them for the C1/C3/C7 checks, but the
`Depends on` cell is destructured into an unnamed slot (`task_id, _, _, status, priority, _,
last_update = row.cells`) and never read again. There is consequently no check at all — C-code or
otherwise — that resolves dependency references against the known ID set. The omission is in the
check *inventory*, not in a check's logic, which is why no existing test covers it.

### Suggested Fix
Add a check that, for every active row, splits its `Depends on` cell on `,`, ignores the `—`
no-dependency token, and reports each remaining entry that is absent from
`set(active_ids) | set(completed_ids)`. Reuse `ID_RE` to reject malformed entries separately from
unresolvable ones, so a typo and a dangling reference produce distinguishable messages.

### Related Files
- `docs/tasks/validate-tasks.py`
- `docs/tasks/active-tasks.md`
- `docs/tasks/completed-tasks.md`
