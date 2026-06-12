# Quick Start

Get emage.code running in your project in five minutes.

## 1. Install (recommended)

From a clone of this repository:

```bash
git clone https://gitlab.com/em-age/emage.code.git
cd emage.code
scripts/install.sh --target /path/to/your-project --platform cursor
```

| Platform | `--platform` value |
|----------|------------------|
| Cursor | `cursor` |
| GitHub Copilot (VS Code) | `github` |
| Gemini CLI | `gemini` |
| Opencode | `opencode` |
| Pi | `pi` |
| All platforms | `all` |

Makefile shortcut: `make install TARGET=/path/to/your-project PLATFORM=cursor`

**Update** an existing install (requires `AGENTS.md` in the target):

```bash
scripts/install.sh --target /path/to/your-project --platform cursor --update
```

## 2. Manual copy (alternative)

| Platform | What to copy from `implementation/` |
|----------|-------------------------------------|
| GitHub Copilot | `.github/` + `.vscode/mcp.json` |
| Gemini CLI | `.gemini/` |
| Opencode | `.opencode/` |
| Cursor | `.cursor/` |
| Pi | `.pi/` |

Plus always: `AGENTS.md` and `docs/`.

## 3. Set MCP env vars

The generated `mcp.json` needs credentials for the MCP servers you want active:

```bash
export GITLAB_PERSONAL_ACCESS_TOKEN=glpat-...
export BRAVE_API_KEY=...
```

See [MCP Servers](mcp-servers). Only `core` servers are required.

## 4. Invoke the orchestrator

```
/discover-skills "start new project"
/new-project "My SaaS application"
```

Use `/handoff` before ending a session to resume cleanly later.

## 5. Track progress

- `docs/tasks/active-tasks.md` — task ledger
- `docs/checkpoints/` — phase snapshots
- `docs/decisions/` — ADRs

## 6. Maintainers — release docs gate

```bash
python3 scripts/verify-release-docs.py --tag vX.Y.Z
```

## 7. Schema-first workflows

See [Implementation Guide](implementation-guide) for cookbooks, triggers, packaging, and validation commands.

## Troubleshooting

- **Agents not loading?** Confirm format: `.mdc` (Cursor), `.agent.md` (Copilot), `.md` (Gemini/Opencode/Pi).
- **MCP failing?** Check env vars and network access.
- **Drift after editing knowledge?** Run `make sync` from repo root.
