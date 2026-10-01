# plan-096 — Reconcile the validation-gate verdict formats and gate definitions (P37)

**Created:** 2026-10-01
**Based on:** `docs/plans/plan-093-validate-workflow-repair.md` §4 (P37); `docs/plans/plan-095-user-decisions-p34-p36-root-refresh.md`.
**Scopes:** `T572`.

## 1. Why P37 next

The queue is empty, and the root drift is cleared. P37 is the largest open consistency item that needs no decision
from the user up front. The orchestrator's survey found it wider than the three findings (F1–F3) T566 recorded:
- seven places define a gate verdict: one canonical block in the stable `validation-gates` skill, four one-line
  `[VERDICT] gate=…` markers in other skills, a tech-lead block, and a release-notes section;
- they use five gate-name vocabularies;
- `project-planning` still calls plan approval a VERDICT gate, which contradicts the user's P36 decision.

Nothing parses these markers, no golden case asserts them, and the one coupled case reads a frozen copy, so the
stakes are clarity for the agents that follow these documents, not test breakage.

## 2. Sequence

1. **`T572`** (Solution Architect, judgment, decision only). Prefer a reconciling reading that needs no ranking.
   Where a ruling would require ranking one skill against another, or an agent against a skill, the task stops and
   reports it as a `dependency` on **P34b**, which is the user's question. Output:
   `docs/artifacts/gate-verdict-consistency-v1.md`.
2. **Follow-up:** implementation scoped from the artifact. It is expected to need no grant. If the
   `validation-gates` text changes, re-fixturing the `/validate-workflow` golden case is a separate, optional
   provenance fix that needs a grant and a user-authorized baseline.

The task is **P2**.

## 3. Parked items carried

- P32, P33, P34b and P38.
- The `new-poc` `expect.py` docstring.
- Older P4–P27 items.
