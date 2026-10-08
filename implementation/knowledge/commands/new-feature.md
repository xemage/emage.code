---
description: "Plan and create a new feature including user story, tasks, and implementation plan."
agent: "orchestrator"
argument-hint: "Describe the feature you want to add..."
maturity: stable
audience: both
---

I want to add a new feature to the project. Please:

## Phase 1: Plan & Approve

1. **Create a lightweight plan document** for this feature
   - Write to `docs/plans/plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it
   - Include: objective, affected components, task breakdown, dependency impact
   - Reference protocol: `plan-approve-execute` skill § The Three Phases › Phase 1: Plan (Plan Document Format)
2. **Present the plan for my approval before executing**
   - Show: scope summary, estimated tasks, risk assessment
   - Wait for explicit approval before proceeding

## Phase 2: Execute

3. Have the Product Owner write a user story with acceptance criteria
4. Have the Solution Architect assess the technical impact
5. Have the Scrum Master create tasks and estimate effort
6. Assign to appropriate developers and start implementation

## Phase 3: Track & Validate

7. Write a checkpoint after implementation completes, per `AGENTS.md` § Checkpoint Protocol:
   - Store at `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`
   - Include, in this order: completed tasks, key decisions, blockers, token metrics, next steps
8. Produce versioned artifacts for feature deliverables:
   - Format: `<artifact-name>-v<N>.md`, per `AGENTS.md` § Artifact Versioning
   - Store in `docs/artifacts/`
9. Update `docs/tasks/active-tasks.md` with new tasks and state transitions

## Rails

**Inputs**: A free-text feature description (`{{input}}`).
**Out of scope**: Proceeding to execution before the Phase 1 plan has been presented and explicitly approved by the user.
**Failure mode**: If the Solution Architect's technical-impact assessment surfaces a blocker, reports it rather than proceeding to Phase 2 assignment.

Feature description:

{{input}}
