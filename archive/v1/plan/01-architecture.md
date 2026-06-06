# emage.code — Architecture

## System Architecture Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                        VS Code + Copilot                          │
│                                                                   │
│  User ──→ /command ──→ Orchestrator Agent                         │
│                            │                                      │
│               ┌────────────┼────────────────┐                     │
│               │            │                │                     │
│          Plan Phase    Execute Phase    Review Phase               │
│          (propose)     (coordinate)     (validate)                │
│               │            │                │                     │
│          User Approval  Task DAG         Quality Gates            │
│               │         ┌──┼──┐             │                     │
│               │         │  │  │             │                     │
│               ▼         ▼  ▼  ▼             ▼                     │
│          Specialist Agents (parallel via worktree isolation)       │
│                                                                   │
├───────────────────── Skill Layer ─────────────────────────────────┤
│  Reusable capabilities: planning, review, testing, governance...  │
│                                                                   │
├───────────────────── Memory Layer ────────────────────────────────┤
│  Session → Project (AGENTS.md / docs/) → Team (MCP Memory)       │
│                                                                   │
├───────────────────── MCP Servers ─────────────────────────────────┤
│  GitLab │ Playwright │ Memory │ Seq-Thinking │ Fetch │ Search     │
│                                                                   │
├───────────────────── Workspace ───────────────────────────────────┤
│  .github/agents/  .github/skills/  .github/prompts/              │
│  .github/instructions/  .github/hooks/  .vscode/mcp.json         │
│  AGENTS.md  docs/decisions/  docs/checkpoints/                    │
└───────────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### Layer 1: Command Surface (User → Orchestrator)

Slash commands (`.prompt.md`) are the entry points. Each command targets a specific orchestrator agent and defines the workflow.

| Command | Target | Purpose |
|---------|--------|---------|
| `/new-project` | `@orchestrator` | Full SDLC from idea to release |
| `/new-feature` | `@orchestrator` | Feature planning and implementation |
| `/new-poc` | `@poc-orchestrator` | Fast hypothesis validation |
| `/code-review` | `@tech-lead` | Structured code review |
| `/security-audit` | `@security-engineer` | OWASP Top 10 audit |
| `/prepare-release` | `@release-manager` | Version, changelog, gates |
| `/team-status` | `@orchestrator` | Operational visibility |
| `/batch` | `@orchestrator` | Parallel multi-agent implementation |
| `/plan` | `@orchestrator` | Plan-only mode (no execution) |
| `/evaluate-poc` | `@evaluation-agent` | PoC hypothesis verdict |
| `/poc-demo` | `@demo-agent` | Stakeholder demo packaging |

### Layer 2: Orchestration (Plan → Execute → Review)

The orchestrator operates in three phases:

**Plan Phase:**
1. Receive user request
2. Decompose into task graph with dependencies
3. Identify required agents and artifact flow
4. Present plan to user for approval
5. User approves, modifies, or rejects

**Execute Phase:**
1. Create task entries in structured format
2. Delegate to specialist agents with self-contained briefs
3. Track progress via checkpoint protocol
4. Handle blockers via escalation protocol
5. Enforce token budgets per phase

**Review Phase:**
1. Validation gates at phase boundaries
2. Tech Lead code review (pass/conditional/fail)
3. QA verification of acceptance criteria
4. Security audit for high-risk components
5. Integration checkpoint before merge

### Layer 3: Agent Team

```
Production Track:
  @orchestrator
    ├── @product-owner          (requirements, stories)
    ├── @solution-architect      (design, ADRs)
    ├── @scrum-master           (sprints, issues)
    ├── @tech-lead              (standards, review, merge gate)
    ├── @backend-developer      (APIs, services)
    ├── @frontend-developer     (UI, accessibility)
    ├── @database-engineer      (schema, migrations)
    ├── @qa-engineer            (testing, coverage)
    ├── @security-engineer      (OWASP, audit)
    ├── @devops-engineer        (CI/CD, Docker)
    ├── @release-manager        (versioning, changelog)
    ├── @technical-writer       (documentation)
    └── @ux-designer            (wireframes, flows)

PoC Track:
  @poc-orchestrator
    ├── @technology-scout        (option matrix, scouting)
    ├── @feasibility-agent       (risk assessment)
    ├── @scaffolding-agent       (project skeleton)
    ├── @integration-agent       (third-party wiring)
    ├── @data-mockup-agent       (synthetic data)
    ├── @demo-agent              (stakeholder demos)
    ├── @evaluation-agent        (hypothesis verdict)
    ├── @debt-narrator           (debt scorecard)
    ├── @poc-qa                  (happy-path testing)
    ├── @poc-security            (critical risks only)
    ├── @poc-writer              (minimal docs)
    └── @poc-devops              (local reproducibility)
```

