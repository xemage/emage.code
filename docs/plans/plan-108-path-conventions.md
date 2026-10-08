# plan-108 — Root refresh 7, and the path conventions (P32)

**Created:** 2026-10-08
**Based on:** the user's decisions of 2026-10-08 ("Root refresh: yes, please"; "Next item: continue as
recommended"); `docs/plans/plan-107-remaining-verdict-renderings.md` §4 (G5 and the G7 plan path → P32);
`docs/plans/plan-092-poc-contract-amendments.md` §4 (P32).
**Scopes:** `T595`.

## 1. Root refresh 7

The seventh `--projections-only` refresh followed the plan-082 §2 procedure. It was rehearsed first: `docs/` and
`implementation/` stayed byte-identical, and the changed paths equalled the 44 declared paths. It refreshed those 44
paths, left stale by T594, and drift is now 0. It is recorded in MR !512 and needs no ledger row.

## 2. Sequence for P32

1. **T595** (solution-architect, P2, decision only): D5 records for (a) the production plan path and (b) the
   release-notes duplication, plus user questions for every P5 escalation, with the candidate edits held verbatim.
2. Orchestrator verification.
3. The user decides each escalation, including any command change.
4. Implementation as a separate task. If it changes a golden quote or fixture, it needs a grant and a
   user-authorized v18.

## 3. Not in scope

The following stay parked:
- P33;
- P44;
- L4/X5;
- the plan-106 §3 note;
- P41 observations O1–O5.
