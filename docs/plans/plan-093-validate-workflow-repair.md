# plan-093 — Repair `/validate-workflow` (P28), decided before it is amended

**Created:** 2026-10-01
**Based on:** `docs/plans/plan-090-golden-wave-3.md` §2 (P28); `docs/plans/plan-092-poc-contract-amendments.md` §4;
golden case `validate-workflow-gate-verdict-sources`.
**Scopes:** `T566`.

## 1. Why P28 next

The queue is empty after plan-092. P28 is the only thing blocking `/validate-workflow`, the last `experimental`
command with a red golden case of its own. Its trigger, the wave-3 promotion run, fired with T562.

**The `orchestrator` agent remains blocked either way.** A probe on `develop` (`orchestrator` flipped to `stable` in a
throwaway worktree) shows it fails criteria 3 and 7 on `/plan`'s `plan-real-doc-header-drift`. That is
ADR-007 verdict A, which `command-contract-resolution-v1.md` keeps red by design. P28 is a command repair, not an
agent promotion.

## 2. Sequence, same pattern as plan-091/092

1. **`T566`** (Solution Architect, judgment, decision only): adjudicate under ADR-007 which exit repairs step 5 against
   step 6. The case brief names three candidates. Output: `docs/artifacts/validate-workflow-gate-resolution-v1.md`.
2. **Follow-ups, scoped from T566's artifact:**
   - amend the command (no protected paths);
   - realign the golden case. This flips `known_failing` to `expected_pass` if the repair works. It needs a
     protected-path grant and a user-authorized **v15** baseline.
   - run a promotion pass for `/validate-workflow` if its case turns green.

Like plan-092, every task is **P2**, for the same reason (plan-092 §3).

## 3. Parked items carried

Unchanged from plan-092 §4:
- P32–P35;
- the `new-poc` `expect.py` docstring that still calls P11 "parked";
- the 36-path root drift. Clearing it needs user approval at the time.
