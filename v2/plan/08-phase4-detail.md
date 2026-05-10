# 08 — Phase 4 detail: Commands surface

> Backfill of the v1 Phase-4 placeholder.

## Goal
16 user-invocable slash commands cover the day-to-day developer flow. All commands route to either `orchestrator` or `poc-orchestrator`.

## Inventory

| Command | Routes to | Purpose |
|---------|-----------|---------|
| `/new-project` | orchestrator | Greenfield project from idea |
| `/new-feature` | orchestrator | Feature on existing codebase |
| `/bug-report` | orchestrator | Investigate + fix bug |
| `/code-review` | orchestrator → tech-lead | PR review with verdict |
| `/security-audit` | orchestrator → security-engineer | Vuln assessment |
| `/prepare-release` | orchestrator → release-manager | Release prep + checklist |
| `/sprint-status` | orchestrator → scrum-master | Sprint snapshot |
| `/team-status` | orchestrator | Cross-agent status report |
| `/plan` | orchestrator | Re-run plan phase only |
| `/consolidate-memory` | orchestrator | MCP memory housekeeping |
| `/validate-workflow` | orchestrator | Self-test: protocol compliance |
| `/skillify` | orchestrator | Promote a recurring pattern to a skill |
| `/batch` | orchestrator | Run a sequence of commands |
| `/new-poc` | poc-orchestrator | Greenfield PoC |
| `/evaluate-poc` | poc-orchestrator → evaluation-agent | PoC pass/fail review |
| `/poc-demo` | poc-orchestrator → demo-agent | Generate PoC demo script |

## Command file shape

```markdown
---
description: "What the command does, one short sentence."
agent: "orchestrator"
argument-hint: "What the user should type after the command."
---

<Imperative prompt body. The orchestrator interprets this as the user's request.>

## Phase 1: Plan-Approve-Execute
## Phase 2: Execute
## Phase 3: Review
```

## Acceptance criteria
- [ ] All 16 commands present in `knowledge/commands/`.
- [ ] Every command's `agent` field exists in `knowledge/agents/`.
- [ ] Bodies do not reference platform-specific paths.
