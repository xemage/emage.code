---
description: "Validate the multi-agent workflow using scenario-based tests, handoff checks, and command regression checks."
agent: "orchestrator"
argument-hint: "Optional scope override (small|medium|complex|all)"
maturity: stable
audience: both
---

Run a workflow validation pass for the AI development team configuration.

## Validation Scope

1. Scenario suites: `small`, `medium`, `complex` (or filtered by user input)
2. Role behavior checks for Product Owner, Solution Architect, Tech Lead
3. Handoff integration checks:
   - API contract parity
   - QA defect routing closure
   - Security-to-release blocking consistency
4. Command regression checks:
   - `new-project`, `new-poc`, `evaluate-poc`, `code-review`, `prepare-release`, `team-status`

## Validation Gate References

5. **Check all validation gates.** Gate types, executors and the VERDICT format are defined in the `validation-gates` skill (§ Gate Types, § Verdict Format); the orchestrator's invocation points are in the `orchestrator` agent's § Validation Gates. Each gate below names where it is defined:
   - Architecture review gate — `validation-gates` skill § Gate Types, **Architecture**
   - Code review gate — `validation-gates` skill § Gate Types, **Implementation**
   - Integration checkpoint gate — `validation-gates` skill § Gate Types, **Integration**
   - Security audit gate — `validation-gates` skill § Gate Types, **Security**
   - Release gate — `validation-gates` skill § Gate Types, **Release**

   These are the skill's five gate types, in the order of its § Procedures › 4. Gate Pipeline for a Release. Plan approval (`plan-approve-execute` skill § The Three Phases › Phase 2: Approve, a user decision: Approve / Revise / Reject) and the architecture briefing (`orchestrator` agent § Core Workflow › Phase 3: Development, step 1) are workflow steps, not validation gates, and are not checked here.
6. For each gate, verify:
   - Gate is reachable in workflow
   - Gate produces a VERDICT
   - Gate blocks progression on FAIL
   - Gate escalation path is defined

## Output Requirements

7. Use the Workflow Validation Scorecard format from `testing-strategy` skill
8. Return verdict per scenario: `pass`, `conditional_pass`, `fail`
9. Aggregate a final verdict with prioritized remediation backlog
10. Include owners and ETA for each remediation item

## Verdict Output

11. **Produce a structured VERDICT** at the end of validation:

```
## WORKFLOW VALIDATION VERDICT

- **Status**: PASS | CONDITIONAL_PASS | FAIL
- **Scenarios tested**: <count>
- **Scenarios passed**: <count>
- **Scenarios failed**: <count>
- **Gates validated**: <count>/<total>
- **Handoff checks**: passed=<n>, failed=<n>
- **Command regressions**: passed=<n>, failed=<n>
- **Blocker IDs**: [if FAIL — list blocking issues]
- **Validator**: orchestrator
- **Timestamp**: <ISO-8601>
```

If FAIL, the remediation backlog must include:
- Issue description
- Severity (CRITICAL/HIGH/MEDIUM/LOW)
- Owner
- Estimated fix effort
- Blocked workflows

## Rails

**Inputs**: The scenario scope (`small`/`medium`/`complex`/`all`, from `{{input}}`) and the current agent/command/handoff configuration.
**Out of scope**: Modifying any agent, command, or handoff file — this command only reports pass/conditional_pass/fail per scenario.
**Failure mode**: If any gate is unreachable, doesn't produce a VERDICT, doesn't block on FAIL, or lacks an escalation path, the overall VERDICT is FAIL with that gate named in the remediation backlog.

Scope override:
{{input}}
