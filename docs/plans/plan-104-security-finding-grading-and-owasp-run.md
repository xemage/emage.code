# plan-104 — Security-finding grading by any executor, and the per-MR OWASP run (SEC-T586-07)

**Created:** 2026-10-08
**Based on:** the user's decisions of 2026-10-08 ("Root refresh: yes, please refresh"; "Next item: continue as
recommended"); `docs/plans/plan-103-security-gate-alignment.md` §5;
`docs/artifacts/security-review-security-gate-alignment-v1.md` (SEC-T586-07).
**Scopes:** `T588`, `T589`.

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

## 4. Outcome (2026-10-08)

- **The T588 ruling** is `security-finding-grading-and-owasp-run-v1.md`.
  - (a) and (b) are both gaps, not contradictions (Step A). Both escalated under P5.
  - The orchestrator verified the ruling: 40/40 quotes verbatim, and all six anchors unique.
- **User decisions** (2026-10-08, verbatim option labels):
  - Q-a: **"Pointer (Recommended)"** (A1).
  - Q-b: **"Tech Lead per MR (Recommended)"** (B1).
  - O1: **"Rule it next (Recommended)"**.
- **Security Engineer review: CONDITIONAL_PASS** (`security-review-security-finding-grading-v1.md`).
  - C1 (SEC-T588-01, `SECURITY:MEDIUM`): the pointer must not displace the PoC severity floors at
    `poc-security-engineer:21` and `poc-orchestrator:76`. The orchestrator verified that both floors exist.
  - SEC-T588-02 to 05 are `SECURITY:LOW`.
  - All were adopted verbatim in `security-finding-grading-and-owasp-run-v2.md`.
- **Orchestrator check of v2.** The three edits apply once each to scratch copies. The user-chosen A1 sentences are
  verbatim, and C1 and the LOW wordings are present.
- **Next: T589** (backend-developer, P2) applies v2's three edits:
  - E-A1 in `validation-gates`
  - E-B1a in `code-review`
  - E-B1b in `tech-lead`
- **O1** is ruled in plan-105 (T590).

## 5. Completion (2026-10-08)

- **T589 is merged** (MR !500, `develop` `fad9580`). E-A1, E-B1a and E-B1b were applied verbatim, and the
  orchestrator verified them independently. Condition C1 is satisfied.
- **Root drift** is 20 declared paths. The next root refresh needs the user's approval.
- **plan-104 is complete.** O1 continues in plan-105.
