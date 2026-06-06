# emage.code — Protocols & Contracts

This document defines the core protocols that all agents must follow. These protocols are the "operating system" of the agent team — they replace implicit conventions with explicit, structured contracts.

## Protocol 1: Task Management Protocol

### Task States
```
pending → in_progress → in_review → done
                ↓
            blocked → (escalated) → in_progress
                                        ↓
                                    cancelled
```

### Task Entry Format (in `docs/tasks/active-tasks.md`)
```markdown
| ID | Title | Status | Owner | Blocked By | Blocks | Priority | Created |
|----|-------|--------|-------|------------|--------|----------|---------|
| T001 | Define requirements | done | @product-owner | — | T002, T003 | P0 | 2025-01-15 |
| T002 | System architecture | in_progress | @solution-architect | T001 | T004, T005 | P0 | 2025-01-15 |
| T003 | UX wireframes | in_progress | @ux-designer | T001 | T005 | P1 | 2025-01-15 |
```

### Task Brief Format (individual `docs/tasks/task-<ID>.md`)
```markdown
---
id: T002
title: System architecture
owner: "@solution-architect"
status: in_progress
blocked_by: [T001]
blocks: [T004, T005]
priority: P0
---

## Objective
Design the system architecture based on approved requirements (requirements-v1.md).

## Inputs
- requirements-v1.md (from @product-owner, T001)
- Technology constraints from user

## Expected Outputs
- architecture-v1.md (component diagram, tech stack, data flow)
- ADR-001 through ADR-N (key decisions with rationale)

## Acceptance Criteria
- All functional requirements have a component owner
- Data flow covers all user stories
- ADRs reference requirement IDs
- No unresolved technology risks

## Constraints
- Token budget: ≤80k for this phase
- Must complete before T004 and T005 can start
```

### Task Rules
1. Only the orchestrator creates, assigns, and transitions tasks
2. Agents report completion by updating the task brief with: `status: done`, `artifacts: [list]`, `summary: "..."`.
3. If blocked, agent updates status to `blocked` and adds: `blocker: "description"`, `blocker_type: "technical|dependency|unclear_requirements"`
4. Orchestrator reads task state before any delegation
5. A task is only `done` when all acceptance criteria are met

---

## Protocol 2: Plan-Approve-Execute

### Plan Document Format (`docs/plans/plan-<ID>.md`)
```markdown
# Plan: <Title>

## Goal
<One-paragraph description of what will be accomplished>

## Task Decomposition
<Mermaid dependency graph>

## Agent Assignments
| Task | Agent | Estimated Scope | Dependencies |
|------|-------|-----------------|--------------|
| ... | ... | ... | ... |

## Artifact Flow
<Which agent produces what, consumed by whom>

## Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ... | ... | ... | ... |

## Token Budget
| Phase | Budget | Model Tier |
|-------|--------|------------|
| Planning | ≤80k | Standard |
| Implementation | ≤120k | Standard |
| QA/Security | ≤60k | Standard |

## Approval
- [ ] User approved this plan
```

### Workflow
1. User invokes `/new-project` (or `/new-feature`, `/new-poc`)
2. Orchestrator analyzes the request
3. Orchestrator writes `docs/plans/plan-<ID>.md` with full decomposition
4. Orchestrator presents a summary to the user and asks: "Shall I proceed with this plan?"
5. User approves → Orchestrator begins execution
6. User modifies → Orchestrator updates plan and re-presents
7. User rejects → Orchestrator acknowledges and waits for new direction

---

## Protocol 3: Checkpoint Compression

### Checkpoint Format (`docs/checkpoints/checkpoint-<SEQ>-<phase>.md`)
```markdown
---
sequence: 3
phase: implementation
timestamp: 2025-01-16T14:30:00Z
token_metrics:
  phase_budget: 120000
  used: 87400
  projected: 105000
  variance: "-12.5%"
---

# Checkpoint: Implementation Phase

## Completed
- T004: Backend API (done, artifacts: [openapi.yaml, src/api/])
- T005: Frontend Shell (done, artifacts: [src/ui/])

## In Progress
- T006: Integration Tests (owner: @qa-engineer, 60% complete)

## Blocked
- T007: E2E Tests (blocked by T006)

## Key Decisions Since Last Checkpoint
- ADR-003: Chose PostgreSQL over MongoDB for relational query patterns
- ADR-004: JWT with refresh tokens for authentication

## Open Risks
- Frontend state management library undecided (T005 used local state as placeholder)

## Next Steps
1. Complete T006 (integration tests)
2. Unblock T007 (E2E tests)
3. Begin T008 (security audit) once T006 is done
```

### Checkpoint Rules
1. Orchestrator writes a checkpoint at every phase boundary (planning → architecture → implementation → QA → release)
2. When delegating to an agent, provide the latest checkpoint + task-specific brief (NOT the full history)
3. Checkpoints include token metrics for governance
4. Old checkpoints are archived (not deleted) for audit trail

