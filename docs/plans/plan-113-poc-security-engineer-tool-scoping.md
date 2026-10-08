# plan-113 — Tool scoping for `poc-security-engineer` (L4/X5)

**Created:** 2026-10-08
**Based on:** the user's instruction of 2026-10-08, "Continue with the next best step";
`docs/artifacts/poc-security-reviewer-blocking-v3.md` §12 X5; plan-099.
**Scopes:** `T602`.

## 1. Why now

Every substantive rule item is closed. What remains of real value is a hardening item: the PoC security reviewer holds
an unrestricted `execute` tool, while the production `security-engineer` holds only fixed-argv audit tools.

## 2. Sequence

1. **T602** (solution-architect, decision only): D5 records, the list of execution-dependent statements, the test
   coupling, and one user question.
2. Orchestrator verification, then a Security Engineer review of every amendment.
3. The user decides the tool grant.
4. Implementation as a separate task. It may include new runtime code (a fixed-command git-history tool) only if the
   user chooses it.

## 3. Not in scope

The notes in plan-112 §2, and the other X-items (X1–X4, X6–X8).
