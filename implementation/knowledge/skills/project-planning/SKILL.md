---
name: project-planning
description: "Create structured project plans, work breakdown structures (WBS), milestone timelines, feature decomposition, and sprint roadmaps. Use when starting a new project, planning a major feature, or creating a development roadmap."
maturity: experimental
---

# Project Planning

Skill for creating comprehensive project plans from high-level ideas, including work breakdown structures, milestone timelines, and sprint roadmaps.

## When to Use
- Starting a new project from an idea
- Planning a major feature or epic
- Creating a development roadmap
- Breaking down complex work into manageable tasks

## Procedure

### 1. Idea Analysis
Analyze the project idea and extract:
- Core problem being solved
- Target users/audience
- Key features and capabilities
- Constraints (time, budget, technology)
- Success criteria

### 2. Work Breakdown Structure (WBS)
Decompose the project into a hierarchy:

```markdown
# WBS: [Project Name]

## 1. Project Setup
  1.1 Repository & CI/CD setup
  1.2 Development environment
  1.3 Architecture design
  1.4 Database schema design

## 2. Core Features (MVP)
  2.1 [Feature Area 1]
    2.1.1 [Sub-feature / Task]
    2.1.2 [Sub-feature / Task]
  2.2 [Feature Area 2]
    2.2.1 [Sub-feature / Task]

## 3. Extended Features
  3.1 [Feature Area]

## 4. Quality & Security
  4.1 Testing implementation
  4.2 Security audit
  4.3 Performance optimization

## 5. Documentation
  5.1 API documentation
  5.2 User guide
  5.3 Architecture docs

## 6. Deployment & Release
  6.1 Staging deployment
  6.2 Production deployment
  6.3 Monitoring setup
```

### 3. Milestone Planning
Map WBS items to time-boxed milestones:

```markdown
# Milestone Plan

## Milestone 1: Foundation (Week 1-2)
- Goal: Project infrastructure and architecture ready
- Deliverables:
  - [ ] Repository with CI/CD pipeline
  - [ ] Architecture document
  - [ ] Database schema v1
  - [ ] Development environment runnable

## Milestone 2: MVP Core (Week 3-6)
- Goal: Core features functional
- Deliverables:
  - [ ] [Core Feature 1] complete with tests
  - [ ] [Core Feature 2] complete with tests
  - [ ] Basic UI functional

## Milestone 3: MVP Complete (Week 7-8)
- Goal: MVP ready for internal testing
- Deliverables:
  - [ ] All MVP features integrated
  - [ ] 80%+ test coverage
  - [ ] Security audit passed
  - [ ] Documentation complete

## Milestone 4: Release (Week 9-10)
- Goal: Production deployment
- Deliverables:
  - [ ] Staging validated
  - [ ] Production deployed
  - [ ] Monitoring active
  - [ ] User documentation published
```

### 4. Sprint Backlog Generation
Convert milestones into 2-week sprints with estimated tasks:

```markdown
# Sprint 1: Foundation

## Sprint Goal
Set up project infrastructure and complete architecture design.

## Tasks
| ID | Task | Assignee | Points | Priority |
|----|------|----------|--------|----------|
| 1 | Create GitLab project and CI/CD | DevOps | 3 | Must |
| 2 | Design system architecture | Architect | 8 | Must |
| 3 | Design database schema | DB Engineer | 5 | Must |
| 4 | Set up dev environment (Docker) | DevOps | 3 | Must |
| 5 | Create initial project structure | Tech Lead | 2 | Must |
| 6 | Write project README | Tech Writer | 2 | Should |

## Capacity: 30 points
## Committed: 23 points
```

### 5. Risk Assessment
```markdown
# Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Strategy] |
```

## Templates
See the planning templates in [.github/skills/project-planning/references/](./references/) for reusable planning templates.

## Output
The skill produces:
1. Project vision summary
2. Work Breakdown Structure
3. Milestone timeline
4. Sprint backlogs with estimated tasks
5. Risk register
6. RACI matrix (who does what)

---

## Protocol-Aware Enhancements

### Plan-Approve-Execute Protocol Reference

All plans produced by this skill feed into the **plan-approve-execute** protocol. The workflow is:

1. **Plan** — This skill produces the plan document (WBS, milestones, sprint backlogs).
2. **Approve** — The plan is presented to the user, who decides **Approve**, **Revise** or **Reject** (`plan-approve-execute` skill § The Three Phases › Phase 2: Approve). Plan approval is the user's decision, not a validation gate: it produces no `PASS` / `CONDITIONAL_PASS` / `FAIL` verdict.
3. **Execute** — Only after the user approves does execution begin.

**No work begins without an approved plan.** If the user chooses Revise, update the plan per the feedback and re-present it for approval. If the user chooses Reject, set the plan's status to `rejected` and discuss alternative approaches.

### Plan Document Format and Versioning

Plan documents are versioned artifacts stored under `docs/plans/`, at the path skill `plan-approve-execute` § File Location defines:

```
docs/plans/plan-<ID>.md
```

Each version is its own plan document at that path, with its own `<ID>`; the `## Version` and `## Changes from v{N-1}` fields below record which version it is. A superseded version is marked as `plan-approve-execute` § Guidelines describes.

**Plan document structure:**
```markdown
# Project Plan v{N}

## Version: {N}
## Date: {YYYY-MM-DD}
## Status: draft | approved | rejected | superseded

## Changes from v{N-1}
- [List of changes]

## Vision Summary
[1-2 paragraphs]

## Work Breakdown Structure
[WBS content]

## Milestone Timeline
[Milestone content]

## Sprint Backlogs
[Sprint content]

## Risk Register
[Risk content]

## Approval
- Decided by: user
- Decision: Approve | Revise | Reject
- Changes requested (if Revise): [list]
```

### Task Decomposition to `docs/tasks/active-tasks.md`

When a plan is approved, the sprint backlog tasks MUST be decomposed into entries in `docs/tasks/active-tasks.md`. This is the canonical task register consumed by all agents and synced to GitLab.

**Decomposition procedure:**

1. For each task in the approved sprint backlog, the orchestrator creates the task (`AGENTS.md` § Task Protocol: "Only orchestrators create/transition tasks"). An agent other than an orchestrator that applies this skill proposes the tasks to the orchestrator and does not write the ledger. Each task gets:
   - a row in `active-tasks.md` with the columns `ID | Title | Owner | Status | Priority | Depends on | Last update`, Status `pending`, and a Priority of `P0`, `P1` or `P2` (`AGENTS.md` § Task Protocol), which the orchestrator sets. The sprint backlog's Must / Should / Could is not a value of that column;
   - a brief at `docs/tasks/task-<ID>.md` (objective, inputs, outputs, acceptance criteria), which also records the task's sprint, points and artifact references, for which the row has no column.

2. Assign sequential TASK IDs continuing from the last used ID.
3. Record dependency links between tasks (e.g., frontend task depends on API contract task).
4. Sync each new task to a GitLab issue (see gitlab-management skill).

**Task lifecycle:** a task's states are those of `AGENTS.md` § Lifecycle States: `pending`, `in_progress`, `blocked`, `in_review`, `done` and `cancelled`. Only an orchestrator transitions a task (`AGENTS.md` § Task Protocol). A task is set to `blocked` when a `[BLOCKER]` is raised, and back to `in_progress` when the blocker is resolved. A task that reaches `done` or `cancelled` is moved to `completed-tasks.md` in the same edit (`AGENTS.md` § Task Protocol). The allowed transitions, and the archive procedure, are those of skill `task-management` (§ Status Lifecycle, § Complete a Task).
