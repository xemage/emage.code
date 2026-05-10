# Quick Start

Get emage.code running in your project in five minutes.

## 1. Pick your platform

| Platform | What to copy |
|----------|--------------|
| GitHub Copilot (VS Code) | `v2/implementation/.github/` + `v2/implementation/.vscode/mcp.json` |
| Gemini CLI | `v2/implementation/.gemini/` |
| Opencode | `v2/implementation/.opencode/` |
| Cursor | `v2/implementation/.cursor/` |

Plus always: `AGENTS.md` and `docs/`.

## 2. Copy into your project

```bash
# Example: GitHub Copilot
git clone https://gitlab.com/em-age/emage.code.git
cd <your-project>
cp -r ../emage.code/v2/implementation/.github         .
mkdir -p .vscode && cp ../emage.code/v2/implementation/.vscode/mcp.json .vscode/
cp    ../emage.code/v2/implementation/AGENTS.md       .
cp -r ../emage.code/v2/implementation/docs            .
```

## 3. Set MCP env vars

The generated `mcp.json` needs credentials for the MCP servers you want active:

```bash
export GITLAB_PERSONAL_ACCESS_TOKEN=glpat-...
export BRAVE_API_KEY=...
# … see mcp.json for the full list
```

Only `core` MCP servers are required; `extended` ones are opt-in. See [MCP Servers](mcp-servers).

## 4. Invoke the orchestrator

In your AI assistant chat:

```
/new-project "My SaaS application"
```

The orchestrator will:
1. **Plan** — propose tasks, dependencies, and agent assignments
2. **Approve** — wait for your go-ahead
3. **Execute** — delegate to specialist agents (backend, frontend, qa, …)

## 5. Track progress

- `docs/tasks/active-tasks.md` — current task ledger
- `docs/checkpoints/` — phase-boundary snapshots
- `docs/decisions/` — ADRs

## Troubleshooting

- **Agents not loading?** Confirm your assistant supports the `.agent.md` (Copilot), `.md` (Gemini/Opencode), or `.mdc` (Cursor) format.
- **MCP server failing?** Check the env var is set and the server's network access works.
- **Slash commands not appearing?** Run `node v2/implementation/scripts/sync.mjs` and re-load your assistant.
