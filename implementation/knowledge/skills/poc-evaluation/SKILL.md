---
name: poc-evaluation
description: "Assess proof-of-concept outcomes against explicit hypotheses and success criteria."
maturity: experimental
---

# PoC Evaluation

## Rails
**Inputs**: A PoC whose outcome is to be assessed: its PoC artifact (`poc-{name}-v{N}`) with the hypothesis and success criteria defined before the PoC started, the evidence gathered against them, and the PoC's `POC-DEBT-SCORECARD.md` and debt ledger (technical-debt-tracking skill). This includes an evaluation run through the `/evaluate-poc` command.

**Out of scope**: Does not scan for `POC-DEBT` tags or write the scorecard; the technical-debt-tracking skill does, and § 8 of the evaluation links to its items. Does not create tasks or write checkpoints: debt items reach the task backlog as promotion proposals, and an orchestrator creates the tasks and writes the checkpoints (`AGENTS.md` § Task Protocol, § Checkpoint Protocol). The `[VERDICT]` line is the PoC track's hypothesis verdict, not a `validation-gates` gate verdict.

**Failure mode**: If any success criterion defined in the PoC artifact was not tested by the PoC's deadline, or rests only on weak evidence, the verdict is `INVALIDATED` with `Evidence strength: weak`, and the Recommended next step names a follow-up PoC with refined criteria (§ Hypothesis Success Criteria Reference). Never force a `VALIDATED` call (`poc-guidelines.md` § Hypothesis-First Validation, Rules 3–4).

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

This line is the one-line rendering of the evaluation's single verdict: a PoC either validates or invalidates its hypothesis (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4). When the evaluation is run through the `/evaluate-poc` command, the line accompanies, and does not replace, that command's `## POC VERDICT` block. Both record the same evaluation, so their values agree: `result=` is the block's `Status`, `evidence_strength=` its `Evidence strength`, `production_recommendation=` its `Production recommendation`, and `hypothesis=` a short form of its `Hypothesis`; `debt_count=` is the total in its `Debt items` line, and `date=` is the date of its `Timestamp`. `gate=poc-evaluation` names this PoC-track verdict. It is not one of the `validation-gates` skill's gate types, and its values are not that skill's `PASS` / `CONDITIONAL_PASS` / `FAIL`.

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

When the production recommendation is `proceed` or `proceed_with_constraints`, complete the following handoff checklist before transitioning to production implementation:

```markdown
## Production Handoff Checklist

### Code & Architecture
- [ ] All POC-DEBT tags inventoried in `POC-DEBT-SCORECARD.md` (`poc-guidelines.md` Scorecard Rule 1) and recorded in the debt ledger with a disposition (technical-debt-tracking skill)
- [ ] Architecture decisions documented in `docs/decisions/`
- [ ] API contracts from PoC promoted to versioned api-contract artifacts
- [ ] Security shortcuts identified and remediation planned

### Knowledge Transfer
- [ ] Key learnings documented in evaluation artifact
- [ ] Integration patterns documented for production implementation
- [ ] Failure modes and edge cases discovered during PoC documented

### Task Creation
- [ ] Refactoring backlog items merged into the debt ledger (technical-debt-tracking skill, § POC-DEBT Tag Scanning Procedure, Step 3)
- [ ] Promotion proposals for every `must_fix_pre_prod` and `can_defer_post_ga` debt item reported to the orchestrator, each with its proposed priority and target sprint (technical-debt-tracking skill, § Promotion Procedure for Debt Items to Production Backlog)
- [ ] Production implementation tasks, and tasks for the accepted proposals, created by an orchestrator as rows in `docs/tasks/active-tasks.md` with `docs/tasks/task-<ID>.md` briefs, referencing PoC artifacts (`AGENTS.md` § Task Protocol)

### Approvals
- [ ] Evaluation verdict reviewed and approved by {approving role}
- [ ] Production recommendation accepted by stakeholder
- [ ] Constraint remediation plan approved (if proceed_with_constraints)
```

The completed checklist is included in the evaluation artifact and referenced in the next checkpoint summary.

When the evaluation is run through the `/evaluate-poc` command, that command's step 10 handoff checklist is required for the same recommendations. Its items complement this list and do not replace it. Produce one `## Production Handoff Checklist` holding this list's four groups and a fifth group, `### Production Readiness (/evaluate-poc step 10)`, with the command's other seven items, each worded exactly as the command words it. The command's eighth item, its architecture-decisions item, is already in the Code & Architecture group in the same words, so list it there only.
