# Canonical knowledge base

This folder is the **single source of truth** for every emage.code platform integration. Files here are platform-neutral; the sync script (`scripts/sync.mjs`) projects them into per-platform folders (`.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`).

> **Never edit files inside the generated platform folders.** Edit here, then re-run sync.

## Layout

| Path | Purpose | Schema |
|------|---------|--------|
| `agents/<name>.md` | Agent definition (1 file per agent) | `schemas/agent.schema.json` |
| `commands/<name>.md` | Slash-command prompt | `schemas/command.schema.json` |
| `instructions/<name>.md` | Always-on or glob-scoped guidance | `schemas/instruction.schema.json` |
| `skills/<skill-name>/SKILL.md` | Reusable capability | `schemas/skill.schema.json` |
| `mcp/servers.yaml` | MCP server registry (single source) | inline |

## Frontmatter — canonical schema

The canonical format uses a **YAML array** for `tools`. Per-platform transforms (e.g. Opencode's object form) are applied automatically by the sync engine.

### Agents (`agents/<name>.md`)

```yaml
---
name: "Display Name"
description: "One- or two-sentence description used by the host platform."
tools: [read, search, edit, execute, agent, web, todo, mcp__gitlab, mcp__memory]
agents: [list, of, subagent, names]    # only for orchestrators
---
```

### Commands (`commands/<name>.md`)

```yaml
---
description: "What this slash command does."
agent: "orchestrator"
argument-hint: "Hint shown to the user when invoking the command."
---
```

### Instructions (`instructions/<name>.md`)

```yaml
---
description: "When this guidance applies."
applyTo: "**/*.{ts,js,py}"             # glob; absent = always-on
---
```

### Skills (`skills/<name>/SKILL.md`)

```yaml
---
name: skill-name
description: "What capability this skill provides."
---
```

## Authoring rules

1. **One canonical version.** Do not maintain platform-specific copies of bodies.
2. **Markdown-only bodies.** No platform-specific link syntax, no extension-specific blocks.
3. **References by name, not path.** Refer to other knowledge artifacts by name (`see skill: plan-approve-execute`); the sync engine handles platform paths.
4. **Tools list is canonical.** Add or remove tools here only; platform transforms convert representation.
5. **MCP servers are registered in `mcp/servers.yaml`.** Reference them in agent `tools:` as `mcp__<server-name>`.
6. **Run `node scripts/sync.mjs` after every change.** CI rejects PRs where committed platform folders drift from `knowledge/`.
