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

`--update` replaces each platform tree (`.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.claude/`, `.cline/`, `.clinerules/`) and keeps the files the harness never ships: `.claude/settings.json`, `.claude/settings.local.json`, and under `.github/` the `workflows/`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE`, `CODEOWNERS`, `dependabot.yml`, `dependabot.yaml`, `FUNDING.yml` and `copilot-instructions.md`. Each platform's MCP/settings config is merged. In `docs/tasks/`, the two ledgers are rewritten: `T<NNN>` task rows and the prose around the table are kept, other table rows are dropped with a warning.

To refresh only the harness projections (platform trees, MCP configs, `AGENTS.md`, and `CLAUDE.md` for Claude Code) and touch nothing under `docs/` or `implementation/`:

```bash
scripts/install.sh --target /path/to/your-project --platform cursor --projections-only
```

`--projections-only` cannot be combined with `--update`, needs an existing install, and does not install the MCP server runtime source.

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
export GITLAB_API_URL=...
export BRAVE_API_KEY=...
export HINDSIGHT_MCP_URL=...
```

The `extended` servers use `CWSO_MCP_URL`, `CWSO_BEARER_TOKEN`, `CWSO_ORIGIN` and `TOOLRADAR_API_KEY`. See [MCP Servers](mcp-servers) for the full table. Only `core` servers are required.

Using the PoC track? Its security scan runs on the `poc-security-audit` server, which needs a one-time Python dependency install, `git` 2.40 or newer and, on Claude Code, an allow rule that you add yourself. See [MCP Servers](mcp-servers#poc-security-scan-server-poc-security-audit).

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
