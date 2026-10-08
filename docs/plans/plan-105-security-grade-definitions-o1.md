# plan-105 — Two security grade definition sets (O1)

**Created:** 2026-10-08
**Based on:** the user's decision of 2026-10-08, O1: "Rule it next (Recommended)";
`docs/artifacts/security-finding-grading-and-owasp-run-v1.md` (O1);
`docs/artifacts/security-review-security-finding-grading-v1.md` (observations).
**Scopes:** `T590`.

## 1. Subject

`security-engineer.md` § Findings Classification (`:81–84`) and `/security-audit` § Severity Classification (`:42–46`)
define the four grades in different words. One finding can therefore get two grades. For example, a missing hardening
header is a "defense-in-depth gap" (MEDIUM) under the agent and a "Hardening recommendation" (LOW) under the command.
That moves the verdict between CONDITIONAL_PASS and PASS. Under T589's E-A1, every executor grades with the agent's
set.

## 2. Sequence

1. **T590** (solution-architect, P2, decision only): one artifact with a D5 record.
   - Under `/security-audit`, ADR-008 P2 and ADR-007 govern the command's output.
   - Any fix must **never lower a grade**.
   - A command amendment is possible only under ADR-007, which means a user decision. Any one-off choice escalates
     under P5.
2. Orchestrator verification, then a Security Engineer review of every amendment, then a user decision on every
   escalation.
3. Implementation as a separate task.

T590 runs in parallel with T589. Their file sets differ: T589 edits `validation-gates`, `code-review` and `tech-lead`,
while T590 reads `security-engineer` and `/security-audit` and edits nothing.

## 3. Not in scope

Everything already decided is an input: P39, FU-6/FU-7, the P40 rulings, and A1/B1.
