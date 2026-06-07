# emage.code

**Next-generation AI dev team orchestration for VS Code + GitHub Copilot, Gemini CLI, and Opencode**

emage.code is a structured multi-agent development system that brings disciplined software engineering practices to AI-assisted coding. It orchestrates a team of specialized agents through Plan-Approve-Execute workflows, DAG-based task management, validation gates, and checkpoint compression — delivering auditable, high-quality results.

> Evolved from DEV-Team-Recruiter. See [MIGRATION.md](MIGRATION.md) for the migration path.

---

## Quick Start

### Prerequisites

See [PREREQUISITES.md](PREREQUISITES.md) for full details.

- **GitHub Copilot**: VS Code with GitHub Copilot extension (+ Copilot Chat)
- **Gemini**: `@google/gemini-cli` installed globally
- **Opencode**: `opencode-ai` installed globally
- Node.js 18+ (for MCP servers via `npx`)
- Git (for worktree isolation)

### Install

#### For GitHub Copilot
1. **Copy the `.github/` directory** to your project root
2. **Copy `.vscode/mcp.json`** to your project root

#### For Gemini
1. **Copy the `.gemini/` directory** to your project root

#### For Opencode
1. **Copy the `.opencode/` directory** to your project root

#### Common for all
1. **Copy `AGENTS.md`** to your project root
2. **Create the `docs/` directory** with subdirectories: `tasks/`, `plans/`, `decisions/`, `checkpoints/`, `artifacts/`

### Use

**GitHub Copilot**: Open Copilot Chat and invoke any slash command:
```
/new-project "My SaaS Application"
```

**Gemini**: Run `gemini` in your terminal and invoke commands.

**Opencode**: Run `opencode` in your terminal and invoke commands.

The orchestrator will propose a plan, wait for your approval, then execute through the agent team.

---

## Architecture Overview

emage.code uses a 6-layer architecture:

```
┌─────────────────────────────────────────┐
│  Layer 1: Commands (16 slash commands)  │  ← User entry points
├─────────────────────────────────────────┤
│  Layer 2: Orchestration                 │  ← Plan-Approve-Execute engine
│           (orchestrator + poc-orch.)    │
├─────────────────────────────────────────┤
│  Layer 3: Agents (27 specialists)       │  ← Domain experts execute tasks
├─────────────────────────────────────────┤
│  Layer 4: Skills (22 reusable)          │  ← Shared capabilities & protocols
├─────────────────────────────────────────┤
│  Layer 5: Memory (docs/ + MCP Memory)   │  ← Task state, checkpoints, artifacts
├─────────────────────────────────────────┤
│  Layer 6: MCP Servers (7 integrations)  │  ← External tool access
└─────────────────────────────────────────┘
```

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Plan-Approve-Execute** | All non-trivial work requires a user-approved plan before execution begins |
| **Task Management (DAG)** | Structured task list with dependencies, ownership, and status in `docs/tasks/` |
| **Checkpoints** | Phase-boundary summaries that compress context for efficient delegation |
| **Validation Gates** | Structured PASS / CONDITIONAL_PASS / FAIL verdicts at quality checkpoints |
| **Artifact Versioning** | Immutable `<type>-v<N>.md` naming with explicit dependency references |
| **Blocker Escalation** | Typed blocker reports with deterministic routing and 2-retry limit before user escalation |
| **Token Governance** | Per-phase token budgets with tracking, warnings, and compression triggers |

---

## Available Commands

| Command | Description |
|---------|-------------|
| `/new-project` | Initialize a new project with full team setup |
| `/new-feature` | Plan and implement a new feature |
| `/bug-report` | Investigate and fix a reported bug |
| `/code-review` | Comprehensive code review with quality gates |
| `/security-audit` | Security analysis and vulnerability assessment |
| `/prepare-release` | Release preparation with checklist |
| `/sprint-status` | Current sprint overview and progress |
| `/team-status` | Full team status across all agents |
| `/new-poc` | Spin up a proof-of-concept with the PoC team |
| `/evaluate-poc` | Evaluate a completed PoC for production viability |
| `/poc-demo` | Generate a demo from a PoC |
| `/validate-workflow` | Validate a workflow against protocol rules |
| `/plan` | Explicitly enter plan mode for any task |
| `/batch` | Decompose sweeping changes into isolated parallel units |
| `/skillify` | Capture a successful workflow as a reusable skill file |
| `/consolidate-memory` | Review and organize persistent memory (promote/prune) |

