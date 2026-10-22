# Quick Start

Get emage.code running in your project in five minutes.

## 1. Install (recommended)

From a clone of this repository:

```bash
git clone https://gitlab.com/em-age/emage.code.git
cd emage.code
scripts/install.sh --target /path/to/your-project --platform claude-code
```

| Platform | `--platform` value |
|----------|------------------|
| GitHub Copilot (VS Code) | `github` |
| Gemini CLI | `gemini` |
| Opencode | `opencode` |
| Pi | `pi` |
| Claude Code | `claude-code` |
| Cline | `cline` |
| All platforms | `all` |

Makefile shortcut: `make install TARGET=/path/to/your-project PLATFORM=claude-code`

**Update** an existing install (requires `AGENTS.md` in the target):

```bash
scripts/install.sh --target /path/to/your-project --platform claude-code --update
```

`--update` replaces each platform tree (`.github/`, `.gemini/`, `.opencode/`, `.pi/`, `.claude/`, `.cline/`, `.clinerules/`) and keeps the files the harness never ships: `.claude/settings.json`, `.claude/settings.local.json`, and under `.github/` the `workflows/`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE`, `CODEOWNERS`, `dependabot.yml`, `dependabot.yaml`, `FUNDING.yml` and `copilot-instructions.md`. Each platform's MCP/settings config is merged, and so is an existing one on a plain install (no `--update`): the installer never overwrites a config wholesale. In `docs/tasks/`, the two ledgers are rewritten: `T<NNN>` task rows and the prose around the table are kept, other table rows are dropped with a warning, and a copy of the ledger as it was is saved first (`<ledger>.bak`, see below).

To refresh only the harness projections (platform trees, MCP configs, `AGENTS.md`, and `CLAUDE.md` for Claude Code) and touch nothing under `docs/` or `implementation/`:

```bash
scripts/install.sh --target /path/to/your-project --platform claude-code --projections-only
```

`--projections-only` cannot be combined with `--update`, needs an existing install, and does not install the MCP server runtime source.

### Files and notes the installer produces

All of this is read from `scripts/install.sh`, `scripts/merge-mcp-json.py` and `scripts/merge-task-docs.py` on 2026-10-22; none of it was run for this page **(unverified by a run)**.

**Files that can appear next to yours.** The installer writes through a temporary file or sibling and replaces the original in one step, so an interrupt leaves the old file or the new one, never a half-written one. The temporary names are removed on a normal failure; a leftover one means the process was killed hard, and you can delete it after you have looked at it.

| Name | Where | What it is |
|------|-------|------------|
| `.<name>.<random>.tmp`, for example `.mcp.json.k3x9a1.tmp` | Next to each merged MCP/settings config and its `.provenance.json` sidecar, and next to a merged task ledger | The merged text, written first and moved over the original with a rename. It has the mode of the file it replaces, so it is never more readable than the original |
| `<ledger>.bak`, then `<ledger>.bak.2`, `.bak.3` ... | `docs/tasks/active-tasks.md.bak`, `docs/tasks/completed-tasks.md.bak` | A copy of the ledger as it was, saved only when the merge drops rows that are not `T<NNN>` task rows. An earlier backup is never overwritten |
| `<tree>.emage-new.<pid>` and `<tree>.emage-old.<pid>`, for example `.claude.emage-new.4242` | Next to a platform tree or runtime directory, only on `--update` or `--projections-only` **on a host without `rsync`** | The replacement tree is built beside the old one and swapped in with two renames. An interrupt or failure removes them (the old tree is put back if it was moved). If one is still there, the installer refuses to run until you remove it |

With `rsync` installed, trees are synchronised in place and the two `emage` sibling names do not appear. Nothing the installer creates is group- or world-writable, whatever the source modes or your umask.

**Notes the installer prints.** Each is one line on standard error unless stated; none prints a secret value, only names.

| When | What it says (quoted in part) |
|------|-------------------------------|
| An existing MCP/settings config is not valid JSON, or it (or its directory) cannot be replaced | `merge-mcp-json: <file> is not valid JSON (...); nothing was written. Fix or remove the file and re-run.` or `... or its directory is not writable; nothing was written. Fix the permissions and re-run.` The run stops before anything is written |
| A rule or value of yours was replaced | `merge-mcp-json: note: <file>: replaced your value for permission.<key>, hooks...`: a Playwright `permission` rule of yours that the generated `deny` overrides, or a `hooks` value replaced by the generated one |
| A key of yours was kept inside a generator-owned server | `merge-mcp-json: note: <file>: kept your key mcpServers.<server>.env.<KEY>` (also `environment` and `headers`) |
| The top level of your config was not a JSON object | `... the top level of your file is not a JSON object, so the whole file was replaced by the generated config` |
| There is no provenance sidecar, so nothing could be pruned | `merge-mcp-json: note: <file>: there is no provenance sidecar at <path>, so no retired generator entry could be pruned; kept your server(s) <names>, which the generated config does not contain. If one is a retired generator entry, remove it by hand or run scripts/merge-mcp-json.py with --force-prune-keys <name>.` |
| `CLAUDE.md` exists and differs from the generated one (Claude Code) | `note: replacing the existing <target>/CLAUDE.md with the generated one; its previous content is not kept.` `CLAUDE.md` is generator-owned in every mode |
| A ledger row is not a `T<NNN>` row | `warning: dropping non-conforming task row (ID must match T<NNN>): <row>`, then on standard output `back up <ledger> to <ledger>.bak (N row(s) dropped)` |
| `--update` or `--projections-only` will replace a platform tree | `warning: --update replaces <target>/<dir> entirely (rsync --delete) ... Other local edits there will be lost.` |
| A swap sibling already exists (no `rsync`) | `error: <tree>.emage-new.<pid> or <tree>.emage-old.<pid> already exists; remove it and re-run. Nothing was written.` |
| The run ends and a selected platform ships the Playwright server | On standard output, a note with the browser install command and the `.playwright-mcp/` advice (full text and the matching section: [`implementation/PREREQUISITES.md`](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/PREREQUISITES.md#browser-for-the-playwright-server)). The installer neither installs the browser nor edits your `.gitignore` |

A full install or `--update` (not `--projections-only`) also prints the command that installs the Python dependency of the MCP servers and the command that builds the context-retriever index; the first is described in the README section on the PoC security scan server.

## 2. Manual copy (alternative)

| Platform | What to copy from `implementation/` |
|----------|-------------------------------------|
| GitHub Copilot | `.github/` + `.vscode/mcp.json` |
| Gemini CLI | `.gemini/` |
| Opencode | `.opencode/` |
| Pi | `.pi/` |
| Claude Code | `.claude/` + `.mcp.json` + `CLAUDE.md` |
| Cline | `.clinerules/` + `.cline/` (its MCP file is a staging file, not applied automatically: [Cline Setup](cline-setup)) |

Plus always: `AGENTS.md`, `docs/`, and the MCP server runtime source that `install.sh` copies without `--projections-only`: `implementation/runtime/memory/`, `implementation/runtime/security/` and `implementation/runtime/handoff/`, each to the same path in your project, plus an empty `implementation/__init__.py` (leave out any `_index/` and `__pycache__/` folders). The `context-retriever`, `security-audit` and `poc-security-audit` servers launch with `python3 -m implementation.runtime...` and `/handoff` reads `implementation/runtime/handoff/`, so they do not work without it.

## 3. Set MCP env vars

The generated `mcp.json` needs credentials for the MCP servers you want active:

```bash
export GITLAB_PERSONAL_ACCESS_TOKEN_FILE="$HOME/.config/gitlab-mcp/token"  # a path, not the token
export GITLAB_API_URL=...
export BRAVE_API_KEY=...
export HINDSIGHT_MCP_URL=...
```

The GitLab token goes in a file that only you can read, outside every project; you export its path. Exporting the token itself as `GITLAB_PERSONAL_ACCESS_TOKEN` still works, but a non-empty value wins over the file. Scope, role, file steps and checks: [`implementation/PREREQUISITES.md`, "GitLab token"](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/PREREQUISITES.md#gitlab-token).

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

- **Agents not loading?** Confirm format: `.agent.md` (Copilot), `.md` (Gemini/Opencode/Pi/Claude Code).
- **MCP failing?** Check env vars and network access.
- **Drift after editing knowledge?** Run `make sync` from repo root.
