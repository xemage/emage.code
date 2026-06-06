# emage.code implementation

Version-independent canonical knowledge and platform projections for the
current release stream (**v4.0.0**).

Latest release: v5.0.0

## Install

**Recommended** — from the repository root:

```bash
scripts/install.sh --target <your-project> --platform cursor
# or: make install TARGET=<your-project> PLATFORM=cursor
```

**Manual copy** — platform folder plus shared files:

```bash
cp -r implementation/.cursor         <your-project>/.cursor/   # example: Cursor
cp    implementation/AGENTS.md         <your-project>/
cp -r implementation/docs            <your-project>/docs/
```

Per-release notes: [`docs/releases/v4.0.0.md`](../docs/releases/v4.0.0.md).

## Validation commands

From repository root:

```bash
python3 implementation/scripts/check-v3.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
node implementation/scripts/verify-v3.mjs --root implementation
```

Or: `make verify` and `make sync`.

## Authoring

| Path | Purpose |
|------|---------|
| `knowledge/` | Canonical agents, commands, skills, instructions, MCP registry |
| `platforms/` | Per-platform manifest JSON |
| `cookbooks/`, `triggers/`, `runtime/` | Schema-first workflows |
| `.cursor/`, `.github/`, … | **Generated** — run `make sync` after editing `knowledge/` |

Previous releases: [`archive/`](../archive/README.md).

## Package workflow

```bash
python3 implementation/scripts/package-v3.py --help
```

Slash commands: `/package-install`, `/package-update`, `/package-uninstall` (after install).

## Trigger workflow

Examples under `triggers/examples/`. Validated by `check-v3.py --triggers`.

## Adapter smoke workflow

```bash
python3 implementation/scripts/check-v3.py --root implementation --adapters
```
