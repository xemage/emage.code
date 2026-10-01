---
name: poc-evaluation
description: "Assess proof-of-concept outcomes against explicit hypotheses and success criteria."
maturity: experimental
---

# PoC Evaluation

## Framework
1. Restate hypothesis
2. Gather evidence
3. Decide verdict
4. Recommend next step
5. Decide production recommendation: proceed | proceed_with_constraints | do_not_proceed
6. Produce prioritized production refactoring backlog
7. Document residual risks and assumptions

## Verdicts
- Validated
- Invalidated

## Required Output Additions
- Production recommendation
- Refactoring backlog (priority, rationale, owner suggestion)
- Linkage to Technical Debt Scorecard items

---

## Protocol-Aware Enhancements

### Structured Evaluation Verdict Format

Every PoC evaluation MUST conclude with a structured verdict that integrates with the gate protocol:

```
[VERDICT] gate=poc-evaluation | result=VALIDATED|INVALIDATED | evidence_strength=strong|moderate|weak | poc_ref=poc-{name}-v{N} | hypothesis="{short hypothesis}" | production_recommendation=proceed|proceed_with_constraints|do_not_proceed | debt_count={N} | date={YYYY-MM-DD}
```

**Full evaluation artifact structure:**

```markdown
# PoC Evaluation: {Name}

## Date: {YYYY-MM-DD}
## Evaluator: {role}
## PoC Artifact: poc-{name}-v{N}
## Tech Eval Ref: tech-eval-v{N} (if applicable)

## 1. Hypothesis Restatement
[Original hypothesis, verbatim from the PoC artifact]

## 2. Success Criteria Assessment

| Criterion | Target | Actual | Met? |
|-----------|--------|--------|------|
| {criterion 1} | {target} | {actual} | ✅/❌ |
| {criterion 2} | {target} | {actual} | ✅/❌ |

## 3. Evidence Summary
[Specific, measurable evidence gathered during the PoC]

## 4. Verdict
**{VALIDATED | INVALIDATED}**

Evidence strength: {strong | moderate | weak}

Rationale: [Why this verdict]

Recommended next step: [The next step; for an `INVALIDATED` verdict with weak evidence, name a follow-up PoC with refined criteria]

## 5. Production Recommendation
**{proceed | proceed_with_constraints | do_not_proceed}**

### Constraints (if proceed_with_constraints):
- [Constraint 1 — must be resolved before production]
- [Constraint 2]

### Reasons (if do_not_proceed):
- [Reason 1]
- [Reason 2]

## 6. Refactoring Backlog
[Prioritized list of items from POC-DEBT tags and review findings]

| Priority | Item | Rationale | Suggested Owner | Effort |
|----------|------|-----------|-----------------|--------|
| P0 | {item} | {rationale} | {role} | {effort} |
| P1 | {item} | {rationale} | {role} | {effort} |

## 7. Residual Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| {risk} | H/M/L | H/M/L | {mitigation} |

## 8. Technical Debt Scorecard Linkage
[Reference, by inventory `#`, to the related items in `POC-DEBT-SCORECARD.md` in the PoC root (`poc-guidelines.md` § Debt Scorecard), and, by `DEBT-{ID}`, to any debt-ledger items the technical-debt-tracking skill created from this evaluation]
```

### Hypothesis Success Criteria Reference

The evaluation MUST reference the original success criteria defined in the PoC artifact (`poc-{name}-vN.md`). Success criteria that were not defined upfront are noted as "post-hoc criteria" and carry reduced evidentiary weight.

**Rules:**
- Every success criterion from the PoC artifact must appear in the assessment table — even if not tested (mark as "Not Tested" with reason).
- Criteria added after PoC start are flagged: `(post-hoc)`.
- The verdict is `VALIDATED` only if every success criterion defined in the PoC artifact was tested and met by the PoC's deadline. Post-hoc criteria cannot stand in for an untested one.
- If any such criterion was tested and not met, the verdict is `INVALIDATED`, with the evidence strength the tests support.
- Otherwise, if any such criterion is "Not Tested" or rests only on weak evidence, the verdict is `INVALIDATED` with `Evidence strength: weak`, and the Recommended next step names a follow-up PoC with refined criteria. Never force a `VALIDATED` call (`poc-guidelines.md` § Hypothesis-First Validation, Rules 3–4).

### Production Handoff Checklist

When the verdict is `proceed` or `proceed_with_constraints`, complete the following handoff checklist before transitioning to production implementation:

```markdown
## Production Handoff Checklist

### Code & Architecture
- [ ] All POC-DEBT tags cataloged and promoted to technical debt backlog
- [ ] Architecture decisions from PoC documented as decision artifacts
- [ ] API contracts from PoC promoted to versioned api-contract artifacts
- [ ] Security shortcuts identified and remediation planned

### Knowledge Transfer
- [ ] Key learnings documented in evaluation artifact
- [ ] Integration patterns documented for production implementation
- [ ] Failure modes and edge cases discovered during PoC documented

### Task Creation
- [ ] Refactoring backlog items created as tasks in docs/tasks/active-tasks.md
- [ ] Debt remediation tasks created with severity and target sprint
- [ ] Production implementation tasks created referencing PoC artifacts

### Approvals
- [ ] Evaluation verdict reviewed and approved by {approving role}
- [ ] Production recommendation accepted by stakeholder
- [ ] Constraint remediation plan approved (if proceed_with_constraints)
```

The completed checklist is included in the evaluation artifact and referenced in the next checkpoint summary.