---

## Protocol 4: Blocker & Escalation

### Blocker Report Format
```markdown
## BLOCKER: <Title>

- **Task:** T006 (Integration Tests)
- **Reporter:** @qa-engineer
- **Type:** technical | dependency | unclear_requirements | external
- **Severity:** critical | major | minor
- **Description:** <What is blocked and why>
- **Attempted Resolution:** <What was tried>
- **Suggested Resolution:** <If known>
- **Escalation Target:** <Who can unblock — @tech-lead, @solution-architect, or user>
```

### Escalation Path
```
Agent detects blocker
    ↓
Agent reports blocker (updates task status + writes blocker report)
    ↓
Orchestrator reads blocker
    ↓
Is it a dependency blocker?
    YES → Re-prioritize dependent task, notify blocking agent
    NO → Is it a technical blocker?
        YES → Route to @tech-lead for guidance
        NO → Is it an unclear requirement?
            YES → Route to @product-owner for clarification
            NO → Escalate to user with full context
    ↓
Resolution applied → Orchestrator updates task status → Resume
    ↓
If unresolved after 2 attempts → Escalate to user with:
    - Blocker summary
    - What was tried
    - Options for the user to decide
```

### Escalation Rules
1. Agents MUST NOT silently fail. Every blocker is reported.
2. Maximum 2 retry attempts before escalating to user.
3. Blocker reports include what was already tried (prevents circular retries).
4. The orchestrator is the only agent that escalates to the user.

---

## Protocol 5: Validation Gates

### Gate Definitions
| Gate | When | Validator | Pass Criteria |
|------|------|-----------|---------------|
| **Architecture Gate** | After architecture phase | @tech-lead + @security-engineer | All requirements covered, no unresolved risks, ADRs complete |
| **Implementation Gate** | After core implementation | @tech-lead | Code compiles, follows standards, no critical linter errors |
| **Integration Gate** | After parallel work merges | @tech-lead + @qa-engineer | All API contracts match, no merge conflicts, shared state consistent |
| **Security Gate** | Before release | @security-engineer | OWASP Top 10 checked, no critical/high findings unresolved |
| **Release Gate** | Before deployment | @release-manager + @qa-engineer | All tests pass, changelog complete, version tagged |

### Verdict Format
```markdown
## VERDICT: PASS | CONDITIONAL_PASS | FAIL

### Summary
<One paragraph assessment>

### Findings
| # | Severity | Category | Description | Resolution |
|---|----------|----------|-------------|------------|
| 1 | Critical | Security | SQL injection in /users endpoint | Must fix before release |
| 2 | Minor | Style | Inconsistent naming in utils/ | Can fix in next sprint |

### Recommendation
<Proceed | Fix and re-review | Redesign required>
```

### Gate Rules
1. Gates are checkpoints, not bottlenecks. Simple projects may skip non-critical gates.
2. `FAIL` verdicts block progression. Orchestrator creates fix tasks and re-routes.
3. `CONDITIONAL_PASS` allows progression with tracked conditions (added to task list).
4. Validators MUST NOT modify code. Read and report only.
5. Orchestrator decides whether to re-review or accept based on fix severity.

---

## Protocol 6: Artifact Versioning

### Naming Convention
```
<type>-v<N>.md

Examples:
  requirements-v1.md
  requirements-v2.md  (when revised after feedback)
  architecture-v1.md
  implementation-v1/  (directory for code artifacts)
```

### Rules
1. Artifacts are immutable once accepted. Revisions create a new version.
2. Every artifact references its dependencies: `Based on: requirements-v1.md`
3. Agents MUST reference the specific version they consumed (not "the requirements").
4. The orchestrator tracks artifact lineage in checkpoints.

---

## Protocol 7: Delegation Brief Format

When the orchestrator delegates to a specialist agent, it provides a structured brief:

```markdown
## Task Brief for @<agent-name>

### Objective
<Clear, one-paragraph description of what to accomplish>

### Context
- **Project:** <project name/description>
- **Current Phase:** <planning | architecture | implementation | qa | release>
- **Latest Checkpoint:** checkpoint-<N>-<phase>.md

### Inputs
- <artifact-v1.md> — <what it contains and why it's relevant>
- <ADR-001.md> — <relevant decision>

### Constraints
- <Token budget for this task>
- <File ownership boundaries>
- <Technology constraints>

### Expected Outputs
- <List of artifacts to produce>
- <Format requirements>

### Acceptance Criteria
- <Specific, testable criteria>

### Blocker Protocol
If you encounter a blocker:
1. Update the task status to `blocked`
2. Write a blocker report with type, description, and suggested resolution
3. The orchestrator will handle escalation
```
