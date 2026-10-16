---
description: "Request a thorough code review of specified files or the current changes, following the code review skill checklist."
agent: "tech-lead"
argument-hint: "Specify files or describe what to review..."
---

Please perform a thorough code review on the following:

{{input}}

## Review Checklist

Review against:
1. Correctness and acceptance criteria compliance
2. Security (OWASP Top 10)
3. Performance concerns
4. Code quality and maintainability
5. Test coverage
6. Documentation
7. Gate status recommendation (`pass`, `conditional_pass`, `fail`)

Provide structured feedback with severity levels (Must Fix / Should Fix / Nice to Have) and specific remediation suggestions.
If status is `fail`, include blocker details, owner, and retry attempt guidance.

## Artifact Version References

8. Reference the specific artifact versions being reviewed:
   - List artifact files and their versions (e.g., `api-design-v1.2.md`)
   - Note if reviewing against a specific checkpoint
9. Check that implementation matches the approved plan artifact

## Verdict Output

10. **Produce a structured VERDICT** at the end of the review:

```
## VERDICT

- **Status**: PASS | CONDITIONAL_PASS | FAIL
- **Reviewed artifacts**: [list artifact versions reviewed]
- **Must Fix count**: <n>
- **Should Fix count**: <n>
- **Nice to Have count**: <n>
- **Blocker IDs**: [if FAIL — list blocking issues]
- **Reviewer**: tech-lead
- **Timestamp**: <ISO-8601>
```

If CONDITIONAL_PASS, list the conditions, each with an owner and a due point. A security finding listed as a condition carries its remediation plan (owner, fix, deadline) (`security-guidelines.md` § Security Review Workflow). CONDITIONAL_PASS permits the merge, with each condition tracked in the task list (`AGENTS.md` § Validation Gates): on the production track a condition is resolved before the next gate; on the PoC track it becomes a debt item, recorded in the debt ledger and in `POC-DEBT-SCORECARD.md` by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard), except where `poc-orchestrator` § Security Findings sets a security finding's fix deadline no later than the production handoff, which governs.
A security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH` (`security-guidelines.md` § Security Review Workflow), whoever raised it, a breach of an Immutable Security Constraint in `security-guidelines.md`, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, tagged or not, never yields CONDITIONAL_PASS and is never recorded as debt: the status is FAIL until it is resolved. A required control missing only from code outside the change under review is graded at its own severity and tracked. A change that adds or alters code which the missing control should protect is code under review for that control.
If FAIL, the merge is blocked; a Tech Lead waiver may lift a FAIL only when no security finding excluded above is among its causes (skill `code-review` § Review as Validation Gate), and a waiver that lifts a FAIL with a security finding graded `SECURITY:MEDIUM` among its causes does not lift that finding's remediation plan (owner, fix, deadline), which is recorded as a tracked condition before merge. Include blocker details, owner, and retry attempt guidance.

## Rails

**Inputs**: The files or diff to review, or a description of the changes (`{{input}}`); the artifact versions (plan/architecture) the change is meant to conform to.
**Out of scope**: Editing the reviewed code directly — this command only produces a structured review and verdict, executed by `tech-lead` in read-only review mode.
**Failure mode**: If `status` is `fail`, the command requires blocker details, an owner, and retry-attempt guidance before the pipeline can proceed — an incomplete FAIL report is not a valid output.