---

## Agent Roster

### Production Team (14 agents)

| Agent | Role |
|-------|------|
| `orchestrator` | Central coordinator — Plan-Approve-Execute engine, task DAG management |
| `product-owner` | Requirements, user stories, acceptance criteria |
| `solution-architect` | Architecture decisions, system design, ADRs |
| `tech-lead` | Technical direction, code standards enforcement |
| `scrum-master` | Sprint management, blocker resolution, velocity |
| `frontend-developer` | UI/UX implementation |
| `backend-developer` | API, business logic, server-side |
| `database-engineer` | Schema design, migrations, query optimization |
| `qa-engineer` | Testing strategy, test execution, quality gates |
| `security-engineer` | Security analysis, threat modeling, compliance |
| `devops-engineer` | CI/CD, infrastructure, deployment |
| `technical-writer` | Documentation, API docs, user guides |
| `release-manager` | Release coordination, changelog, versioning |
| `ux-designer` | User experience design, wireframes, accessibility |

### PoC Team (13 agents)

| Agent | Role |
|-------|------|
| `poc-orchestrator` | Lightweight PoC coordination |
| `technology-scout` | Technology research and evaluation |
| `feasibility-agent` | Technical feasibility analysis |
| `scaffolding-agent` | Rapid project scaffolding |
| `demo-agent` | Demo creation and presentation |
| `evaluation-agent` | PoC evaluation against criteria |
| `data-mockup-agent` | Test data and mock generation |
| `integration-agent` | Integration testing and API connectivity |
| `technical-debt-narrator` | Technical debt tracking and reporting |
| `poc-devops-engineer` | Lightweight DevOps for PoCs |
| `poc-qa-engineer` | Lightweight QA for PoCs |
| `poc-security-engineer` | Lightweight security for PoCs |
| `poc-technical-writer` | Lightweight documentation for PoCs |

---

## Skills Library

| # | Skill | Purpose |
|---|-------|---------|
| 1 | `api-design` | REST/GraphQL API design patterns |
| 2 | `ci-cd-pipeline` | CI/CD pipeline configuration |
| 3 | `code-review` | Structured code review process |
| 4 | `context-window-management` | Token budget awareness and compression |
| 5 | `dependency-graphing` | Dependency analysis and visualization |
| 6 | `gitlab-management` | GitLab API operations |
| 7 | `poc-evaluation` | PoC evaluation framework |
| 8 | `project-planning` | Project planning and estimation |
| 9 | `rapid-prototyping` | Fast prototyping patterns |
| 10 | `release-workflow` | Release process management |
| 11 | `technical-debt-tracking` | Tech debt identification and tracking |
| 12 | `technology-scouting` | Technology research and comparison |
| 13 | `plan-approve-execute` | Plan-Approve-Execute protocol implementation |
| 14 | `task-management` | DAG-based task state management |
| 15 | `checkpoint-protocol` | Phase-boundary checkpoint compression |
| 16 | `blocker-escalation` | Typed blocker reporting and routing |
| 17 | `validation-gates` | PASS/CONDITIONAL_PASS/FAIL verdict framework |
| 18 | `cost-token-governance` | Per-phase token budget tracking |
| 19 | `testing-strategy` | Comprehensive testing strategies |
| 20 | `skillify` | Workflow → reusable skill capture |
| 21 | `memory-management` | MCP Memory promote/prune operations |
| 22 | `worktree-isolation` | Git worktree-based isolation for parallel work |

---

## File Structure

