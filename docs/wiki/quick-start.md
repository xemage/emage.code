# Quick Start

Get emage.code running in your project in five minutes.

## 1. Pick your platform

| Platform | What to copy |
|----------|--------------|
| GitHub Copilot (VS Code) | `v3/implementation/.github/` + `v3/implementation/.vscode/mcp.json` |
| Gemini CLI | `v3/implementation/.gemini/` |
| Opencode | `v3/implementation/.opencode/` |
| Cursor | `v3/implementation/.cursor/` |
| Pi | `v3/implementation/.pi/` |

Plus always: `AGENTS.md` and `docs/`.

## 2. Copy into your project

```bash
# Example: GitHub Copilot
git clone https://gitlab.com/em-age/emage.code.git
cd <your-project>
cp -r ../emage.code/v3/implementation/.github         .
mkdir -p .vscode && cp ../emage.code/v3/implementation/.vscode/mcp.json .vscode/
cp    ../emage.code/v3/implementation/AGENTS.md       .
cp -r ../emage.code/v3/implementation/docs            .

# Pi (terminal agent)
cp -r ../emage.code/v3/implementation/.pi           .pi/
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
/discover-skills "start new project"
/new-project "My SaaS application"
```

Use `/handoff` before ending a session to resume cleanly later.

The orchestrator will:
1. **Plan** — propose tasks, dependencies, and agent assignments
2. **Approve** — wait for your go-ahead
3. **Execute** — delegate to specialist agents (backend, frontend, qa, …)

## 5. Track progress

- `docs/tasks/active-tasks.md` — current task ledger
- `docs/checkpoints/` — phase-boundary snapshots
- `docs/decisions/` — ADRs

## 6. Release with documentation gate (maintainers)

Before creating a release tag, update release docs markers and validate:

```bash
python3 scripts/verify-release-docs.py --tag vX.Y.Z
```

The release pipeline blocks publication when this check fails.

## 7. Use v3 for schema-first workflows

When you want the next-generation workflow, follow the v3 implementation page:

1. Read [v3 Implementation](v3-implementation).
2. Validate the repository from the root:
	```bash
	python3 v3/implementation/scripts/check-v3.py --root v3/implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
	node v3/implementation/scripts/verify-v3.mjs --root v3/implementation
	```
3. Use the cookbook, package, trigger, and adapter workflows documented there.

## Troubleshooting

- **Agents not loading?** Confirm your assistant supports the `.agent.md` (Copilot), `.md` (Gemini/Opencode), or `.mdc` (Cursor) format.
- **MCP server failing?** Check the env var is set and the server's network access works.
- **Slash commands not appearing?** Run `node v3/implementation/scripts/sync-v3.mjs --root v3/implementation` and re-load your assistant.
