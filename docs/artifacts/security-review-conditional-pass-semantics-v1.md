# Security reviews of the CONDITIONAL_PASS ruling (T580 / P39)

> Filename: `security-review-conditional-pass-semantics-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer. Every review was read-only, and this agent has no write tools.
- **Recorded by**: orchestrator, who transcribed the reviewer's three hand-backs from 2026-10-02.
- **Reviewed**: `docs/artifacts/conditional-pass-semantics-v1.md`, then `-v2.md`, then `-v3.md`, each checked against
  `security-guidelines.md`, `AGENTS.md` § Validation Gates and the PoC security rules (O1, plan-099).
- **Outcome applied in**: `docs/artifacts/conditional-pass-semantics-v4.md`, which supersedes v1–v3.

## Round 1: v1, **FAIL as scoped**

Batch A was sound and weakened nothing. However, Batches B and C were optional, which left two HIGH routes open:

- **SEC-001 (HIGH)**: a Tech Lead waiver could override a security FAIL (`code-review:150`, `:159`, `tech-lead:111`).
  That made production laxer than PoC.
- **SEC-002 (HIGH)**: `/security-audit` forced FAIL only on CRITICAL, so a HIGH could reach CONDITIONAL_PASS at the
  Security gate itself.
- **SEC-003 (MEDIUM)**: the security exclusion was keyed to the `SECURITY:` label, so a security issue raised under
  another label escaped it. Fix: define security findings by subject.
- **SEC-004 (MEDIUM)**: the omitted-control class applied only on PoC. Production was laxer (Q3).
- **SEC-005 (MEDIUM)**: `testing-strategy:240` treated "high findings have mitigations" as a route to
  CONDITIONAL_PASS.
- **SEC-006, SEC-007 (LOW)**: due points, and the remediation plan carried with each condition.
- **SEC-008 (LOW)**: the `security-engineer` SLA table and the `validation-gates:74` tiers. Follow-up FU-6.

User decisions, 2026-10-02:

- **Q1**: "Keep it, except for security (Recommended)".
- **Q2**: "Recorded by handoff (Recommended)".
- **Q3**: "Both tracks (Recommended)".
- **Q4**: "Next release cycle". The user chose this over the orchestrator's "before deployment".

## Round 2: v2 delta, **CONDITIONAL_PASS**

SEC-001 and SEC-002 were met: C1/C3/C4 and B2–B4 became required. SEC-003 to SEC-007 were met, except SEC-004 in
B1. With Q4 applied as worded, no security finding of any grade can ship through a Release-gate CONDITIONAL_PASS.

New findings:

- **SEC-009 (MEDIUM)**: the PASS rows did not exclude the grade-independent classes.
- **SEC-010 (MEDIUM)**: B1 was missing the Q3 omitted-control class.
- **SEC-012 (MEDIUM)**: the Release gate's executor did not know the Q4 security exclusion. Its risk-acceptance
  route (`release-manager:45`, `:181`, `:222`; `/prepare-release:69`) could let a security MEDIUM ship unfixed. The
  orchestrator widened the scope to cover it.
- **SEC-011, SEC-013 to SEC-017 (LOW)**:
  - SEC-011: a waived MEDIUM keeps its plan.
  - SEC-013: the template due point now carries the security exception.
  - SEC-014: a security LOW is not a condition.
  - SEC-015: adjacency to the change counts as code under review.
  - SEC-016: classification is by subject.
  - SEC-017: B2b is required.

## Round 3: v3 phrase check, **CONDITIONAL_PASS**

Every v2 condition was adopted. The orchestrator's mechanical diff showed each relayed After text present verbatim.
Nothing lets a security finding of any grade, or a constraint breach, merge or ship.

New findings:

- **SEC-018 (LOW, condition)**: the architect's own R5 (`prepare-release:61`) sorted findings by grade only. As a
  result, a security LOW would block releases, and a constraint breach graded MEDIUM would take the "fix before
  ships" branch.
- **SEC-019 (LOW, condition)**: B1 lacked the adjacency rule, so one decision could have two values.
- **SEC-020, SEC-021 (LOW, optional)**: C4's waiver-plan clause, and an A6 wording clarification.

User decisions, 2026-10-02:

- **Q7**: "Whole project (Recommended)". With no change under review, the whole project is the code under review.
- **Q8**: "Yes, block (Recommended)". A pre-existing security HIGH blocks unrelated merges; this is the fail-safe
  default as written.

The reviewer said a delta review of v4 was not required: an orchestrator phrase check that the corrected texts
appear exactly as given would suffice. That check passed. SEC-018 to SEC-021 and Q7 appear byte-for-byte in v4,
`conditional-pass-semantics-v4.md` §16.

## Follow-ups carried

- **FU-2 (protected path; needs a grant and a user-authorized baseline)**: refresh stale quotes in three open golden
  cases:
  - `code-review-conditional-pass-conditions-gap`
  - `security-audit-critical-not-fail`
  - `prepare-release-conditional-pass-conditions-gap`

  Each case's `check()` reads only its fixture, so no result changes.
- **FU-6 (SEC-008)** and **FU-7** (`receiving-code-review:86`: escalation never lifts an excluded security FAIL).