```
your-project/
├── .github/
│   ├── agents/
│   │   ├── orchestrator.agent.md
│   │   ├── poc-orchestrator.agent.md
│   │   ├── product-owner.agent.md
│   │   ├── solution-architect.agent.md
│   │   ├── tech-lead.agent.md
│   │   ├── scrum-master.agent.md
│   │   ├── frontend-developer.agent.md
│   │   ├── backend-developer.agent.md
│   │   ├── database-engineer.agent.md
│   │   ├── qa-engineer.agent.md
│   │   ├── security-engineer.agent.md
│   │   ├── devops-engineer.agent.md
│   │   ├── technical-writer.agent.md
│   │   ├── release-manager.agent.md
│   │   ├── ux-designer.agent.md
│   │   ├── technology-scout.agent.md
│   │   ├── feasibility-agent.agent.md
│   │   ├── scaffolding-agent.agent.md
│   │   ├── demo-agent.agent.md
│   │   ├── evaluation-agent.agent.md
│   │   ├── data-mockup-agent.agent.md
│   │   ├── integration-agent.agent.md
│   │   ├── technical-debt-narrator.agent.md
│   │   ├── poc-devops-engineer.agent.md
│   │   ├── poc-qa-engineer.agent.md
│   │   ├── poc-security-engineer.agent.md
│   │   └── poc-technical-writer.agent.md
│   ├── skills/
│   │   ├── api-design/
│   │   ├── blocker-escalation/
│   │   ├── checkpoint-protocol/
│   │   ├── ci-cd-pipeline/
│   │   ├── code-review/
│   │   ├── context-window-management/
│   │   ├── cost-token-governance/
│   │   ├── dependency-graphing/
│   │   ├── gitlab-management/
│   │   ├── memory-management/
│   │   ├── plan-approve-execute/
│   │   ├── poc-evaluation/
│   │   ├── project-planning/
│   │   ├── rapid-prototyping/
│   │   ├── release-workflow/
│   │   ├── skillify/
│   │   ├── task-management/
│   │   ├── technical-debt-tracking/
│   │   ├── technology-scouting/
│   │   ├── testing-strategy/
│   │   ├── validation-gates/
│   │   └── worktree-isolation/
│   ├── prompts/
│   │   ├── batch.prompt.md
│   │   ├── bug-report.prompt.md
│   │   ├── code-review.prompt.md
│   │   ├── consolidate-memory.prompt.md
│   │   ├── evaluate-poc.prompt.md
│   │   ├── new-feature.prompt.md
│   │   ├── new-poc.prompt.md
│   │   ├── new-project.prompt.md
│   │   ├── plan.prompt.md
│   │   ├── poc-demo.prompt.md
│   │   ├── prepare-release.prompt.md
│   │   ├── security-audit.prompt.md
│   │   ├── skillify.prompt.md
│   │   ├── sprint-status.prompt.md
│   │   ├── team-status.prompt.md
│   │   └── validate-workflow.prompt.md
│   ├── instructions/
│   │   ├── coding-standards.instructions.md
│   │   ├── git-workflow.instructions.md
│   │   ├── poc-guidelines.instructions.md
│   │   └── security-guidelines.instructions.md
│   └── hooks/
│       └── post-edit-reminder.json
├── .vscode/
│   └── mcp.json
├── AGENTS.md
└── docs/
    ├── tasks/
    │   ├── active-tasks.md
    │   └── completed-tasks.md
    ├── plans/
    ├── decisions/
    ├── checkpoints/
    └── artifacts/
```

---

## MCP Server Configuration

The `.vscode/mcp.json` configures 7 MCP servers:

| Server | Purpose |
|--------|---------|
| `filesystem` | Local file operations via `@anthropic/mcp-filesystem` |
| `memory` | Persistent key-value memory via `@anthropic/mcp-memory` |
| `brave-search` | Web search via Brave Search API |
| `gitlab` | GitLab API operations (issues, MRs, pipelines) |
| `sequential-thinking` | Complex reasoning and multi-step analysis |
| `playwright` | Browser automation and testing |
| `context7` | Documentation lookup for libraries and frameworks |

---

## Migration from DEV-Team-Recruiter

If you're upgrading from DEV-Team-Recruiter, see [MIGRATION.md](MIGRATION.md) for:
- File mapping (old → new)
- Breaking changes
- New features and capabilities
- Step-by-step migration instructions

---

## Documentation

| Document | Location |
|----------|----------|
| Active tasks | `docs/tasks/active-tasks.md` |
| Completed tasks | `docs/tasks/completed-tasks.md` |
| Plans | `docs/plans/` |
| Architecture decisions | `docs/decisions/` |
| Phase checkpoints | `docs/checkpoints/` |
| Versioned artifacts | `docs/artifacts/` |
