# emage.code — Vision & Overview

## What Is emage.code?

**emage.code** is the next-generation evolution of DEV-Team-Recruiter, purpose-built for VS Code + GitHub Copilot. It transforms an IDE into an autonomous software development organization by combining:

- The proven **multi-agent team architecture** from DEV-Team-Recruiter (27 specialized agents, dual-track orchestration)
- The **advanced orchestration primitives** discovered in Claude Code (DAG-based task management, worktree isolation, team coordination, layered memory, batch pipelines)
- **Native VS Code Copilot capabilities** (`.agent.md`, `.prompt.md`, `.instructions.md`, skills, hooks, MCP servers)

## Why "emage.code"?

The name reflects a shift from "recruiting" pre-built agent configs to **emerging** intelligent agent behavior through better primitives: structured coordination, persistent state, self-improving workflows, and adaptive memory.

## What Changes from DEV-Team-Recruiter?

| Dimension | DEV-Team-Recruiter | emage.code |
|-----------|-------------------|------------|
| **Platform** | 4 platforms (GitHub Copilot, Gemini CLI, Claude Code, OpenCode) | VS Code + GitHub Copilot, Gemini CLI, and OpenCode |

## Coordination | Implicit delegation via agent instructions | Explicit task DAG with dependency tracking and status protocol |
| **State** | MCP Memory server (unstructured) | Layered memory hierarchy (session → project → team) with structured checkpoints |
| **Parallelism** | Hoped-for (instructions say "parallel") | Git worktree isolation per agent with file-ownership boundaries |
| **Failure handling** | None documented | Validation gates, blocker protocol, retry + escalation |
| **Self-improvement** | Static config files | Skillify workflow (capture successful patterns as reusable skills) |
| **Planning** | Orchestrator decides internally | Plan-Approve-Execute cycle with user sign-off |
| **Batch operations** | Not supported | Decompose → Isolate → Spawn → Track → Merge pipeline |
| **Security model** | Instructions-only | Immutable security policy injection + permission classification |
| **Observability** | `/team-status` (feature-flagged) | Real-time task board, spend telemetry, checkpoint compression |

## Design Principles

1. **Config-file native** — No custom VS Code extension required. Everything works via `.github/`, `.vscode/`, and MCP servers
2. **Progressive complexity** — Simple projects use 3-4 agents; complex projects scale to the full team
3. **Explicit over implicit** — Task dependencies, artifact lineage, and decision logs are structured and auditable
4. **Fail-safe over fail-fast** — Blockers create new tasks, not dead ends. Escalation has a deterministic path
5. **Context-efficient** — Agents receive only what they need. Checkpoint compression prevents token explosion
6. **Self-improving** — Successful workflows can be captured as skills. Memory consolidation prunes stale context
7. **User-in-the-loop** — Plans require approval. Destructive actions require confirmation. Progress is always visible

## Target User

A developer (solo or team) who wants to describe a feature, project, or proof-of-concept and have an AI agent team plan, design, implement, test, and deliver it — with real-time visibility and control at every stage.

## Scope of Initial Implementation

The implementation targets **VS Code with GitHub Copilot**, **Gemini CLI**, and **OpenCode** using:
- Native agent systems (`.agent.md` for Copilot, `.md` for Gemini/OpenCode)
- Commands and Prompts (`.prompt.md` slash commands for Copilot, `commands/` for Gemini/OpenCode)
- Instructions and rules (`.instructions.md` for Copilot, `instructions/` for Gemini/OpenCode)
- Reusable skills (`.md` skill cards)
- MCP servers for external tool access (GitLab, Playwright, Memory, etc.)
- Workspace conventions via `AGENTS.md`

Future portability to Claude Code is planned but the architecture should not preclude it.
