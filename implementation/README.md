# emage.code implementation

Canonical knowledge and platform projections for the current release stream
(**v8.0.0**).

Latest release: v8.0.0

## Install

**Recommended** — from the repository root:

```bash
scripts/install.sh --target <your-project> --platform claude-code
# or: make install TARGET=<your-project> PLATFORM=claude-code
```

**Update** an existing install (requires `AGENTS.md` in the target):

```bash
scripts/install.sh --target <your-project> --platform claude-code --update
```

`--update` replaces the platform trees but spares the client-owned files
`.claude/settings.json`, `.claude/settings.local.json` and, under `.github/`,
`workflows/`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`,
`PULL_REQUEST_TEMPLATE`, `CODEOWNERS`, `dependabot.yml`, `dependabot.yaml`,
`FUNDING.yml` and `copilot-instructions.md`; each platform's MCP/settings config
is merged.

**Refresh only the harness projections** (platform trees, MCP configs,
`AGENTS.md`, and `CLAUDE.md` for Claude Code), leaving `docs/` and
`implementation/` untouched. Mutually exclusive with `--update`; needs an
existing install:

```bash
scripts/install.sh --target <your-project> --platform claude-code --projections-only
```

**PoC security scan server.** `implementation/runtime/security/` is installed
with the harness (not by `--projections-only`) and backs the
`poc-security-audit` MCP server. It needs the Python package `mcp`
(`implementation/runtime/security/requirements-mcp-server.txt`), `git` 2.40 or
newer, a launch from the project root and, on Claude Code, the allow rule
`mcp__poc-security-audit__*` in your own `.claude/settings.json`, which the
installer never writes. Details:
[MCP Servers](../docs/wiki/mcp-servers.md#poc-security-scan-server-poc-security-audit).

**Manual copy** — platform folder plus shared files:

```bash
cp -r implementation/.claude         <your-project>/.claude/   # example: Claude Code
cp    implementation/AGENTS.md         <your-project>/
cp -r implementation/docs            <your-project>/docs/
# MCP server runtime source (the installer skips it only under --projections-only);
# leave out any _index/ and __pycache__/ folders
mkdir -p <your-project>/implementation/runtime && touch <your-project>/implementation/__init__.py
cp -r implementation/runtime/memory   implementation/runtime/security \
      implementation/runtime/handoff  <your-project>/implementation/runtime/
```

Per-release notes: [`docs/releases/v8.0.0.md`](../docs/releases/v8.0.0.md).

## Validation commands

From repository root:

```bash
python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --maturity --packaging --triggers --adapters
node implementation/scripts/verify.mjs --root implementation
```

Or: `make verify` and `make sync`. Thin wrappers: `scripts/sync.sh`, `scripts/verify.sh`, `scripts/sync.ps1`.

## Authoring

| Path | Purpose |
|------|---------|
| `knowledge/` | Canonical agents, commands, skills, instructions, MCP registry |
| `platforms/` | Per-platform manifest JSON |
| `cookbooks/`, `triggers/`, `runtime/` | Schema-first workflows |
| `.github/`, `.claude/`, … | **Generated** — run `make sync` after editing `knowledge/` |

## Package workflow

```bash
python3 implementation/scripts/package.py --help
```

Slash commands: `/package-install`, `/package-update`, `/package-uninstall` (after install).

## Trigger workflow

Examples under `triggers/examples/`. Validated by `check.py --triggers`.

## Adapter smoke workflow

```bash
python3 implementation/scripts/check.py --root implementation --adapters
```
