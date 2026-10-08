---
name: "validation-gates"
description: "Define and execute validation gates with structured verdicts. Use when performing code review gates, QA gates, security audits, or release readiness checks."
---

# Validation Gates

## Purpose

Enforce quality checkpoints at critical project milestones. Each gate produces a structured verdict (PASS, CONDITIONAL_PASS, or FAIL) that determines whether work can proceed to the next phase.

## When to Use

- Before merging implementation work (implementation gate)
- Before declaring a feature integration-complete (integration gate)
- Before any release or deployment (security gate, release gate)
- When reviewing architectural decisions (architecture gate)
- At any phase transition in the project lifecycle

## Gate Types

| Gate | Executor | Trigger | Focus |
|------|----------|---------|-------|
| **Architecture** | Tech Lead | Before implementation starts | Design soundness, pattern compliance, scalability |
| **Implementation** | Tech Lead | After code complete, before merge | Code quality, test coverage, convention adherence |
| **Integration** | QA Agent | After feature merge, before release | End-to-end functionality, regression, compatibility |
| **Security** | Security Agent | Before any release | Vulnerabilities, auth flaws, data exposure, OWASP Top 10 |
| **Release** | Release Manager | Before deployment | All gates passed, docs complete, migration guides ready |

## Verdict Format

Every gate MUST produce a verdict in this format:

```markdown
## Gate Verdict: <Gate Name>

**Gate:** architecture | implementation | integration | security | release
**Executor:** <agent-name>
**Date:** YYYY-MM-DD
**Target:** <feature, task, or release being evaluated>

### Verdict: PASS | CONDITIONAL_PASS | FAIL

### Findings

| # | Severity | Category | Description | Recommendation |
|---|----------|----------|-------------|----------------|
| 1 | critical | ... | ... | ... |
| 2 | high | ... | ... | ... |
| 3 | medium | ... | ... | ... |
| 4 | low | ... | ... | ... |

### Conditions (if CONDITIONAL_PASS)
- [ ] <condition> — owner: <who>; due: before the next gate (production track; at the Release gate, the next release cycle, except a security finding, which is fixed before the release ships) | recorded as debt in the debt ledger and scorecard by the production handoff (PoC track; a security finding graded medium is fixed by its remediation-plan deadline, no later than the handoff); a security finding also carries its remediation plan (owner, fix, deadline)
- [ ] <condition>

### Summary
<1-3 sentence overall assessment>
```

### Verdict Rules

| Verdict | Criteria |
|---------|----------|
| **PASS** | No critical or high findings, no security finding graded medium, and none of the security findings excluded below. Medium/low findings noted but non-blocking. |
| **CONDITIONAL_PASS** | No critical findings, and none of the security findings excluded below. Other high findings have documented mitigations. Medium/low with clear remediation plan. Each condition is tracked as a task with an owner and a due point, under the track rule: on the production track, all conditions must be resolved before the next gate, except that a Release-gate CONDITIONAL_PASS may ship with its conditions tracked as tasks for the next release cycle; on the PoC track, each condition becomes a debt item, recorded in the debt ledger and the debt scorecard by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard). Neither deferral applies to a security finding (below). |
| **FAIL** | Any critical finding unresolved, OR any high finding without mitigation, OR any security finding excluded below. Work must return to the implementer. |

