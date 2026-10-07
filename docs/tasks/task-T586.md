# T586 — Rule FU-6 and FU-7 (security-gate criteria alignment) under ADR-008

**ID:** T586
**Owner:** solution-architect
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-07
**Based on:**
- `docs/plans/plan-103-security-gate-alignment.md`
- `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted): D1–D5, P1–P5, § Order of application,
  § Validation
- `docs/artifacts/conditional-pass-semantics-v4.md` (the P39 ruling, applied by T582): §1.7, §2 (where FU-6 is
  named), and its FU table
- `docs/artifacts/security-review-conditional-pass-semantics-v1.md` (SEC-008, the origin of FU-6; FU-7)
- `docs/artifacts/adr-008-rulings-p40-p43-v3.md` and v1 §5 and §10 (S4 is jointly satisfiable; FU-6 noted). Also
  `docs/artifacts/security-review-adr-008-rulings-n1-v1.md` (F2: the Security gate's own criteria were left to FU-6).
- The user's instruction of 2026-10-07: "Continue with the next best step". The recommended step was FU-6, with FU-7
  as its sibling from the same security review.

## 1. What and why

Two follow-ups from the P39 security review are still open. Both concern how the security gate's own documents state
criteria that tier 1 (`security-guidelines.md`, a stable instruction) already fixes.

- **FU-6 (SEC-008)** has three parts:
  - **(a) The SLA table.** `security-engineer.md` § severity table (around `:79–84` on `develop` `a9c4f04`) gives
    CRITICAL and HIGH "Must fix before release", MEDIUM "Fix within current sprint" and LOW "Fix within next sprint".
    Set this against:
    - `security-guidelines.md` § Security Review Workflow (`:182–185`): "`CRITICAL` and `HIGH` findings block merge
      until resolved", "`MEDIUM` findings must have a remediation plan before merge", and "`LOW` findings are tracked
      as technical debt";
    - `validation-gates` § Verdict Rules (the security paragraph): a medium's "fix is due under the track rule"; a low
      "is not a condition".
  - **(b) The `validation-gates` severity tiers** (§ Severity Definitions, now around `:76–81`; P39 cited them as
    `:74`). For example, `critical` includes "security vulnerability", while `high` says a security finding graded high
    blocks merge. Rule whether these tiers are misaligned with tier 1's `SECURITY:*` grading, and if so how.
  - **(c) The Security Gate Protocol.** `security-engineer.md` § Security Gate Protocol (around `:151–153`) does not
    name two things from P39: the omitted-required-control class, and the Q7 whole-project scope.
- **FU-7.** `receiving-code-review/SKILL.md` (around `:86`) says "`FAIL` findings block merge until resolved or
  escalated via blocker protocol." Under P39, escalation never lifts an excluded security FAIL (no waiver; "until
  resolved").

**Decision only.** Write exactly one file, your artifact. Edit no knowledge file, test, ledger or other document. A
Security Engineer reviews your ruling before anything is implemented. The user sees every P5 escalation.

## 2. Output

`docs/artifacts/security-gate-alignment-v1.md`, containing:

1. **A D5 record for each subject**: FU-6(a), FU-6(b), FU-6(c) and FU-7. Each record contains:
   - the subject;
   - both clauses, quoted verbatim with file and line **on `develop` `a9c4f04`**. Re-read every line: T582 and T585
     moved lines in `validation-gates`.
   - the Step A analysis, including the one-value test;
   - the step that fired. Expect Step B (P1) wherever `security-guidelines.md`'s declared scope covers the subject, but
     show it: quote the declared-scope text you rely on.
   - the amendment, as exact Before/After text with file and unique anchor, or "none";
   - an explicit statement that maturity was not relied on.
2. **Constraints on any amendment:**
   - No upward amendment (ADR-008 Validation 4): never edit `security-guidelines.md`, `AGENTS.md` or a command.
   - Never relax a check (ADR-007 §5).
   - Nothing may weaken `security-guidelines.md`, an Immutable Security Constraint or P39. P39 is an input and is not
     reopened.
   - If a fix seems to need a **command** change (for example `/security-audit`), do not propose it. Record it as a
     parked observation with its reason.
3. **Self-placement only at Step D** (user decision Q1). If Steps A–D do not decide a subject, escalate it under P5
   with a user question: the subject, both quotes, why the steps did not decide it, 2–4 options with their
   consequences, and your recommendation.
4. **Interactions.** State how each amendment sits with the P40 S2/S3 note N1 now in `validation-gates` ("strictest
   applies"; it deliberately does not cover the Security gate), and with `security-engineer`'s VERDICT Format
   Conditions line (`owner=…, remediation=…, deadline=…`).
5. **Golden coupling.** The orchestrator pre-computed it, with held-out pruned:

   | File | Open golden cases |
   |---|---|
   | `agents/security-engineer.md`, `skills/receiving-code-review/SKILL.md` | `discover-skills-registry-grounded-recommendation` only (a frozen registry snapshot; not coupled) |
   | `skills/validation-gates/SKILL.md` | `validate-workflow-gate-verdict-sources` (frozen fixture copy; its result reads only Gate Types and the Verdict Format) |
   | `commands/security-audit.md` (not to be amended) | `security-audit-coverage-consistency`, `security-audit-critical-not-fail`, `security-audit-verdict-fields-compliant` |

   For each amendment, state whether it would change a quote, a fixture or a result. Read cases by path under
   `tests/golden/open/<case>/`.
6. **An amendment list and a summary table**: subject, step, outcome, files.

## 3. Constraints

- **Read access:** the whole repo except `tests/golden/held-out/` (never open it), `.env*`, and credential and key
  files.
- **Write access:** your artifact only, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge.
- Quote verbatim, and mark omissions with "…". Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written: `docs/artifacts/security-gate-alignment-v1.md`, with `Based on:`.
2. Four D5 records. Each names one step, and its quotes are verbatim at `a9c4f04`.
3. No ruling relies on maturity, corpus counts, majority practice or golden-coupling convenience.
4. Every amendment has exact Before/After text, is neither upward nor relaxing, and states its golden coupling.
5. Every P5 escalation has a user question that meets §2.3.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). A P5 escalation is a ruling outcome, not a blocker. If ADR-008 cannot apply as
written, stop and report it as `unclear_requirements`.
