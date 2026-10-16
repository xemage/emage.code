# T588 — Rule SEC-T586-07 (security-finding grading by any executor; per-MR OWASP run) under ADR-008

**ID:** T588
**Owner:** solution-architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-08
**Based on:**
- `docs/plans/plan-104-security-finding-grading-and-owasp-run.md`
- `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted): D1–D5, P1–P5, § Order of application,
  § Validation
- `docs/artifacts/security-review-security-gate-alignment-v1.md`, SEC-T586-07 (the origin of this task)
- `docs/artifacts/security-gate-alignment-v2.md` (FU-6 and FU-7, applied by T587) and
  `docs/artifacts/conditional-pass-semantics-v4.md` (P39). Both are inputs and are not reopened.
- The user's instruction of 2026-10-08: "Next item: continue as recommended". The recommended item was SEC-T586-07.

## 1. What and why

The Security Engineer's review of T586 recorded two pre-existing gaps (`SECURITY:LOW`, observations):

- **(a) Grading by an executor who is not the Security Engineer.**
  - `validation-gates` § Verdict Rules (`:70`) says a security finding is "any finding in the security category,
    whichever gate or executor raises it, graded on the `security-guidelines.md` § Security Review Workflow scale".
  - Tier 1 names the four grades but does not define them.
  - The only definitions are in `security-engineer.md` § Findings Classification (`:75–86`).
  - Nothing tells a Tech Lead (Implementation gate) or a QA Engineer (Integration gate) which definitions to grade a
    security finding by.

  Rule whether a gap or contradiction exists under ADR-008. If it does, rule where the pointer belongs: for example,
  the reviewer's suggestion of a `validation-gates` clause "graded with the definitions in agent `security-engineer`
  § Findings Classification".
- **(b) The per-MR OWASP run.**
  - `security-guidelines.md` § Security Review Workflow step 1 (`:180`) reads: "Run OWASP Top 10 checklist against
    every merge request touching security-sensitive code".
  - `validation-gates` § Gate Types (`:28`) and § When to Use (`:17`) trigger the Security gate "Before any release".
  - `code-review/SKILL.md` § Security (OWASP) (around `:34–39`) partly covers the checklist at the Implementation
    gate.
  - Nothing assigns the per-MR run.

  Rule whether the documents contradict each other or are only silent. If tier 1's step 1 needs an owner, rule which
  document must say so, and how. This is the kind of question that may need **P5 escalation**: assigning an owner is
  a choice, not a reading, unless some document's own text places it.

**Decision only.** Write exactly one file, your artifact. A Security Engineer reviews every amendment before
implementation. The user decides every P5 escalation.

## 2. Output

`docs/artifacts/security-finding-grading-and-owasp-run-v1.md`, containing:

1. **A D5 record for (a) and one for (b).**
   - Quote every clause verbatim with file and line **on `develop` `7ec903a`**, and re-read each line.
   - Give the Step A analysis, including the one-value test, and name the step that fired.
   - Quote the declared-scope text for P1–P3.
   - Give the amendment as exact Before/After text with a unique anchor, or write "none".
   - State explicitly that maturity was not relied on.
2. **Silence is not a contradiction.** If a subject is a gap rather than a conflict, say so. Rule whether ADR-008
   decides how to fill it, or whether filling it is a choice for the user (P5).
3. **Constraints:**
   - No upward amendment: never edit `security-guidelines.md`, `AGENTS.md` or a command.
   - Never relax a check, and never weaken a security rule.
   - P39 and FU-6/FU-7 are inputs.
   - If a fix would need a **command** change (for example `/code-review` or `/security-audit`), park it with a reason.
4. **Self-placement only at Step D** (the user's Q1 decision). For each P5 escalation, write a user question: the
   subject, the quotes, why the steps did not decide it, 2–4 options with their consequences (including workload and
   which agent runs what), and your recommendation.
5. **Golden coupling.** The orchestrator pre-computed it, with held-out pruned. Read the cases by path under
   `tests/golden/open/<case>/`.

   | File | Open golden cases |
   |---|---|
   | `skills/validation-gates/SKILL.md` | `validate-workflow-gate-verdict-sources` (frozen fixture copy; `check()` reads only Gate Types and the Verdict Format's `**Gate:**`, plus "Every gate MUST produce a verdict") |
   | `skills/code-review/SKILL.md`, `commands/code-review.md` | `code-review-conditional-pass-conditions-gap`, `code-review-fail-blocker-details` |
   | `agents/orchestrator.md` | `validate-workflow-gate-verdict-sources` (cited) |
   | `commands/security-audit.md` (not to be amended) | `security-audit-coverage-consistency`, `security-audit-critical-not-fail`, `security-audit-verdict-fields-compliant` |
   | `agents/{tech-lead,qa-engineer,security-engineer}.md`, `skills/testing-strategy/SKILL.md` | none |

   **Warning:** any edit to `validation-gates` § Gate Types touches a table that `validate-workflow-gate-verdict-sources`
   checks. Its fixture is frozen, so the result does not change, but say so explicitly.
6. **An amendment list, expected hit counts and a summary table.** For each count, state whether it is a line count
   or an occurrence count. Never count a substring that your own After text splits or negates.

## 3. Constraints

- **Read access:** the whole repo, except: never open `tests/golden/held-out/`, and never read `.env*`, credential
  or key files.
- **Write access:** your artifact only, plus this brief's `**Status:**` line (`in_review` when done).
- **No shell:** you have none. Do not commit, push or merge.
- **Quoting:** quote verbatim and mark omissions with "…". Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written: `docs/artifacts/security-finding-grading-and-owasp-run-v1.md`, with `Based on:`.
2. There are two D5 records, each naming one step, with quotes verbatim at `7ec903a`.
3. No ruling relies on maturity, corpus counts, majority practice or golden-coupling convenience.
4. Every amendment has exact Before/After text, is neither upward nor relaxing, and states its golden coupling.
5. Every P5 escalation has a user question that meets §2.4.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). A P5 escalation is a ruling outcome, not a blocker.
