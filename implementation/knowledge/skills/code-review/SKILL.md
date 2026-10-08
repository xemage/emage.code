---
name: code-review
description: "Perform structured code reviews with checklists for correctness, security, performance, and maintainability. Use when reviewing merge requests, pull requests, checking code quality, or performing peer review."
maturity: stable
---

# Code Review

Skill for performing thorough, structured code reviews following best practices.

## When to Use
- Reviewing a merge request or pull request
- Performing peer code review
- Checking code quality before merge
- Evaluating third-party code or libraries

## Procedure

### 1. Context Gathering
- Read the MR/PR description and linked issue
- Understand the feature or bug being addressed
- Review the acceptance criteria
- Check the architecture constraints

### 2. Review Checklist

#### Correctness
- [ ] Code does what the issue/story requires
- [ ] Edge cases handled
- [ ] Error handling is appropriate
- [ ] No off-by-one errors or boundary issues
- [ ] Concurrency issues addressed (if applicable)

#### Security (OWASP)
- [ ] Input validation on all user inputs
- [ ] No SQL/command/XSS injection vectors
- [ ] Authentication/authorization checks present
- [ ] Sensitive data not logged or exposed
- [ ] No hardcoded secrets or credentials
- [ ] The review states whether the merge request touches security-sensitive code. For one that does: the `security-guidelines.md` § OWASP Top 10 Checklist Reference run against the change, all ten categories (A01 to A10), as that instruction's § Security Review Workflow step 1 requires, with each category's result (findings, none, or not applicable) noted in the review; each security finding recorded with its grade (skill `validation-gates` § Verdict Rules, § Severity Definitions). This run does not replace the Security gate before release (skill `validation-gates` § Gate Types).

#### Performance
- [ ] No N+1 query issues
- [ ] Appropriate use of indexes (database)
- [ ] No unnecessary allocations or copies
- [ ] Efficient algorithms for the data size
- [ ] Caching used where appropriate

#### Maintainability
- [ ] Code is readable and self-documenting
- [ ] Functions are focused (single responsibility)
- [ ] DRY — no unnecessary duplication
- [ ] Naming is clear and consistent
- [ ] No commented-out code left behind

#### Testing
- [ ] Tests added for new functionality
- [ ] Tests cover happy path and error cases
- [ ] Tests are deterministic (no flaky tests)
- [ ] Mocking is appropriate (not over-mocked)

#### Documentation
- [ ] Public APIs documented
- [ ] Complex logic has explanatory comments
- [ ] Breaking changes documented

### 3. Feedback Format

The `### Verdict:` below is the review's one gate verdict (§ VERDICT Format for Validation Gates), so it takes one of the values `AGENTS.md` § Validation Gates allows, `PASS`, `CONDITIONAL_PASS` or `FAIL`, and the same value as the concluding `[VERDICT]` line. An open point that is a defect is a finding: grade it on § Severity Guide, and the verdict follows from the findings. A review that cannot conclude because a question stays open issues no verdict until the question is answered: the reviewer reports a blocker (`AGENTS.md` § Blocker Protocol) rather than fabricating a `PASS` (skill `validation-gates` § Rails, Failure mode), and no merge is approved without the verdict (§ Rails).

```markdown
## Review: [MR Title]

### Verdict: [PASS | CONDITIONAL_PASS | FAIL]

### Summary
[1-2 sentence overall assessment]

### Findings

#### 🔴 Must Fix
1. **[file:line]** — [Issue description]
   > Suggestion: [How to fix]

#### 🟡 Should Fix
1. **[file:line]** — [Issue description]
   > Suggestion: [How to fix]

#### 🔵 Nice to Have
1. **[file:line]** — [Improvement suggestion]

#### ✅ Well Done
- [Positive observations about the code]
```

### 4. Severity Guide
| Level | Criteria | Action |
|-------|----------|--------|
| 🔴 Must Fix | Bug, security issue, data loss risk | Block merge |
| 🟡 Should Fix | Performance, maintainability concern | Request changes |
| 🔵 Nice to Have | Style, minor improvement | Comment only |
| ✅ Well Done | Excellent pattern, clean code | Acknowledge |

## Guidelines
- Be constructive — explain WHY, suggest HOW
- Praise good code, not just critique problems
- Focus on the code, not the person
- Ask questions when you're uncertain
- Don't nitpick style issues that linters should catch

