---
name: receiving-code-review
description: "Respond to code review feedback with technical rigor. Use before implementing review suggestions."
maturity: experimental
---

# Receiving Code Review

## Rails
**Inputs**: MR/PR review comments, `tech-lead`/`security-engineer` findings,
or an orchestrator review-gate condition — any structured feedback an agent
must act on before implementing suggested changes.

**Out of scope**: Does not define the review format or VERDICT vocabulary
itself (see skill `code-review` for the checklist a reviewer produces this
skill's input from) — this skill governs the *implementer's* response, not
the *reviewer's* output. Does not authorize silently skipping any item,
regardless of perceived priority.

**Failure mode**: Implementing a suggestion without the READ/UNDERSTAND/
VERIFY/EVALUATE sequence, or marking a review thread resolved without
verification evidence, is a Forbidden Pattern per this skill's own list. An
unclear item must stop implementation and request clarification rather than
proceed on a partial or guessed understanding.

## Purpose

Turn review feedback into correct changes — not performative agreement or blind edits.

## When to Use

- Addressing MR/PR review comments
- Processing tech-lead or security-engineer findings
- Responding to orchestrator review gate conditions

## Response Pattern

```
1. READ    — full feedback without reacting
2. UNDERSTAND — restate each item in your own words
3. VERIFY  — check against actual codebase state
4. EVALUATE — sound for this project, stack, and constraints?
5. RESPOND — clarify, push back with reasoning, or proceed
6. IMPLEMENT — one item at a time; verify each
```

## Clarification Rule

If any item is unclear, **stop** and ask before implementing partial fixes.
Related items often share assumptions; partial understanding causes wrong fixes.

## Evaluation Checklist

Before implementing a suggestion:

- [ ] Technically correct for this codebase?
- [ ] Breaks existing behavior or contracts?
- [ ] Reason for current implementation understood?
- [ ] Works across supported platforms (if knowledge/projection change)?
- [ ] Test or verification step identified?

Push back with evidence when a suggestion is wrong for this context.

## Implementation Discipline

- One review item per commit when possible
- Run targeted tests after each item
- Update task brief or checkpoint if scope changes
- Mark review threads resolved only after verification evidence exists

## Forbidden Patterns

- Implementing all comments before understanding each
- "Fixed" without re-running relevant tests
- Silently skipping items that seem low priority
- Agreeing without verification when the suggestion is architectural

## Integration with Validation Gates

| Review source | Gate |
|---------------|------|
| Tech Lead | Implementation gate |
| Security Engineer | Security gate |
| QA Engineer | Integration gate |

`FAIL` findings block merge until resolved or escalated via blocker protocol.
