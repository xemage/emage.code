# `/validate-tasks` report — ledger with violations

Ran `python3 docs/tasks/validate-tasks.py` from the project root. Exit code: `1`.

Every line the validator emitted, reproduced verbatim:

```
FAIL C5: ID appears in both ledgers: T902
FAIL C6: task-T902.md has ID T902 present in 2 ledgers (expected 1)
FAIL C7: missing brief file: task-T904.md
FAIL C8: completed ID T902 has brief status 'in_progress' (expected done or cancelled)
FAIL C8: completed ID T904 has brief status 'None' (expected done or cancelled)
TASK LEDGER: FAIL (5 violations)
```

## Proposed fix, one per violation

1. `FAIL C5: ID appears in both ledgers: T902` — T902 is listed in both `active-tasks.md` and
   `completed-tasks.md`. **Not auto-fixed.** Which ledger is correct — is T902 still in flight, or
   was it completed on 2026-09-24?
2. `FAIL C6: task-T902.md has ID T902 present in 2 ledgers (expected 1)` — the same underlying
   double-listing seen from the brief's side. **Not auto-fixed**; it resolves with the answer to
   violation 1. Which ledger is correct for T902?
3. `FAIL C7: missing brief file: task-T904.md` — `completed-tasks.md` cites T904 but no
   `task-T904.md` exists. Proposed fix: add the missing brief, or drop the T904 row if it was
   never a real task.
4. `FAIL C8: completed ID T902 has brief status 'in_progress' (expected done or cancelled)` —
   **Not auto-fixed.** Which ledger is correct: the brief's `in_progress` status, or the completed
   row?
5. `FAIL C8: completed ID T904 has brief status 'None' (expected done or cancelled)` —
   **Not auto-fixed**; depends on the resolution of violation 3. Which ledger is correct here?

C5, C6 and C8 violations are deliberately left unfixed pending your answer, per the command's
"Do NOT auto-fix C5, C6, or C8" rule.
