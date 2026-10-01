# plan-093 — Repair `/validate-workflow` (P28), decided before it is amended

**Created:** 2026-10-01
**Based on:** `docs/plans/plan-090-golden-wave-3.md` §2 (P28); `docs/plans/plan-092-poc-contract-amendments.md` §4;
golden case `validate-workflow-gate-verdict-sources`.
**Scopes:** `T566`; follow-ups `T567`, `T568`, `T569` (§4).

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

## 4. T566's decision and the follow-ups

`validate-workflow-gate-resolution-v1.md` rules under ADR-007 branch 1, same-file prong. Step 5's list becomes the `validation-gates` skill's five gate types in pipeline order. The Architecture gate replaces the briefing, and plan approval leaves the list. Steps 6 and 11 and the Failure mode are unchanged. In §9 the orchestrator verified the artifact's unverified claims and ruled that the 6 → 5 gate change is not a Validation 1 weakening, because the check gains completeness and ordered list-fidelity predicates. It also parked P36 and P37.

| Task | Covers | Protected paths? | Owner |
|---|---|---|---|
| `T567` | FU-1: amend step 5 (lines 25–32), regenerate, and declare the 6 new root drift paths | No | Backend Developer |
| `T568` | FU-2: realign the golden case, which flips to `expected_pass` | **Yes**: §5 grant for one case directory; user-authorized **v15** | QA Engineer |
| `T569` | FU-3: promote `/validate-workflow` to `stable` (commands 14/5), after an orchestrator dry run | No | Backend Developer |

They run in sequence, one MR each. T567 alone leaves the case red, which is already its state, so unlike plan-092 there is no stale-green window.

**Parked (new):**
- **P36:** should `/validate-workflow` check plan approval as a non-gate? A scope question for the owner and the Product Owner; it interacts with P10. **Trigger:** the next task touching `/validate-workflow`'s scope.
- **P37:** gate-definition inconsistencies outside the command:
  - the integration gate has two VERDICT formats (`validation-gates` `## Gate Verdict` vs `testing-strategy` `[VERDICT] gate=qa-validation`);
  - the orchestrator's Core Workflow never names an "Implementation Gate";
  - the Architecture gate's executor differs between the skill (Tech Lead) and the orchestrator (Tech Lead + Security Engineer).

  **Trigger:** the next task touching `validation-gates`, `testing-strategy` or `orchestrator.md`.
- `validation-gates`' `docs/plans/plan-<feature>.md` joins **P32**.
