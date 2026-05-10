# emage.code Quick-Start Guide for OpenCode

Get your AI development team running in under 10 minutes.

---

## 1. Prerequisites

| Requirement | Version | Install |
|-------------|---------|---------|
| **OpenCode** | latest | `npm install -g opencode-ai` |
| **Node.js** | ≥ 18 | [nodejs.org](https://nodejs.org) |
| **Git** | any | [git-scm.com](https://git-scm.com) |

Optional (enables additional MCP servers):
- GitLab Personal Access Token → `GITLAB_PERSONAL_ACCESS_TOKEN`
- Brave Search API key → `BRAVE_API_KEY`
- GitLab API URL → `GITLAB_API_URL` (default: `https://gitlab.com/api/v4`)

---

## 2. Set Up

### Copy into your project

```bash
cp -r emage.code/implementation/.opencode  /path/to/your/project/.opencode
cp    emage.code/implementation/AGENTS.md  /path/to/your/project/AGENTS.md
```

Or if starting fresh, use this repo's `implementation/` folder directly as your project root.

### Set environment variables (optional)

```bash
# Linux / macOS
export GITLAB_PERSONAL_ACCESS_TOKEN=your_token
export GITLAB_API_URL=https://gitlab.com/api/v4
export BRAVE_API_KEY=your_key

# Windows (PowerShell)
$env:GITLAB_PERSONAL_ACCESS_TOKEN = "your_token"
$env:GITLAB_API_URL = "https://gitlab.com/api/v4"
$env:BRAVE_API_KEY = "your_key"
```

### Start OpenCode in your project

```bash
cd /path/to/your/project
opencode
```

---

## 3. Your First Conversation

### Start a new project

Type in the OpenCode chat:

```
/new-project Build a REST API for a task management app with user auth, CRUD operations, and PostgreSQL.
```

The **Orchestrator** will:
1. Ask any clarifying questions
2. Write a plan document to `docs/plans/`
3. Show you the plan and ask for approval
4. After approval, coordinate the full team: Product Owner → Solution Architect → Scrum Master → Developers → QA → Security → Release

### Start a PoC

```
/new-poc Can we use WebSockets for real-time collaboration in our app? Hypothesis: latency < 100ms for 50 concurrent users.
```

### Add a feature to an existing project

```
/new-feature Add OAuth2 social login (Google + GitHub) to the existing auth system.
```

---

## 4. Available Commands

All commands use `/command-name` syntax in the OpenCode chat.

### Project Workflow

| Command | Description |
|---------|-------------|
| `/new-project` | Start a new project — full team orchestration |
| `/new-feature` | Plan and implement a new feature |
| `/new-poc` | Start a hypothesis-driven proof of concept |
| `/plan` | Plan-only mode — get a plan without executing |
| `/batch` | Decompose a large change into parallel worktree units |

### Review & Validation

| Command | Description |
|---------|-------------|
| `/code-review` | Structured code review with PASS/FAIL verdict |
| `/security-audit` | OWASP audit with severity classification |
| `/validate-workflow` | Validate a workflow against protocol gates |
| `/evaluate-poc` | Formal PoC evaluation with handoff checklist |

### Status & Reporting

| Command | Description |
|---------|-------------|
| `/team-status` | Full team status with task DAG and blockers |
| `/sprint-status` | Sprint progress, velocity, and forecasts |
| `/bug-report` | Structured bug report with task creation |
| `/prepare-release` | Release gate checklist and changelog generation |

### Utilities

| Command | Description |
|---------|-------------|
| `/skillify` | Capture the current workflow as a reusable skill |
| `/consolidate-memory` | Review and prune MCP Memory entries |
| `/poc-demo` | Prepare a stakeholder demo for a PoC |

---

## 5. Agent Roster

Agents are invoked automatically by the Orchestrator. You interact only with:

- `@orchestrator` — for production projects
- `@poc-orchestrator` — for PoC work

### Production Team

| Agent | Responsibility |
|-------|---------------|
| `product-owner` | Requirements, user stories, acceptance criteria |
| `solution-architect` | System design, ADRs, `architecture-vN.md` |
| `scrum-master` | Sprint planning, task tracking, velocity |
| `tech-lead` | Code review, coding standards, merge gate |
| `backend-developer` | REST APIs, services, business logic |
| `frontend-developer` | UI components, state management, UX integration |
| `database-engineer` | Schema design, migrations, query optimization |
| `qa-engineer` | Test plans, automation, QA validation gate |
| `security-engineer` | OWASP audit, security validation gate |
| `devops-engineer` | CI/CD pipelines, infrastructure, environments |
| `release-manager` | Release gates, changelogs, version management |
| `technical-writer` | Documentation, ADRs, artifact lineage |
| `ux-designer` | Wireframes, user flows, design specs |

### PoC Team

| Agent | Responsibility |
|-------|---------------|
| `technology-scout` | Technology landscape research |
| `feasibility-agent` | Risk and feasibility assessment |
| `scaffolding-agent` | Rapid project scaffolding |
| `integration-agent` | Third-party integration prototyping |
| `data-mockup-agent` | Mock data and fixtures |
| `demo-agent` | Stakeholder demo preparation |
| `evaluation-agent` | PoC success/failure verdict |
| `technical-debt-narrator` | Debt inventory and scoring |
| `poc-qa-engineer` | Lightweight PoC testing |
| `poc-security-engineer` | Critical security checks for PoC |
| `poc-technical-writer` | PoC documentation |
| `poc-devops-engineer` | PoC deployment and environment |

---

## 6. How It Works

### Plan-Approve-Execute

Every non-trivial request follows this cycle:

```
User Request
     │
     ▼
 PLAN PHASE ──── Orchestrator decomposes the request into tasks,
     │            writes docs/plans/plan-<id>.md, presents summary
     │
     ▼
 APPROVAL ─────  "Shall I proceed?" — you approve, modify, or reject
     │
     ▼
 EXECUTE PHASE ── Orchestrator delegates tasks to specialist agents,
     │             tracks progress in docs/tasks/active-tasks.md
     │
     ▼
 CHECKPOINTS ──── Written at each phase boundary to docs/checkpoints/
     │
     ▼
 GATES ─────────── Tech Lead / QA / Security / Release Manager
                    produce PASS / CONDITIONAL_PASS / FAIL verdicts
```

### Task Management

All work is tracked in markdown tables:

```
docs/tasks/
├── active-tasks.md      ← All in-flight tasks (TASK-001, TASK-002, ...)
└── completed-tasks.md   ← Archived completed tasks
```

Task lifecycle: `pending → in_progress → blocked → in_review → done`

### Artifact Versioning

Deliverables are never overwritten — new versions are created:

```
docs/artifacts/
├── requirements-v1.md
├── requirements-v2.md   ← updated requirements
├── architecture-v1.md
└── architecture-v2.md   ← revised architecture
```

### Blocker Escalation

If an agent gets stuck:
1. It reports a structured blocker (`technical` / `dependency` / `unclear_requirements` / `external`)
2. The Orchestrator routes to the appropriate resolver
3. After 2 failed retries, the Orchestrator escalates to you

---

## 7. MCP Servers

The `opencode.json` configures 19 MCP servers. They start automatically when needed.

### Core (always available)

| Server | Package | Purpose |
|--------|---------|---------|
| `memory` | `@modelcontextprotocol/server-memory` | Persistent runtime facts across sessions |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Complex multi-step reasoning |
| `fetch` | `mcp-fetch-server` | Fetch external URLs and APIs |
| `context7` | remote: mcp.context7.com | Up-to-date library documentation |

### Integrations (require env vars)

| Server | Env Var Required | Purpose |
|--------|-----------------|---------|
| `gitlab` | `GITLAB_PERSONAL_ACCESS_TOKEN` | Issues, MRs, CI/CD |
| `brave` | `BRAVE_API_KEY` | Web search |
| `github` | GitHub token | GitHub repos |
| `supabase` | Supabase key | Supabase projects |
| `postgresql` | DB URL | Direct DB access |

### Tools (auto-installed via npx)

`playwright`, `filesystem`, `git`, `e2b`, `docker`, `redis`, `figma`, `notion`, `toolradar`

---

## 8. Skills Library

Skills are reference documents that agents load for specific tasks. They live in `.opencode/skills/<name>/SKILL.md`.

| Skill | When It's Used |
|-------|---------------|
| `plan-approve-execute` | Every project/feature kickoff |
| `task-management` | Creating and tracking tasks |
| `checkpoint-protocol` | Writing and compressing progress checkpoints |
| `validation-gates` | Code review, QA, security, release gates |
| `blocker-escalation` | Handling and routing blocked work |
| `dependency-graphing` | Building Mermaid task DAGs |
| `worktree-isolation` | Parallel agent work in git worktrees |
| `release-workflow` | Versioning, changelogs, hotfixes |
| `skillify` | Capturing workflows as reusable skills |
| `memory-management` | Managing MCP Memory and AGENTS.md |
| `cost-token-governance` | Token budgets and model routing |
| `code-review` | Structured review with VERDICT |
| `testing-strategy` | Test plans and coverage targets |
| `api-design` | REST/GraphQL API contracts |
| `ci-cd-pipeline` | Pipeline design and versioning |
| `technical-debt-tracking` | PoC debt inventory and promotion |

---

## 9. File Layout Reference

```
your-project/
├── AGENTS.md                          ← Workspace conventions (auto-loaded)
├── .opencode/
│   ├── opencode.json                  ← Config: instructions, MCP servers
│   ├── agents/                        ← 27 agent definitions
│   ├── commands/                      ← 16 slash commands
│   ├── skills/                        ← 22 skill reference docs
│   └── instructions/                  ← 4 always-on coding rules
└── docs/                              ← Created during project work
    ├── tasks/
    │   ├── active-tasks.md
    │   └── completed-tasks.md
    ├── plans/
    ├── checkpoints/
    ├── decisions/
    └── artifacts/
```

---

## 10. Tips

- **Plan first** — Use `/plan` before `/new-project` if you want to review the decomposition without committing to execution.
- **Check status anytime** — `/team-status` gives a full snapshot including task DAG, blockers, and token spend.
- **PoC before building** — Use `/new-poc` to validate risky assumptions before committing the full team.
- **Capture good workflows** — When you find an effective pattern, use `/skillify` to save it as a reusable skill.
- **Let the Orchestrator coordinate** — Don't invoke specialist agents directly; always go through `@orchestrator` so the task graph stays consistent.
- **Approve plans explicitly** — After the plan phase, reply `APPROVED`, `APPROVED_WITH_CHANGES: <details>`, or `REJECTED: <reason>`.

---

## 11. Troubleshooting

### MCP server fails to start

```bash
# Test a server manually
npx -y @modelcontextprotocol/server-memory

# Check Node version
node --version   # must be >= 18
```

### GitLab integration not working

Ensure the environment variable is set in the same shell session where you run `opencode`:

```bash
export GITLAB_PERSONAL_ACCESS_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
export GITLAB_API_URL=https://your-gitlab.com/api/v4   # omit for gitlab.com
opencode
```

### Agent doesn't follow the plan protocol

Explicitly mention the workflow: *"Use Plan-Approve-Execute. Write the plan to `docs/plans/` first."* The `AGENTS.md` file at the project root also reinforces this, ensure it's present.

### Tasks not being tracked

Check that `docs/tasks/active-tasks.md` exists. If not:

```bash
mkdir -p docs/tasks
echo "| ID | Title | Status | Assignee | Blocks | BlockedBy | Priority | Created |
|----|-------|--------|----------|--------|-----------|----------|---------|" > docs/tasks/active-tasks.md
```

---

*For full architecture details see [README.md](../README.md). For migrating from DEV-Team-Recruiter see [MIGRATION.md](../MIGRATION.md).*
