# plan-107 — Remaining verdict renderings and editorial items (P41, G3–G9)

**Created:** 2026-10-08
**Based on:** the user's instruction of 2026-10-08, "Continue with the next best step" (the recommended step was
P41); `docs/artifacts/gate-verdict-consistency-v1.md` §13.3; `docs/plans/plan-106-golden-residual-staleness.md` §3.
**Scopes:** `T593`.

## 1. Why now

P41 is the last parked item from the gate-verdict review (T572). The rulings since then (P39, P40/P43, FU-6/FU-7,
SEC-T586-07, O1) have settled the verdict criteria and the security grading. That leaves the renderings, the release
executor (G4), the release-notes path (G5), the second vocabularies (G6) and the `project-planning` defects (G7).

## 2. Sequence

1. **T593 (solution-architect, P2, decision only):** one artifact with a D5 record per item G3–G9.
2. **Orchestrator verification.** If any amendment touches security criteria, a **Security Engineer review** follows.
3. **The user decides** every P5 escalation, including any command change (G4 is likely).
4. **Implementation** is a separate task. If it changes a golden quote or fixture, it also needs a protected-path
   grant and a user-authorized v18.

## 3. Not in scope

- All earlier rulings are inputs.
- The plan-path parts of G5 and G7 may be deferred to P32.
- P33, P44 and L4/X5 stay parked.
