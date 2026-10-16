# plan-103 — Security-gate criteria alignment (FU-6, FU-7) under ADR-008

**Created:** 2026-10-07
**Based on:** the user's instruction of 2026-10-07, "Continue with the next best step" (the recommended step was
FU-6); `docs/plans/plan-102-adr-008-rulings-p40-p43.md` §5;
`docs/artifacts/security-review-conditional-pass-semantics-v1.md` (SEC-008, FU-7).
**Scopes:** `T586`, `T587`.

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

## 4. Outcome (2026-10-08)

- **T586 ruling** (`security-gate-alignment-v1.md`):
  - All four subjects (FU-6(a), FU-6(b), FU-6(c) and FU-7) were decided at Step A: the clauses are jointly
    satisfiable. Nothing escalated under P5, so there is no user question.
  - The orchestrator verified the ruling: all 45 quotes are verbatim, every anchor is unique, no other knowledge file
    restates the clauses, and no test asserts them.
- **Security Engineer review: CONDITIONAL_PASS** (`security-review-security-gate-alignment-v1.md`).
  - C1 and C2 (`SECURITY:MEDIUM`) are the FA1 and FB1 example sentences, which could have routed excluded classes to
    "plan" or "debt".
  - SEC-T586-03 to 06 are `SECURITY:LOW`.
  - All were adopted verbatim in `security-gate-alignment-v2.md`, together with the three formerly optional items.
    SEC-T586-07 (a) and (b) are parked as observations.
- **Orchestrator check of v2.** All seven edits apply to scratch copies, and each Before occurs once. The reviewer's
  wording is present verbatim for C1, C2 and 03–06. The superseded wording is gone.
- **Next: T587** (backend-developer, P2) applies v2's seven edits verbatim:
  - FA1, FC1, FC3 and FC2 in `agents/security-engineer.md`;
  - FB1 and FD1 in `skills/validation-gates/SKILL.md`;
  - F7 in `skills/receiving-code-review/SKILL.md`.

  It regenerates the mirrors and the registry and declares the root drift. No golden case, command or tier-1 file is
  touched.

## 5. Completion (2026-10-08)

- **T587 is merged** (MR !495, `develop` `38b043e`). The seven v2 edits were applied verbatim and verified
  independently, and conditions C1 and C2 are satisfied. FU-6 and FU-7 are closed.
- **Root drift is 54 declared paths.** The next root refresh needs the user's approval.
- **SEC-T586-07** stays parked as observations: (a) how an executor that is not the Security Engineer grades a security
  finding; (b) the per-MR OWASP run against the Security gate's "Before any release" trigger.
- The queue is empty, and plan-103 is complete.
