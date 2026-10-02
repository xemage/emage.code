# T580 — Make CONDITIONAL_PASS merge semantics consistent (P39), per the user's decision

**ID:** T580
**Owner:** Solution Architect
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-02
**Based on:**
- `docs/plans/plan-100-conditional-pass-and-authority-adr.md`
- `docs/artifacts/gate-verdict-consistency-v1.md` §13.3 (P39)
- `docs/decisions/ADR-007-command-contract-authority.md` (Accepted)
- `docs/artifacts/poc-security-reviewer-blocking-v3.md` (the O1 security blocking rules)

## 1. What and why

The documents disagree on whether a `CONDITIONAL_PASS` verdict allows a merge. **The user has decided the rule**
(2026-10-02, relayed verbatim):

> "CONDITIONAL_PASS allows merge with conditions tracked (closed before the next gate on production; PoC debt due by
> handoff). FAIL blocks. Security HIGH/CRITICAL and constraint breaches never qualify for CONDITIONAL_PASS. The
> experimental /code-review command and tech-lead agent get amended to match AGENTS.md." The user chose: **"Adopt it
> (Recommended)"**.

Your job is to turn this rule into exact amendments and to check that nothing else contradicts it. **Decision only**:
do not edit any file other than your artifact. A Security Engineer reviews the security part before anything is
implemented.

## 2. Facts verified by the orchestrator on `develop` `1682077`

**Agree with the rule (allow merge, track conditions)**
- `AGENTS.md:55`: "`CONDITIONAL_PASS` proceeds with tracked conditions added to the task list."
- `agents/orchestrator.md:44,221`: "track conditions in task list and proceed".
- `skills/code-review/SKILL.md:151`: "A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task …". This skill is stable.
- `skills/validation-gates/SKILL.md:67`: "… All conditions must be resolved before the next gate." This skill is stable.

**Contradict the rule (block merge)**
- `agents/tech-lead.md:97` (experimental): "**CONDITIONAL_PASS**: Code is acceptable with listed conditions that must be addressed before merge. Merge is blocked until conditions are resolved."
- `commands/code-review.md:51` (experimental): "If CONDITIONAL_PASS, list the conditions that must be met before merge."

**A security nuance to settle**
- `skills/validation-gates/SKILL.md:67` lets **HIGH findings with documented mitigations** through as `CONDITIONAL_PASS`.
- `security-guidelines.md` § Security Review Workflow says "`CRITICAL` and `HIGH` findings block merge".
- The user's rule says security HIGH and CRITICAL findings **never** qualify for CONDITIONAL_PASS.
- So `validation-gates`' HIGH-with-mitigation clause may only cover **non-security** HIGH findings. Specify the
  amendment, or the specialisation note, that makes this explicit.
- A **MEDIUM** security finding is a CONDITIONAL_PASS whose condition is a remediation plan due before merge, as
  `security-guidelines` § Security Review Workflow requires.

**Golden coupling**
- The open case `code-review-conditional-pass-conditions-gap` (status `known_failing`, `capability_gap`) quotes "list
  the conditions that must be met before merge" in its `brief.md` and in the `expect.py` docstring.
- Its `check()` tests only for a structured `**Conditions**:` field or `## Conditions` section, not merge
  semantics.
- An amended `/code-review:51` therefore makes those quotes **stale** but does **not** change the case's result.
  Updating the quotes is a protected-path edit, needing a grant and a baseline: report it as a follow-up and do not
  rule on it.
- Held-out cases are **not read**. The implementing task detects any held-out coupling through `scorecard.py --check`
  regressions, which do not reveal case content.

## 3. What to decide

1. Give exact Before/After wording for `tech-lead.md:97` and `commands/code-review.md:51`. Each must say:
   - conditions are tracked with an owner and a due point;
   - on production, conditions close before the next gate;
   - on the PoC track, conditions become debt items due by the production handoff;
   - FAIL blocks;
   - security HIGH/CRITICAL findings and Immutable Constraint breaches never yield CONDITIONAL_PASS.

   Quote the authority. ADR-007 branch 1 applies to the **command**, because a command may not contradict
   `AGENTS.md`. For the **agent**, use the T542/FU-C precedent.
2. Rule on the `validation-gates:67` security nuance: exact wording if amended.
3. Find any other text that says CONDITIONAL_PASS blocks a merge, or that lets a security HIGH/CRITICAL finding
   through. Mark the search **(unverified)** where it needs a shell; the orchestrator will run it.
4. Golden coupling and blast radius. Write a follow-up table showing owner, files, and whether a grant is needed.

## 4. Output

`docs/artifacts/conditional-pass-semantics-v1.md`. Use four-backtick `Before:`/`After:` fences, one per edit.

## 5. Constraints

- **You have no Bash.** Mark unverified claims as such.
- Write exactly one file. Hand it back uncommitted. Do not edit this brief.
- Read-only. You may read `tests/golden/open/code-review-conditional-pass-conditions-gap/{brief.md,expect.py}`
  **only**. **Never open `tests/golden/held-out/`.**
- **Do NOT run `glab mr merge` or any merge/approve API, and do not commit or push.**

## 6. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity `critical` |
`major` | `minor`. A ranking question that ADR-008 (T581, being drafted in parallel) would answer is a `dependency`:
report it rather than deciding it.
