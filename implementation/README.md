# emage.code implementation

Canonical knowledge and platform projections for the current release stream
(**v6.0.2**).

Latest release: v6.0.2

## Install

**Recommended** — from the repository root:

```bash
scripts/install.sh --target <your-project> --platform cursor
# or: make install TARGET=<your-project> PLATFORM=cursor
```

**Update** an existing install (requires `AGENTS.md` in the target):

```bash
scripts/install.sh --target <your-project> --platform cursor --update
```

**Manual copy** — platform folder plus shared files:

```bash
cp -r implementation/.cursor         <your-project>/.cursor/   # example: Cursor
cp    implementation/AGENTS.md         <your-project>/
cp -r implementation/docs            <your-project>/docs/
```

Per-release notes: [`docs/releases/v6.0.2.md`](../docs/releases/v6.0.2.md).

## Validation commands

From repository root:

```bash
python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
node implementation/scripts/verify.mjs --root implementation
```

Or: `make verify` and `make sync`. Thin wrappers: `scripts/sync.sh`, `scripts/verify.sh`, `scripts/sync.ps1`.

## Authoring

| Path | Purpose |
|------|---------|
| `knowledge/` | Canonical agents, commands, skills, instructions, MCP registry |
| `platforms/` | Per-platform manifest JSON |
| `cookbooks/`, `triggers/`, `runtime/` | Schema-first workflows |
| `.cursor/`, `.github/`, … | **Generated** — run `make sync` after editing `knowledge/` |

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
