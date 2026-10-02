# plan-097 — Resolve the PoC skill/command overlaps (P38)

**Created:** 2026-10-02
**Based on:** `docs/artifacts/poc-skills-alignment-v1.md` §7 and §10.3; `docs/plans/plan-096-gate-definition-consistency.md` §5.
**Scopes:** `T574`.

## 1. Why P38 next

The queue is empty. The user has not yet decided the two items that need them:
- **P39**, whether CONDITIONAL_PASS allows a merge. Resolving it may need a held-out read grant.
- **P34b**, the authority ADR for agents and skills.

P38 is the largest remaining item the orchestrator can scope without user input. It finishes the PoC-track
consistency work begun in plans 092 and 094. Seven overlaps remain between the PoC skills and `/evaluate-poc` or
`AGENTS.md`, among them two verdict shapes and two handoff checklists for one evaluation.

## 2. Sequence

1. **`T574`** (Solution Architect, judgment, decision only). Prefer a reconciling reading, as in T572. Any item
   that needs a skill ranked against a command is escalated as a P34b `dependency`. Output:
   `docs/artifacts/poc-skill-command-overlaps-v1.md`.
2. **Follow-ups**, scoped from the artifact:
   - edits to the experimental skills, which need no grant;
   - an amendment to the stable `/evaluate-poc`, only if the ruling compels one. That would also change its golden
     case and need a grant plus a v16 baseline authorized by the user.

All tasks are **P2**.

## 3. Parked items carried

- **Waiting on the user:** P39, P34b, and P40, which depends on P34b.
- **Other parked items:** P32, P33, P41.
- **Also outstanding:** the `new-poc` docstring, and the 33-path root drift. Clearing the drift needs a refresh the
  user approves.
