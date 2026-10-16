# plan-106 — Root refresh 6, and the residual golden staleness (FU-8) under a user-approved v17

**Created:** 2026-10-08
**Based on:** the user's decisions of 2026-10-08: "Root refresh: yes, please"; "Next item: approving a v17
baseline - continue with FU-8". Also `docs/plans/plan-101-golden-quote-refresh.md` §4 (FU-8).
**Scopes:** `T592`.

## 1. Root refresh 6

The sixth `--projections-only` refresh followed the plan-082 §2 procedure and was rehearsed first:
- `docs/` and `implementation/` stayed byte-identical;
- the changed paths matched the 32 declared paths exactly.

It refreshed those 32 paths, left stale by T589 and T591, and drift is now 0. It is recorded in MR !504 and needs
no ledger row.

## 2. FU-8: T592

T592 re-copies both fixture files of `validate-workflow-gate-verdict-sources`. The `validation-gates` copy now also
lags T585, T587 and T589. T592 also updates that case's provenance, and fixes two stale statements in
`security-audit-critical-not-fail`:
- its docstring still reads `tracked_defect`;
- its text says "must not be amended" where it means "relaxed".

The task has a file-scoped `protected-paths-v1.md` §5 grant. It changes no `check()` logic and no result.

**The user pre-approved v17 on 2026-10-08.** The orchestrator writes v17 only after independently verifying T592:
- both fixture copies match their sources (`cmp`-identical);
- the results are unchanged;
- the scorecard is unchanged;
- exactly two hash tests fail.

## 3. Outcome (2026-10-08)

- **T592 is merged** (MR !506, `develop` `a404dbc`), together with evaluator-hash baseline **v17**. The user
  approved v17, and the orchestrator wrote it after verifying the work independently. FU-8 is closed.
- **Parked observation.** In `validate-workflow-gate-verdict-sources/brief.md:193`, the provenance grep result
  ("0 matches") is stated as of `a6be6b0`. A re-run today would also match `docs/tasks/task-T572.md`. The statement
  is not false as written. Restating it would need a new grant and a v18.
- **The queue is empty**, and plan-106 is complete.
