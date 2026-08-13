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
| Claude Code | `claude-code` |
| All platforms | `all` |

Makefile shortcut: `make install TARGET=/path/to/your-project PLATFORM=cursor`

**Update** an existing install (requires `AGENTS.md` in the target):

```bash
scripts/install.sh --target /path/to/your-project --platform cursor --update
```

On update, listed tasks in `docs/tasks/active-tasks.md` and `docs/tasks/completed-tasks.md` are preserved.

## 2. Manual copy (alternative)

| Platform | What to copy from `implementation/` |
|----------|-------------------------------------|
| GitHub Copilot | `.github/` + `.vscode/mcp.json` |
| Gemini CLI | `.gemini/` |
| Opencode | `.opencode/` |
| Cursor | `.cursor/` |
| Pi | `.pi/` |
| Claude Code | `.claude/` + `.mcp.json` + `CLAUDE.md` |

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

## 6. Contributing or building from source?

This page covers everyday use only. To build from source, run tests, or cut a
release, see [CONTRIBUTING.md](https://gitlab.com/em-age/emage.code/-/blob/main/CONTRIBUTING.md).

## 7. Schema-first workflows

See [Implementation Guide](implementation-guide) for cookbooks, triggers, packaging, and validation commands.

## Troubleshooting

- **Agents not loading?** Confirm format: `.mdc` (Cursor), `.agent.md` (Copilot), `.md` (Gemini/Opencode/Pi/Claude Code).
- **MCP failing?** Check env vars and network access.
- **Drift after editing knowledge?** Run `make sync` from repo root.
