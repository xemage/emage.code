# 07 — Phase 3 detail: Skills library completion

> Backfill of the v1 Phase-3 placeholder.

## Goal
The 22 skills in `knowledge/skills/` form a coherent library covering every recurring capability the agents need. Skills are platform-neutral and discoverable.

## Inventory

| Skill | Purpose | Used by |
|-------|---------|---------|
| api-design | REST/GraphQL design checklist | backend-developer, solution-architect |
| blocker-escalation | Blocker reporting protocol | all agents |
| checkpoint-protocol | Phase-boundary summary format | orchestrator |
| ci-cd-pipeline | Pipeline scaffolding | devops-engineer, release-manager |
| code-review | Review checklist + verdict format | tech-lead, qa-engineer, security-engineer |
| context-window-management | Context compression strategies | orchestrator, all agents at budget |
| cost-token-governance | Token-budget tracking | orchestrator |
| dependency-graphing | Task DAG construction | orchestrator |
| gitlab-management | GitLab API patterns | scrum-master, devops-engineer, release-manager |
| memory-management | MCP memory + docs hygiene | orchestrator |
| plan-approve-execute | Plan-Approve-Execute lifecycle | orchestrator, poc-orchestrator |
| poc-evaluation | PoC pass/fail framework | poc-orchestrator, evaluation-agent |
| project-planning | Story mapping + estimation | product-owner, scrum-master |
| rapid-prototyping | PoC scaffolding patterns | poc-orchestrator, scaffolding-agent |
| release-workflow | Release prep + sign-off | release-manager |
| skillify | Pattern-extraction → new skill | (meta) any agent |
| task-management | Task list + brief lifecycle | orchestrator |
| technical-debt-tracking | Debt registry + retirement | technical-debt-narrator |
| technology-scouting | Stack/library evaluation | technology-scout, feasibility-agent |
| testing-strategy | Test pyramid + coverage | qa-engineer |
| validation-gates | Gate format + verdict routing | tech-lead, qa-engineer, security-engineer |
| worktree-isolation | Git worktree per agent | devops-engineer, orchestrator |

## Skill file shape

```markdown
---
name: <slug>
description: "What capability the skill provides — one or two sentences."
---

# <Title>
## Purpose
## When to Use
## Inputs
## Outputs
## Procedure
1. …
## Failure Modes
## References
```

## Acceptance criteria
- [ ] All 22 skills present under `knowledge/skills/<name>/SKILL.md`.
- [ ] Each skill has the seven canonical sections.
- [ ] No skill body refers to a platform-specific path or convention.
- [ ] Each agent that uses a skill mentions it by name in their agent file.