**Security findings never qualify for CONDITIONAL_PASS.** A security finding is any finding in the security category, whichever gate or executor raises it, graded on the `security-guidelines.md` § Security Review Workflow scale (`SECURITY:CRITICAL`/`HIGH`/`MEDIUM`/`LOW`); the Findings table records that grade as its Severity and `security` as its Category. A finding about a control that `security-guidelines.md` requires is a security finding, whatever category it is filed under. `security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved". A security finding graded critical or high, and any breach of an Immutable Security Constraint in `security-guidelines.md` (which "cannot be overridden by any agent, configuration, or runtime decision"), yields FAIL until it is resolved, whatever mitigation is documented, and no waiver applies to it. The "documented mitigations" route above is for high findings outside the security category only. The same FAIL rule, with no waiver, holds for any security control `security-guidelines.md` requires for the code under review that is omitted, removed, disabled or weakened, tagged or not (on the PoC track, `poc-orchestrator` § Security Findings). None of these is ever recorded as debt. A required control missing only from code outside the change under review is graded at its own severity and tracked like any other finding of that grade. A change that adds or alters code which the missing control should protect is code under review for that control. With no change under review (for example a full-project `/security-audit`), the whole project is the code under review. A security finding graded medium yields at best CONDITIONAL_PASS: its remediation plan (owner, fix, deadline) is recorded as a tracked condition with the verdict, before the affected work's next merge (`security-guidelines.md` § Security Review Workflow: "`MEDIUM` findings must have a remediation plan before merge"); the condition is the fix, due under the track rule above (production: before the next gate; PoC: by the production handoff, as `poc-orchestrator` § Security Findings already requires). The next-release-cycle rule never applies to a security finding: at the Release gate, a security finding graded medium is fixed before the release ships. A security finding graded low is not a condition: it is tracked as technical debt (`security-guidelines.md` § Security Review Workflow; on the PoC track, recorded for debt handoff per `poc-orchestrator` § Security Findings).

**Criteria from the executor's own documents.** Other documents also state verdict criteria; this note covers two of the gates: skill `code-review` § VERDICT Format for Validation Gates (Implementation gate); skill `testing-strategy` § VERDICT Format for QA Gate and § Coverage Thresholds That Determine Gate Outcome, and the `qa-engineer` agent's § Validation Gate Protocol (Integration gate). They apply together with the rules above to the gate's one verdict. A PASS or CONDITIONAL_PASS row states what that verdict requires; it does not grant the verdict when another applicable criterion requires a stricter one. So the verdict is PASS only if every applicable set of criteria, the rules above included, admits PASS, CONDITIONAL_PASS only if every one admits at least CONDITIONAL_PASS, and FAIL otherwise. No set of criteria, the rules above included, makes another less strict.

### Severity Definitions

| Severity | Definition |
|----------|-----------|
| `critical` | Broken functionality, security vulnerability, data loss risk. Blocks all progress. |
| `high` | Significant defect or design flaw. Must be addressed before release; a security finding graded high blocks merge until resolved (§ Verdict Rules). |
| `medium` | Quality concern or technical debt. Should be addressed, can be tracked. |
| `low` | Minor style issue, optimization opportunity, or suggestion. |

A security finding (§ Verdict Rules) takes the tier its grade names on the `security-guidelines.md` § Security Review Workflow scale: `SECURITY:CRITICAL` is `critical`, `SECURITY:HIGH` is `high`, `SECURITY:MEDIUM` is `medium` and `SECURITY:LOW` is `low`. What a security finding of each grade requires is stated in § Verdict Rules, and its tier never lowers that: a breach of an Immutable Security Constraint, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, yields FAIL whatever its tier; any other security finding graded medium needs its remediation plan before merge, and any other graded low is tracked as technical debt.

Whichever gate or executor raises a security finding, it is graded with the definitions in agent `security-engineer` § Findings Classification, whose CRITICAL, HIGH, MEDIUM and LOW are `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM` and `SECURITY:LOW`. A finding that fits more than one definition takes the highest grade it fits. Those definitions decide the grade only; what each grade requires is stated in § Verdict Rules and in the paragraph above. No grade so given is lower than a minimum grade set elsewhere for that kind of finding (for example `poc-security-engineer` § Behavior, "Severity floor", or `poc-orchestrator` § Security Findings for a secret not yet committed). Nor does this paragraph lift an earlier deadline that the executor's own documents set (for the Security Engineer, the SLA paragraph of that section).

## Gate Input Requirements

Each gate type requires specific inputs to perform its evaluation:

### Architecture Gate
- Plan document (`docs/plans/plan-<ID>.md`; `<ID>`: skill `plan-approve-execute` § File Location)
- Proposed design / tech stack
- Dependency analysis

### Implementation Gate
- Source code changes (diff or file list)
- Test results and coverage report
- Convention checklist (from `AGENTS.md`)

### Integration Gate
- Merged feature in integration branch
- End-to-end test results
- Regression test results
- API contract validation (if applicable)

### Security Gate
- Full codebase scan results
- Dependency audit (`npm audit`, `pip audit`, etc.)
- Authentication/authorization flow review
- Data handling review (PII, encryption, storage)

### Release Gate
- All prior gate verdicts (must be PASS or CONDITIONAL_PASS with conditions resolved)
- Changelog / release notes draft
- Documentation updates
- Migration guide (if breaking changes)
- Rollback plan

## Procedures

### 1. Execute a Gate

1. Identify the gate type and assign to the correct executor.
2. Gather all required inputs for that gate type.
3. The executor reviews each input against the gate's criteria.
4. The executor produces a verdict document.
5. Store the verdict in `docs/artifacts/gate-<type>-<target>-<date>.md`.

### 2. Handle a FAIL Verdict

1. Return the verdict to the task assignee with specific findings.
2. The assignee addresses all critical and high findings and every security finding that § Verdict Rules excludes from CONDITIONAL_PASS.
3. The assignee requests a re-evaluation.
4. The gate executor re-runs the gate, producing a new verdict.

### 3. Handle a CONDITIONAL_PASS Verdict

1. Proceed with work, but track all conditions as tasks, each with an owner and a due point. At the Implementation gate, proceeding includes the merge; at the Release gate, it includes shipping the release, with the explicit risk acceptance `release-manager` § Release Gate Policy requires.
2. On the production track, conditions MUST be resolved before the next gate in the pipeline; at the Release gate, which has no next gate, they are tracked as tasks for the next release cycle. On the PoC track, each condition instead becomes a debt item, recorded in the debt ledger and the debt scorecard by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard). Neither deferral applies to a security finding (§ Verdict Rules): one graded medium is fixed before the next gate on the production track (at the Release gate, before the release ships), and on the PoC track by its remediation-plan deadline, no later than the production handoff (`poc-orchestrator` § Security Findings).
3. When all conditions are resolved, update the verdict document:
   - Check off each condition.
   - Add a note: `All conditions resolved on YYYY-MM-DD`.

### 4. Gate Pipeline for a Release

```
Architecture Gate → Implementation Gate → Integration Gate → Security Gate → Release Gate
```

Each gate must achieve at least CONDITIONAL_PASS before the next gate can start. The Release Gate verifies that all prior conditions have been resolved.

## Examples

### Implementation Gate Verdict — CONDITIONAL_PASS

```markdown
## Gate Verdict: Implementation Review

