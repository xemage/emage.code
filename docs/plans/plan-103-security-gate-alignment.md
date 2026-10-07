# plan-103 — Security-gate criteria alignment (FU-6, FU-7) under ADR-008

**Created:** 2026-10-07
**Based on:** the user's instruction of 2026-10-07, "Continue with the next best step" (the recommended step was
FU-6); `docs/plans/plan-102-adr-008-rulings-p40-p43.md` §5;
`docs/artifacts/security-review-conditional-pass-semantics-v1.md` (SEC-008, FU-7).
**Scopes:** `T586`.

## 1. Why now

FU-6 is the security gate's own criteria. The P40 S2/S3 rule ("strictest applies") deliberately left those out, and
the N1 security review pointed to FU-6 (F2). FU-7 comes from the same P39 security review. Both bring the security
gate's documents into line with `security-guidelines.md`.

## 2. Sequence

1. **Ruling: T586** (solution-architect, P2, decision only). One artifact,
   `security-gate-alignment-v1.md`, with a D5 record for each of FU-6(a), FU-6(b), FU-6(c) and FU-7.
2. **Orchestrator verification.** Re-check the quotes, confirm the step and its declared-scope text, and confirm that
   no amendment is upward or relaxing.
3. **Security Engineer review** of every amendment. All of them touch security criteria.
4. **User**: every P5 escalation, plus any amendment that needs a choice.
5. **Implementation**: a separate task once steps 2–4 are done.

## 3. Not in scope

- P39, the P40 rulings and the verdict format are inputs and are not reopened.
- No command is amended (`/security-audit` included). A finding that needs a command change is parked.
- No root refresh. That needs the user's approval; drift is currently 41 declared paths.
