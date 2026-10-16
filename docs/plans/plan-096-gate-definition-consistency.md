# plan-096 — Reconcile the validation-gate verdict formats and gate definitions (P37)

**Created:** 2026-10-01
**Based on:** `docs/plans/plan-093-validate-workflow-repair.md` §4 (P37); `docs/plans/plan-095-user-decisions-p34-p36-root-refresh.md`.
**Scopes:** `T572`; follow-up `T573` (§4).

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

## 4. T572's decision and the follow-up

`gate-verdict-consistency-v1.md` reconciles the formats **without ranking any documents**: two MUSTs that can both be satisfied, one verdict per gate, and each skill's own declared scope. As a result, P34b is not triggered.

- The one-line `[VERDICT]` markers in `code-review` and `testing-strategy` sit **alongside** the canonical `validation-gates` block.
- Gate names map onto the skill's five kinds (`code-review` → implementation, `qa-validation` → integration).
- `project-planning` is amended to match P36.
- `tech-lead` and the orchestrator each get a one-line clarification.
- `validation-gates` and `/validate-workflow` are untouched, so no golden case needs re-fixturing and the baseline does not change.

In §13 the orchestrator verified the claims that dispatch depends on and accepted E1–E7.

| Task | Covers | Protected paths? | Owner |
|---|---|---|---|
| `T573` | FU-1: E1–E7 in 3 skills and 2 agents, regeneration, root-drift declarations | No | Backend Developer |

**Parked (new):**
- **P39:** whether CONDITIONAL_PASS allows a merge. This is a behavioural conflict. An ADR-007 ruling on `/code-review` may need a held-out read grant, which needs the user's approval.
- **P40:** differing verdict *criteria*. Depends on P34b.
- **P41:** remaining verdict renderings and editorial items (G3–G9).

## 5. Outcome (2026-10-01)

P37 is resolved. T573 (!465) applied E1-E7, so the verdict formats are now reconciled without ranking any document above another. The 33 root paths stay declared until the next user-approved root refresh. **P39** (whether CONDITIONAL_PASS allows a merge) is the most consequential open item. Resolving it may need a held-out read grant, which is the user's call.
