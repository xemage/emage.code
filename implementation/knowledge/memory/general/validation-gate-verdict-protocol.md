---
scope: general
title: "Validation gates use exactly three verdicts, and reviewers do not fix what they are reviewing"
tags: [quality-gates, review-protocol]
---

## Three verdicts, three consequences

Every quality gate in this harness resolves to exactly one of three verdicts. `PASS` proceeds to
the next phase outright. `CONDITIONAL_PASS` also proceeds, but the reviewer's stated conditions are
recorded and tracked in the task list rather than silently dropped. `FAIL` blocks progression
entirely until fix tasks are created and re-delegated, and the same gate is re-invoked once the fix
lands — it is not overridden or waived.

## Reviewers do not edit what they are reviewing

A review-role agent (Tech Lead, QA, or Security) does not modify code or content during its own
review pass — its output is the verdict itself, plus annotations, approvals, or rejections. Fixing
a finding is always a separate, subsequently-dispatched task, never something the reviewer does in
the same pass as producing the verdict.
