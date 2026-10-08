# plan-105 — Two security grade definition sets (O1)

**Created:** 2026-10-08
**Based on:** the user's decision of 2026-10-08, O1: "Rule it next (Recommended)";
`docs/artifacts/security-finding-grading-and-owasp-run-v1.md` (O1);
`docs/artifacts/security-review-security-finding-grading-v1.md` (observations).
**Scopes:** `T590`, `T591`.

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

## 4. Outcome (2026-10-08)

- **The T590 ruling** (`security-grade-definitions-v1.md`):
  - O1 is a real contradiction under `/security-audit`, and it escalated under P5. Amending the agent to follow the
    command would lower grades, and overriding the command breaks P2.
  - The orchestrator verified 46/46 quotes and the anchors.
  - The orchestrator also redacted a held-out sibling case name that the artifact had copied from pre-T411 open briefs.
    Nothing was read from held-out, and the isolation test passes.
- **User decision** (2026-10-08, verbatim option label): Q-O1 **"Higher of the two (Recommended)"**, i.e. option A,
  E-O1a and E-O1b.
- **Security Engineer review: CONDITIONAL_PASS** (`security-review-security-grade-definitions-v1.md`). Its conditions
  were adopted verbatim in `security-grade-definitions-v2.md`:
  - C1 (MEDIUM): the command side also takes its highest grade, which makes option A's guarantee hold.
  - C2 (LOW): the floor pointer reads "for example".
  - C3 (LOW): the agent's SLA paragraph still applies.
- **The sequencing guard is satisfied.** T589 is merged, and its floor sentence is on `develop`.
- **Next: T591** (backend-developer, P2) applies E-O1a to the stable `/security-audit` command and E-O1b to
  `security-engineer`. No golden quote, fixture or result changes.
