# plan-104 — Security-finding grading by any executor, and the per-MR OWASP run (SEC-T586-07)

**Created:** 2026-10-08
**Based on:** the user's decisions of 2026-10-08 ("Root refresh: yes, please refresh"; "Next item: continue as
recommended"); `docs/plans/plan-103-security-gate-alignment.md` §5;
`docs/artifacts/security-review-security-gate-alignment-v1.md` (SEC-T586-07).
**Scopes:** `T588`.

## 1. Root refresh 5

The fifth `--projections-only` refresh follows the plan-082 §2 procedure. It was rehearsed first, with `docs/` and
`implementation/` byte-identical and the changed paths equal to the 54 declared paths. It refreshed those 54 paths
(left stale by T585 and T587), and drift is now 0. It is recorded in MR !497 and needs no ledger row.

## 2. Sequence for SEC-T586-07

1. **Ruling: T588** (solution-architect, P2, decision only): one artifact with a D5 record for each of (a) and (b).
2. **Orchestrator verification.**
3. **Security Engineer review** of every amendment.
4. **User:** every P5 escalation. Part (b) is likely to need one, because assigning an owner for the per-MR OWASP
   run is a choice.
5. **Implementation:** a separate task.

## 3. Not in scope

- P39, FU-6/FU-7 and the P40 rulings are inputs.
- No command is amended.
- FU-8, P32, P33, P41 and P44 stay parked.