**Gate:** implementation
**Executor:** tech-lead
**Date:** 2025-03-25
**Target:** T021 (Token Bucket Rate Limiting)

### Verdict: CONDITIONAL_PASS

### Findings

| # | Severity | Category | Description | Recommendation |
|---|----------|----------|-------------|----------------|
| 1 | high | testing | No load test for concurrent access | Add load test with 1000 concurrent requests |
| 2 | medium | code quality | Magic numbers in rate limit config | Extract to configuration constants |
| 3 | low | style | Inconsistent error message format | Align with project error format convention |

### Conditions
- [ ] Add load test covering concurrent access scenario
- [ ] Extract rate limit values to configuration

### Summary
Implementation is functionally correct with good unit test coverage. Load testing gap is the primary concern — must verify concurrent behavior before integration.
```

## Guidelines

- Gates are non-negotiable checkpoints. Do not skip gates to save time.
- Verdicts must be evidence-based. Every finding must reference specific code, tests, or documentation.
- CONDITIONAL_PASS is not a skip. Track conditions as real tasks.
- Gate executors should not review their own work. Cross-agent review is mandatory.
- Store all verdict documents for audit trail purposes.

## Rails

**Inputs**: A gate type (architecture/implementation/integration/security/release), its designated executor agent, and that gate type's required inputs per the "Gate Input Requirements" table above.
**Out of scope**: Performing the underlying implementation work being gated, or substituting for the gate executor's own domain expertise — this skill defines the verdict process and format, not the review content itself.
**Failure mode**: A gate that cannot produce a verdict (missing required inputs) is not silently skipped — the executor reports a blocker per the requesting agent's own blocker protocol rather than fabricating a PASS.
