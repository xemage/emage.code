# Implementation Guide

emage.code uses an `implementation/` tree at the repository root. It provides
schema-first canonical knowledge, managed cookbooks, trigger workflows, packaging,
and validation super-gates (current release: v8.0.0).

## What to use it for

- cookbook-driven orchestration definitions
- trigger-based execution with policy guardrails
- package install / update / uninstall workflows
- adapter smoke testing and compatibility checks
- mandatory workflow skills (`/discover-skills`, `/handoff`, safety guards)

## Install

**Recommended:** use the installer from the repo root:

```bash
git clone https://gitlab.com/em-age/emage.code.git
cd emage.code
scripts/install.sh --target <your-project> --platform claude-code
```

Update an existing project:

```bash
scripts/install.sh --target <your-project> --platform claude-code --update
```

`--update` replaces the platform trees but spares the client-owned files `.claude/settings.json`, `.claude/settings.local.json` and, under `.github/`, `workflows/`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE`, `CODEOWNERS`, `dependabot.yml`, `dependabot.yaml`, `FUNDING.yml` and `copilot-instructions.md`; each platform's MCP/settings config is merged (a plain install over an existing config merges it too). The task ledgers in `docs/tasks/` keep their `T<NNN>` rows and the prose around the table; other table rows are dropped with a warning, after a copy of the ledger is saved as `<ledger>.bak`. The files the installer can leave next to yours and the notes it prints are listed in [Quick Start](quick-start#files-and-notes-the-installer-produces).

Refresh only the harness projections, leaving `docs/` and `implementation/` untouched (mutually exclusive with `--update`):

```bash
scripts/install.sh --target <your-project> --platform claude-code --projections-only
```

The PoC security scan runs on the `poc-security-audit` MCP server, which needs `mcp` (Python), `git` 2.40 or newer and, on Claude Code, an allow rule you add to your own `.claude/settings.json`: see [MCP Servers](mcp-servers#poc-security-scan-server-poc-security-audit).

Or see [Quick Start](quick-start) and [`docs/releases/v8.0.0.md`](https://gitlab.com/em-age/emage.code/-/blob/main/docs/releases/v8.0.0.md).

Supported projections: GitHub Copilot, Gemini CLI, Opencode, Pi, Claude Code, Cline.

## Validate (maintainers)

From the repository root:

```bash
python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --maturity --packaging --triggers --adapters
node implementation/scripts/verify.mjs --root implementation
```

## Main entry points

- [Implementation README](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/README.md)
- [Agents Overview](agents-overview)
- [Quick Start](quick-start)

## Notes

- Edit canonical files under `implementation/knowledge/` only; run `make sync`.
