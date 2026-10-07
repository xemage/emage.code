# plan-102 — First ADR-008 rulings: P40 slices S2–S4 and P43

**Created:** 2026-10-07
**Based on:** the user's instruction of 2026-10-07, "Continue with the Recommended next step" (a ruling task for P40
S2–S4 and P43 under ADR-008, with no knowledge-file edits until the user approves);
`docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted); `docs/plans/plan-101-golden-quote-refresh.md` §4.
**Scopes:** `T584`, `T585`.

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

## 4. Outcome (2026-10-07)

- **T584 ruling.** The orchestrator verified it independently: 65 of 65 quotes are verbatim at `a54bbba`, and the
  anchors are unique. The ruling has three versions:
  - `adr-008-rulings-p40-p43-v1.md`: S2, S3 and S4 are jointly satisfiable at Step A, and P43 escalates under P5.
  - `-v2.md`: the exact P43 edits.
  - `-v3.md`: the final implementation input, with the Security Engineer's wording adopted.
- **The user's decisions (2026-10-07, verbatim option labels):**
  - P43: **"Evaluation decides, tighten-only (Recommended)"**.
  - P40 S2/S3: **"Strictest applies (Recommended)"**.
  - Notes: **"N1 + N2 + N3 (Recommended)"**.
- **Security Engineer phrase check of N1: PASS.** Three optional `SECURITY:LOW` wording points were all adopted in v3
  (`security-review-adr-008-rulings-n1-v1.md`).
- **Next: T585 (backend-developer, P2), the implementation task.** It applies the six edits in v3 (N1–N3; P1–P3 for P43) to
  `validation-gates`, `code-review`, `testing-strategy`, `rapid-prototyping`, `poc-evaluation` and
  `evaluation-agent`. It also runs `sync.mjs` and `generate-registry.py`, and either declares the root drift or
  refreshes it later with the user's approval.
  - No command, tier-1 file or golden case is touched, so no evaluator-hash change is expected.
  - `validate-workflow-gate-verdict-sources` keeps a frozen fixture of `validation-gates`. The fixture lags, and the
    result is unchanged.
- **Parked observations from v1 §12:** the scope-gaming mitigation's breadth (ADR-008 § Risks), and G1's own example
  being single-valued. Neither changes an outcome. FU-6 is noted, not decided.

## 5. Completion (2026-10-07)

- **T585 is merged** (MR !491, `develop` `f42ecec`). The six v3 edits are applied verbatim and verified independently.
  Root drift is 41 declared paths, and the next root refresh needs the user's approval. No golden or evaluator-hash
  change was needed (v16 still holds).
- **Erratum to `adr-008-rulings-p40-p43-v3.md` §4** (the artifact is immutable, so it is recorded here):
  - `the rules above included` occurs twice, on one line, so `grep -c` returns 1.
  - `is the PoC's outcome` has 0 hits in `rapid-prototyping` and 1 in `evaluation-agent`. P1's text reads
    "**The PoC's outcome.**" and "it is not the PoC's outcome".
- The queue is empty, and plan-102 is complete.
