# emage.code — File Structure

## Complete Workspace Layout

```
your-project/
├── AGENTS.md                              ← Workspace-level instructions (global conventions)
│
├── .github/
│   ├── agents/                            ← Agent definitions (YAML frontmatter + instructions)
│   │   ├── orchestrator.agent.md          ← Central coordinator (user-invocable)
│   │   ├── poc-orchestrator.agent.md      ← PoC coordinator (user-invocable)
│   │   ├── product-owner.agent.md
│   │   ├── solution-architect.agent.md
│   │   ├── tech-lead.agent.md
│   │   ├── scrum-master.agent.md
│   │   ├── backend-developer.agent.md
│   │   ├── frontend-developer.agent.md
│   │   ├── database-engineer.agent.md
│   │   ├── qa-engineer.agent.md
│   │   ├── security-engineer.agent.md
│   │   ├── devops-engineer.agent.md
│   │   ├── release-manager.agent.md
│   │   ├── technical-writer.agent.md
│   │   ├── ux-designer.agent.md
│   │   ├── technology-scout.agent.md
│   │   ├── feasibility-agent.agent.md
│   │   ├── scaffolding-agent.agent.md
│   │   ├── integration-agent.agent.md
│   │   ├── data-mockup-agent.agent.md
│   │   ├── demo-agent.agent.md
│   │   ├── evaluation-agent.agent.md
│   │   ├── debt-narrator.agent.md
│   │   ├── poc-qa.agent.md
│   │   ├── poc-security.agent.md
│   │   ├── poc-writer.agent.md
│   │   └── poc-devops.agent.md
│   │
│   ├── prompts/                           ← Slash commands
│   │   ├── new-project.prompt.md          ← /new-project
│   │   ├── new-feature.prompt.md          ← /new-feature
│   │   ├── plan.prompt.md                 ← /plan (plan-only, no execution)
│   │   ├── batch.prompt.md                ← /batch (parallel multi-unit changes)
│   │   ├── code-review.prompt.md          ← /code-review
│   │   ├── security-audit.prompt.md       ← /security-audit
│   │   ├── prepare-release.prompt.md      ← /prepare-release
│   │   ├── team-status.prompt.md          ← /team-status
│   │   ├── bug-report.prompt.md           ← /bug-report
│   │   ├── new-poc.prompt.md              ← /new-poc
│   │   ├── evaluate-poc.prompt.md         ← /evaluate-poc
│   │   ├── poc-demo.prompt.md             ← /poc-demo
│   │   ├── skillify.prompt.md             ← /skillify (capture workflow as skill)
│   │   └── consolidate-memory.prompt.md   ← /consolidate-memory
│   │
│   ├── skills/                            ← Reusable capability cards
│   │   ├── task-management.md             ← Task protocol (create, update, track, close)
│   │   ├── dependency-graphing.md         ← DAG construction and visualization
│   │   ├── checkpoint-protocol.md         ← Checkpoint format, compression, resume
│   │   ├── plan-approve-execute.md        ← Plan presentation and approval workflow
│   │   ├── blocker-escalation.md          ← Blocker detection, routing, escalation
│   │   ├── validation-gates.md            ← Quality gate definitions and pass/fail criteria
│   │   ├── worktree-isolation.md          ← Git worktree creation, assignment, merge
│   │   ├── project-planning.md            ← WBS, milestone timelines, feature decomposition
│   │   ├── api-design.md                  ← REST/GraphQL design, OpenAPI specs
│   │   ├── code-review.md                 ← Review checklists and verdict format
│   │   ├── testing-strategy.md            ← Test pyramid, frameworks, coverage targets
│   │   ├── ci-cd-pipeline.md              ← Pipeline templates and deployment automation
│   │   ├── gitlab-management.md           ← GitLab API operations
│   │   ├── release-workflow.md            ← Versioning, changelog, release gates
│   │   ├── context-window-management.md   ← Token budgets, progressive loading
│   │   ├── cost-token-governance.md       ← Budget envelopes, model routing, caching
│   │   ├── technology-scouting.md         ← Option matrix, evaluation criteria
│   │   ├── rapid-prototyping.md           ← Minimal scaffolding for PoC
│   │   ├── poc-evaluation.md              ← Hypothesis verdict framework
│   │   ├── technical-debt-tracking.md     ← Debt ledger, scorecard, remediation
│   │   ├── skillify.md                    ← Capture workflow as reusable skill
│   │   └── memory-management.md           ← Memory hierarchy, consolidation rules
│   │
│   ├── instructions/                      ← Coding rules (file-pattern scoped)
│   │   ├── coding-standards.instructions.md
│   │   ├── git-workflow.instructions.md
│   │   ├── security-guidelines.instructions.md
│   │   └── poc-guidelines.instructions.md
│   │
│   └── hooks/                             ← Post-action hooks
│       └── post-edit-reminder.json
│
├── .vscode/
│   └── mcp.json                           ← MCP server configuration
│
└── docs/                                  ← Project state (created by agents at runtime)
    ├── plans/                             ← Plan documents (created before execution)
    │   └── plan-001.md
    ├── tasks/                             ← Task state (DAG + individual briefs)
    │   ├── active-tasks.md                ← Structured task list with dependency graph
    │   ├── completed-tasks.md             ← Archive
    │   └── task-T001.md                   ← Individual task brief
    ├── decisions/                          ← Architecture Decision Records
    │   └── ADR-001-tech-stack.md
    ├── checkpoints/                       ← Phase boundary summaries
    │   └── checkpoint-001-planning.md
    └── artifacts/                          ← Versioned deliverables
        ├── requirements-v1.md
        ├── architecture-v1.md
        └── TECHNICAL-DEBT.md
```

## File Counts

| Category | Count | New vs. Carried Forward |
|----------|-------|------------------------|
| Agents | 27 | 27 carried forward (enhanced instructions) |
| Slash Commands | 14 | 12 carried + 2 new (`/plan`, `/batch`, `/skillify`, `/consolidate-memory`) |
| Skills | 22 | 12 carried + 10 new (task-management, dependency-graphing, checkpoint-protocol, plan-approve-execute, blocker-escalation, validation-gates, worktree-isolation, skillify, memory-management, release-workflow) |
| Instructions | 4 | 4 carried (enhanced) |
| Hooks | 1 | 1 carried |
| Runtime docs | 5 dirs | All new (plans/, tasks/, decisions/, checkpoints/, artifacts/) |

## Key Differences from DEV-Team-Recruiter

1. **`docs/` directory** — Runtime state management for tasks, plans, checkpoints, decisions, artifacts
2. **10 new skills** — Encapsulate the orchestration protocols (task mgmt, DAG, checkpoints, etc.)
3. **4 new commands** — `/plan`, `/batch`, `/skillify`, `/consolidate-memory`
4. **Enhanced agent instructions** — All 27 agents updated with protocol awareness (task protocol, checkpoint format, blocker escalation)
5. **Orchestrator rewrite** — Core orchestrator fundamentally restructured around Plan-Approve-Execute + DAG-based coordination
