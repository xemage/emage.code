# plan-102 — First ADR-008 rulings: P40 slices S2–S4 and P43

**Created:** 2026-10-07
**Based on:** the user's instruction of 2026-10-07, "Continue with the Recommended next step" (a ruling task for P40
S2–S4 and P43 under ADR-008, with no knowledge-file edits until the user approves);
`docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted); `docs/plans/plan-101-golden-quote-refresh.md` §4.
**Scopes:** `T584`.

## 1. Why now

ADR-008 made P40 and P43 schedulable (plan-100 §5). The queue is empty, and nothing else blocks them. These are the
first rulings made under ADR-008, so they also exercise the ADR's Validation items 3, 5 and 6 for the first time.

## 2. Sequence

1. **T584 (solution-architect, P2, decision only).** One artifact, `adr-008-rulings-p40-p43-v1.md`, with a D5 record
   for each of P40 S2, S3, S4 and P43, and a user question for every P5 escalation. S1 is settled by T580/T582.
2. **Orchestrator verification.** Every quote is re-checked against `develop`. Each record names exactly one step.
   Every Step D outcome quotes a self-placement sentence. No ruling cites maturity.
3. **User decisions.** Every escalation is put to the user verbatim. Amendments, if any, are listed for approval.
4. **Review.** If any amendment touches security criteria (likely only S4), a Security Engineer reviews it before
   implementation.
5. **Implementation**, a separate task, scoped only after steps 3–4. If it changes a golden quote or fixture, it needs
   a protected-path grant and a user-authorized evaluator-hash v17.

## 3. Not in scope

- P39 and the verdict format (T572) are inputs and are not reopened.
- Also out of scope: FU-6, FU-7, FU-8, P32, P33, P41, P44 and L4/X5.
- If a ruling bears on FU-6 (the `security-engineer` SLA table against the `validation-gates` tiers), the artifact may
  note it, but does not decide it.
