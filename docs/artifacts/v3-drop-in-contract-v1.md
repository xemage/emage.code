# v3 Drop-In Contract v1

## Objective
Define the minimum release contract for `implementation` to be instantly usable with the same bootstrap and operational model as `v2/implementation`.

## Required implementation surface

### Top-level files
- `AGENTS.md`
- `PREREQUISITES.md`
- `SECURITY.md`
- `.gitignore`
- `README.md`

### Canonical source tree
- `knowledge/`
- `platforms/`
- `_extras/`

### Generated platform outputs
- `.github/`
- `.gemini/`
- `.opencode/`
- `.cursor/`
- `.vscode/mcp.json`

### Runtime workspace scaffolding
- `docs/artifacts/_template.md`
- `docs/checkpoints/_template.md`
- `docs/decisions/_template.md`
- `docs/plans/_template.md`
- `docs/tasks/active-tasks.md`
- `docs/tasks/completed-tasks.md`

### Sync and drift toolchain
- `scripts/sync-v3.mjs`
- `scripts/verify-v3.mjs`
- `scripts/sync.sh`
- `scripts/sync.ps1`

## Determinism and portability requirements
- Drift checks must be stable across Linux and Windows runners.
- Generated manifest paths must use POSIX separators.
- Text comparison in check mode must tolerate CRLF/LF line-ending differences.

## CI release-readiness requirements
- Run full v3 super-gate:
  - `python3 implementation/scripts/check-v3.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters`
- Run v3 drift gate:
  - `node implementation/scripts/verify-v3.mjs --root implementation`
- Run v3 sync no-diff gate:
  - `node implementation/scripts/sync-v3.mjs --root implementation`
  - fail if `git diff --quiet` is false afterward.

## Release candidate checklist
- `implementation` contains all required contract files and directories.
- Generated platform outputs are present and committed.
- Local validation commands pass.
- Branch and MR pipelines are green.
- Release docs and wiki references point to v3-native commands.
