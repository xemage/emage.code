# plan-097 — Resolve the PoC skill/command overlaps (P38)

**Created:** 2026-10-02
**Based on:** `docs/artifacts/poc-skills-alignment-v1.md` §7 and §10.3; `docs/plans/plan-096-gate-definition-consistency.md` §5.
**Scopes:** `T574`; follow-up `T575` (§4).

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

## 4. T574's decision and the follow-up

`poc-skill-command-overlaps-v1.md` rules on all seven items without ranking one document over another. Every edit (E1–E12) falls on an experimental skill. `/evaluate-poc` is untouched, so no golden case, grant or v16 baseline is needed.

- F1: the skill's marker accompanies the command's block.
- F2: the two checklists are complementary; the combined list applies.
- F3: amended. "Promoted" becomes "inventoried", with a disposition.
- F4: clarified. The skill proposes; the orchestrator creates.
- F6: the marker is a status report to the orchestrator.
- F7: `## Rails` sections are written now.
- F8: made explicit.

In §16 the orchestrator verified the claims and accepted E1–E12.

| Task | Covers | Protected paths? | Owner |
|---|---|---|---|
| `T575` | FU-1: E1–E12 in the three PoC skills, regeneration, 21 root-drift declarations | No | Backend Developer |

**Parked (new):**
- **P42 (security, scheduled next):** the stable `poc-guidelines.md` and `rapid-prototyping` present "No input validation" as a model shortcut, which contradicts `security-guidelines` Immutable Constraints 3–4. `security-guidelines` states that it supersedes, so no P34b ranking is needed.
- **P43:** two binary verdicts for one PoC. Joins P40 (depends on P34b).
- **P44:** the `evaluate-poc` golden case expects numbered backlog lines, but the skill's template uses a table. This is a protected path; batch it with the `new-poc` docstring.