---

## Protocol-Aware Enhancements

### VERDICT Format for Validation Gates

Code review is a **validation gate** in the emage.code workflow. Every review MUST conclude with a structured verdict that downstream gates (CI/CD, release) can consume:

```
[VERDICT] gate=code-review | result=PASS|CONDITIONAL_PASS|FAIL | reviewer={role} | artifact_ref={artifact-version} | date={YYYY-MM-DD}
```

Code review is the `validation-gates` skill's **Implementation** gate (§ Gate Types: Tech Lead, after code complete, before merge). This line accompanies, and does not replace, the `## Gate Verdict` block that skill's § Verdict Format requires of every gate, with `**Gate:** implementation`. Both record the gate's one verdict, so `result=` carries the same value as the block's `### Verdict:`.

**Verdict definitions:**

| Verdict | Meaning | Pipeline Effect |
|---------|---------|-----------------|
| `PASS` | No must-fix findings. Code is merge-ready. | Pipeline proceeds. |
| `CONDITIONAL_PASS` | Only should-fix findings. Code may merge with tracked follow-ups. | Pipeline proceeds; follow-up items logged to `docs/tasks/active-tasks.md`. |
| `FAIL` | One or more must-fix findings. Code must not merge. | Pipeline halts. Re-review required after fixes. |

These definitions apply together with skill `validation-gates` § Verdict Rules, which applies to the same verdict (the paragraph "Criteria from the executor's own documents" there). Grade each finding on both scales, this skill's § Severity Guide and that skill's § Severity Definitions, and give the most restrictive verdict either requires. A Must Fix finding is `FAIL` even where that skill would admit `CONDITIONAL_PASS` for a high finding outside the security category with a documented mitigation, and a high finding without a documented mitigation is `FAIL` even when it is graded Should Fix here.

### Artifact Version Awareness

When reviewing code, always note which artifact versions are relevant to the review:

- **API contracts:** Confirm the code conforms to the referenced `api-contract-vN`.
- **Architecture decisions:** Confirm the code aligns with `architecture-decision-vN`.
- **Pipeline config:** Confirm CI/CD changes match `pipeline-config-vN`.

Include artifact references in the review output:

```markdown
### Artifacts Reviewed
- api-contract-v3 — endpoints conform ✅
- architecture-decision-v2 — pattern followed ✅
```

### Review as Validation Gate

The code-review verdict is consumed by the CI/CD pipeline at the `approve` stage. The following rules apply:

1. A `FAIL` verdict blocks the merge request — no override without Tech Lead waiver (documented as a decision artifact). No waiver applies to a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, whoever raised it, to a breach of an Immutable Security Constraint, or to a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened: `security-guidelines.md` says "`CRITICAL` and `HIGH` findings block merge until resolved" (§ Security Review Workflow), and that its Immutable Security Constraints "cannot be overridden by any agent, configuration, or runtime decision". A waiver that lifts a `FAIL` with a security finding graded `SECURITY:MEDIUM` among its causes does not lift that finding's remediation plan (owner, fix, deadline), which is recorded as a tracked condition before merge (`security-guidelines.md` § Security Review Workflow).
2. A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint. On the production track the item is resolved before the next gate; on the PoC track it becomes a debt item, recorded in the debt ledger and the debt scorecard by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard), unless `poc-orchestrator` § Security Findings sets a security finding's fix deadline no later than the production handoff, which governs.
3. A `PASS` verdict allows merge with no additional conditions.
4. Every verdict must be recorded in the next checkpoint summary under `decisions=[...]`.

## Rails

**Inputs**: The MR/PR diff or worktree changes, the linked issue/task brief and its acceptance criteria, the architecture/coding-standards constraints the change must respect.
**Out of scope**: Editing the code under review (read-only during review), making architecture or requirements decisions, approving a merge without producing the structured VERDICT block.
**Failure mode**: A `FAIL` verdict halts the pipeline and requires re-review after fixes; a `FAIL` may not be overridden without a documented Tech Lead waiver decision artifact, and a `FAIL` for a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, whoever raised it, for a breach of an Immutable Security Constraint, or for a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, may not be overridden at all (§ Review as Validation Gate).
