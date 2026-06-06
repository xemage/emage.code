# Research: Agents, Skills & Ecosystem Patterns v1

Based on: [Superpowers](https://github.com/obra/superpowers), [Awesome OpenCode](https://github.com/awesome-opencode/awesome-opencode), [Pi](https://pi.dev), [HackerNoon — 12 OpenCode Skills](https://hackernoon.com/twelve-opencode-skills-every-dev-team-should-steal)

Status: Research artifact for emage.code v3 roadmap (not implemented).

## Executive summary

Three converging patterns appear across ecosystems:

1. **Mandatory skill workflows** (Superpowers) — agents check skills before acting; skills encode process, not just prompts.
2. **Plugin/skill marketplaces** (OpenCode awesome list) — composable capabilities: memory, handoff, safety nets, background agents.
3. **Minimal harness + project `.pi/`** (Pi) — extensions, skills, prompts as files; `AGENTS.md` as shared context standard.

emage.code v3 already aligns on (1) via commands/skills/instructions and (3) via projection + `AGENTS.md`. Gaps vs ecosystem: background agents, handoff prompts, env safety plugins, and dynamic skill discovery.

---

## Superpowers ([obra/superpowers](https://github.com/obra/superpowers))

MIT agentic methodology with composable skills across Cursor, OpenCode, Gemini, Copilot, Codex.

### Core workflow (skills trigger automatically)

| Skill | Purpose | emage.code overlap |
|-------|---------|-------------------|
| `brainstorming` | Socratic design before code | `/plan`, `/new-project` (partial) |
| `using-git-worktrees` | Isolated branch per task | `worktree-isolation` skill |
| `writing-plans` | Bite-sized tasks with file paths | `project-planning`, task briefs |
| `subagent-driven-development` | Fresh subagent per task + 2-stage review | orchestrator delegation model |
| `executing-plans` | Batch execution with checkpoints | Plan-Approve-Execute |
| `test-driven-development` | RED-GREEN-REFACTOR enforced | coding-standards (weak TDD gate) |
| `requesting-code-review` | Pre-merge review checklist | `/code-review`, validation-gates |
| `receiving-code-review` | Rigorous response to feedback | — (gap) |
| `finishing-a-development-branch` | Merge/PR/keep/discard decision | release-workflow (partial) |
| `dispatching-parallel-agents` | Concurrent subagents | `/batch` (partial) |
| `systematic-debugging` | 4-phase root cause | — (gap as skill) |
| `verification-before-completion` | Evidence before success claims | validation-gates (partial) |

### Takeaways for emage.code

- Add **`receiving-code-review`** and **`systematic-debugging`** skills.
- Strengthen **`verification-before-completion`** as a mandatory pre-commit/release gate skill.
- Superpowers' "skills before any task" matches `using-superpowers` bootstrap — consider equivalent in `AGENTS.md` or orchestrator brief.

---

## Awesome OpenCode — Plugins ([plugins section](https://github.com/awesome-opencode/awesome-opencode#plugins))

High-value plugins for dev teams:

| Plugin | Capability | Steal for emage.code? |
|--------|------------|----------------------|
| **Oh My Opencode** / **Oh My Opencode Slim** | Background agents, LSP/AST/MCP tools, sub-agents | High — maps to orchestrator + subagents |
| **Micode** | Brainstorm-Plan-Implement, worktree isolation, AST tools | High — overlaps Plan-Approve-Execute |
| **Background Agents** | Async delegation, context persistence | High — trigger framework extension |
| **Agent Memory** | Letta-style persistent memory blocks | Medium — MCP memory exists |
| **Handoff** | Session handoff prompts | High — v3 handoff security model |
| **CC Safety Net** | Block destructive git/fs commands | High — security-engineer patterns |
| **Froggy** | Hooks + specialized agents + gitingest | Medium |
| **open-plan-annotator** | Browser UI for plan annotation | Low (PoC) |
| **Envsitter Guard** | Block `.env` reads | High — security guidelines |
| **Dynamic Context Pruning** | Prune stale tool outputs | Medium — token governance |
| **Agent Skills (JDT)** | Dynamic skill discovery | High — v3 packaging/registry |
| **Octto** | Interactive brainstorming UI | Low |

### Agents section highlights

- **Agentic** — modular agents + commands for structured SDLC
- **Claude Subagents** — production-ready subagent reference
- **Opencode Agents** — enhanced workflow configs

### Projects section highlights

- **Agent of Empires** — multi-session TUI + worktrees + Docker
- **Beads** — Steve Yegge task graph for agents
- **hcom** — cross-terminal agent messaging
- **Cupcake** — OPA/Rego policy layer for agents

---

## Pi ([pi.dev](https://pi.dev))

Minimal terminal coding agent; emage.code now projects to `.pi/`:

| Pi concept | emage.code projection |
|------------|----------------------|
| `AGENTS.md` | Root + `knowledge/` → workspace copy |
| `.pi/prompts/` | `knowledge/commands/` → slash templates |
| `.pi/skills/` | `knowledge/skills/` |
| `.pi/instructions/` | `knowledge/instructions/` |
| `.pi/agents/` | `knowledge/agents/` (persona reference) |
| Extensions (TS) | Not projected — Pi-native extensions |
| `pi install` packages | Future: v3 packaging → pi packages |

---

## HackerNoon — 12 OpenCode Skills

Article focuses on transferable OpenCode skill patterns (full text paywalled). Themes from ecosystem alignment:

1. **Structured planning before implementation**
2. **Code review as a first-class skill**
3. **Git/worktree discipline**
4. **Test-first implementation**
5. **Debugging methodology**
6. **Context/memory management**
7. **Security guardrails on destructive ops**
8. **Handoff between sessions**
9. **Parallel agent delegation**
10. **Skill discovery/packaging**
11. **Token/context pruning**
12. **Verification before declaring done**

Most map to Superpowers + Awesome OpenCode entries above.

---

## Recommended emage.code v3 follow-ups

| Priority | Item | Source |
|----------|------|--------|
| P1 | `systematic-debugging` skill | Superpowers |
| P1 | `receiving-code-review` skill | Superpowers |
| P1 | Handoff prompt templates in triggers | OpenCode Handoff plugin |
| P1 | Destructive-command guard in security guidelines | CC Safety Net |
| P2 | Background agent trigger recipes | Oh My Opencode |
| P2 | Dynamic skill discovery via v3 packaging | Agent Skills JDT |
| P2 | Pi extension bridge (optional) | pi.dev extensibility |
| P3 | Plan annotation UI | open-plan-annotator |

---

## References

- Superpowers: https://github.com/obra/superpowers
- Awesome OpenCode: https://github.com/awesome-opencode/awesome-opencode
- Pi coding agent: https://pi.dev / https://github.com/badlogic/pi-mono
- HackerNoon article: https://hackernoon.com/twelve-opencode-skills-every-dev-team-should-steal