### Layer 4: Skill Library

Skills are reusable capability cards that agents invoke on demand. They keep agent prompts compact by externalizing detailed guidance.

| Category | Skills |
|----------|--------|
| **Planning** | `project-planning`, `task-decomposition`, `dependency-graphing` |
| **Development** | `api-design`, `code-review`, `coding-standards-enforcement` |
| **Quality** | `testing-strategy`, `security-audit-checklist`, `validation-gates` |
| **Operations** | `ci-cd-pipeline`, `gitlab-management`, `release-workflow` |
| **Governance** | `context-window-management`, `cost-token-governance`, `checkpoint-protocol` |
| **PoC** | `technology-scouting`, `rapid-prototyping`, `poc-evaluation`, `technical-debt-tracking` |
| **Meta** | `skillify` (capture workflows as skills), `remember` (memory management) |

### Layer 5: Memory Hierarchy

```
┌─────────────────────────────────────┐
│ Layer 3: Team Memory                │  ← MCP Memory server (knowledge graph)
│   Cross-project decisions,          │    Persistent across sessions/projects
│   shared conventions, org patterns  │
├─────────────────────────────────────┤
│ Layer 2: Project Memory             │  ← AGENTS.md + docs/decisions/ + docs/checkpoints/
│   Architecture decisions (ADRs),    │    Committed to repo, versioned
│   checkpoint summaries, task state  │
├─────────────────────────────────────┤
│ Layer 1: Session Memory             │  ← In-conversation state
│   Current task context, active      │    Ephemeral, compressed at boundaries
│   blockers, progress updates        │
└─────────────────────────────────────┘
```

### Layer 6: MCP Server Infrastructure

| Server | Role | Used By |
|--------|------|---------|
| **GitLab** | Repository, issues, MRs, pipelines | Orchestrator, Scrum Master, DevOps, Release |
| **Playwright** | Browser automation, E2E testing | QA, Frontend, Demo Agent |
| **Memory** | Persistent knowledge graph | Orchestrator (team memory) |
| **Sequential Thinking** | Complex problem decomposition | Architect, Orchestrator |
| **Fetch** | Web content for research | Architect, Tech Lead, Developers |
| **Brave Search** | Technology discovery | Technology Scout, Feasibility |
| **Context7** | Framework/API documentation | Technology Scout, Integration |

## Key Architectural Decisions

### ADR-001: Config Files Over Custom Extension
**Decision:** Use native VS Code Copilot config files (`.agent.md`, `.prompt.md`, etc.) without a custom extension.
**Rationale:** Zero installation beyond Copilot. Config files are portable, versionable, and composable. Custom extensions add maintenance burden and installation friction.

### ADR-002: File-Based Task State Over MCP Task Server
**Decision:** Manage task state via structured markdown files in `docs/tasks/` rather than a custom MCP task server.
**Rationale:** Copilot agents can read/write files natively. File-based state is debuggable, versionable, and doesn't require additional server infrastructure. The orchestrator instructions enforce the task protocol.

### ADR-003: Worktree Isolation via Instructions
**Decision:** Instruct agents to work in separate git worktrees for parallel tasks, managed by the orchestrator.
**Rationale:** Git worktrees provide native file isolation without containers. The orchestrator creates worktrees, assigns agents, and merges results. This is a convention enforced by agent instructions, not a runtime constraint.

### ADR-004: Plan-Approve-Execute as Default Workflow
**Decision:** All non-trivial workflows require user approval of the plan before execution begins.
**Rationale:** Autonomous agent systems need guardrails. The plan phase is cheap (no code changes). User approval ensures alignment and prevents wasted work.

### ADR-005: Layered Memory with Checkpoint Compression
**Decision:** Three memory layers (session/project/team) with automatic checkpoint compression at phase boundaries.
**Rationale:** Long-running projects exhaust context windows. Checkpoint compression preserves essential state without token explosion. The memory hierarchy ensures the right information is available at the right scope.
