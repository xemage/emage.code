# T590 — Rule O1 (two security grade definition sets) under ADR-008 and ADR-007

**ID:** T590
**Owner:** solution-architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-08
**Based on:**
- `docs/plans/plan-105-security-grade-definitions-o1.md`
- `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted), especially P2, and
  `docs/decisions/ADR-007-command-contract-authority.md` (Accepted)
- `docs/artifacts/security-finding-grading-and-owasp-run-v1.md` (O1) and `-v2.md` (E-A1, which T589 is applying)
- `docs/artifacts/security-review-security-finding-grading-v1.md` (observations)
- The user's decision of 2026-10-08: O1, "Rule it next (Recommended)".

## 1. What and why

Two documents define the four security grades differently:

- `security-engineer.md` § Findings Classification (`:81–84`):
  - CRITICAL: "Actively exploitable, data breach risk, authentication bypass"
  - HIGH: "Significant vulnerability, requires specific conditions to exploit"
  - MEDIUM: "Moderate risk, defense-in-depth gap"
  - LOW: "Minor issue, best-practice deviation"
- `/security-audit` § Severity Classification (`:42–46`):
  - CRITICAL: "Actively exploitable, immediate remediation required"
  - HIGH: "Exploitable with moderate effort; …"
  - MEDIUM: "Potential risk; …"
  - LOW: "Hardening recommendation, add to backlog"

One finding can therefore get two grades. For example, a missing hardening header is MEDIUM under the agent and LOW
under the command, which moves the verdict between CONDITIONAL_PASS and PASS. T589's E-A1 makes every executor grade
with the agent's set (with the PoC floors kept).

Rule whether these two sets contradict each other under ADR-008. If they do, rule what decides it:

- **Under `/security-audit`**, P2 and ADR-007 govern the command's own output contract.
- A command clause can be amended only under ADR-007. Any such amendment is a user decision; never propose one as
  settled.
- **Any fix must never lower a grade.** This follows ADR-007 §5 ("Never resolve by relaxing a check") and the
  security rules.
- If no step decides, escalate under P5 with a user question that gives 2–4 options, their consequences and your
  recommendation.

**Decision only.** Write exactly one file, your artifact. A Security Engineer reviews every amendment, and the user
decides every escalation and any command change.

## 2. Output

`docs/artifacts/security-grade-definitions-v1.md`, containing:

1. **A D5 record.** It includes:
   - every clause quoted verbatim with file and line, **on the `develop` commit your worktree is on**;
   - the Step A analysis, with the one-value test;
   - the step that fired;
   - the declared-scope text;
   - the amendment, with exact Before/After and a unique anchor, or "none";
   - a statement that maturity was not relied on.
2. **The interaction with E-A1.** T589 is applying it in parallel; it is not in your worktree yet. Its final text is
   in `security-finding-grading-and-owasp-run-v2.md`.
3. **Golden coupling.** These open golden cases touch the files, with held-out pruned. Read each case by path under
   `tests/golden/open/<case>/`.
   - `/security-audit` is cited by `security-audit-coverage-consistency`, `security-audit-critical-not-fail` and
     `security-audit-verdict-fields-compliant`.
   - `security-engineer.md` is cited by no case.
   - For any command amendment, state whether a quote, a fixture or a result changes. A change to a golden quote
     needs a protected-path grant and a user-authorized evaluator-hash baseline.
4. **Hit counts.** Give the line count and the occurrence count for each. Do not count a substring that your own
   After text splits.
5. **A summary table.**

## 3. Constraints

- **Read access:** the whole repo, except: never open `tests/golden/held-out/`, and never read `.env*`, credential or
  key files.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- **No shell:** you have none. Do not commit, push or merge.
- **Quoting:** quote verbatim and mark omissions with "…". Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written: `docs/artifacts/security-grade-definitions-v1.md`, with `Based on:`.
2. It holds a D5 record that names one step, with quotes verbatim on the worktree's commit.
3. No amendment lowers a grade, is upward, or amends a command without a user decision.
4. Every P5 escalation has a user question that meets §1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). A P5 escalation is a ruling outcome, not a blocker.
