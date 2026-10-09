# plan-114 — Placeholder flag for scanner findings (L-3) and the AGENTS.md naming conflicts

**Created:** 2026-10-09
**Based on:** the user's decisions of 2026-10-09 (Q3: "A - it must be possible though to flag a finding as placeholder, so it does not block"; Q4: "C - but do not forget / note the cosmetics"; "go");
`docs/artifacts/security-review-poc-security-audit-code-v1.md` (L-3);
`docs/plans/plan-112-parked-note-cleanup.md` §2; `docs/artifacts/path-conventions-v3.md` §8 (O1, O2, O5).
**Scopes:** `T606`, `T607`, `T608`, `T609`, `T610`.

## 1. Why now

plan-113 is complete. Two user decisions are waiting:

- **Q3.** The scanner stays strict, so a placeholder such as `password=changeme` is reported like any other secret. The user also
  wants a way to flag a finding as a placeholder so that it does not block. How that is done is a design question.
- **Q4.** Three notes conflict with tier-1 text (`AGENTS.md`) and can mislead agents. They need rulings.

## 2. Sequence

1. **T606** and **T607** (both solution-architect, decision only, independent of each other): each writes one artifact that
   ends in at most one user question.
2. Orchestrator verification. T606 gets a Security Engineer review of every amendment.
3. The user decides. Implementation is separate tasks.

## 3. Cosmetics to carry (the user said not to forget them)

- `poc-orchestrator:102` indentation (P33 O4): cosmetic. Fixing it forces a root refresh, so it rides along with the
  implementation of T607's decision, or with the next change to that file.

## 4. Not in scope

The other plan-112 §2 notes (CI's third `release-notes.md`, P41 O2/O3/O4, the P33 O1/O2/O5/O6 rulings) stay parked.
T605 (SEV-1..SEV-6 plus three pins) stays unscheduled.

## 5. Outcome of the rulings (2026-10-09)

- **T606** took three ruling versions: Security Engineer FAIL on v1 (HIGH: an "ephemeral local instance" clause would have made a working credential flaggable), FAIL on v2 (HIGH: the scanner spec for the label lacked the all-matches rule), CONDITIONAL_PASS on v3 (0 high, 3 medium, 5 low, all carried into the implementation tasks).
- **User decisions** (AskUserQuestion, verbatim labels): T606 Q1 "You confirm each flag (Recommended)"; T606 Q2 "Remove skip, label 3 shapes (Recommended)"; T607 O1 "Amend coding-standards (Recommended)"; T607 O2+O5 "Apply both (Recommended)".
- **Implementation:** T608 (agent text E-P1, E-O1, E-P2), then T609 (scanner E-S2, contract v3) and T610 (naming edits; K-1 indentation cosmetic) in parallel, each reviewed before merge, then one root refresh.
- **Open observation:** `checkpoint-protocol/SKILL.md` uses a third checkpoint name (`checkpoint-<N>.md`) against its own `:44` (naming ruling O7); not ruled, stays parked.
