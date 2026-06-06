# emage.code v3 implementation

v3 is the **current release stream** — schema-first canonical knowledge,
managed cookbooks, triggers, packaging, and validation super-gates.

Latest release: v3.0.1

## Install

Copy the platform folder for your assistant plus shared workspace files:

```bash
# GitHub Copilot
cp -r v3/implementation/.github         <your-project>/
mkdir -p <your-project>/.vscode
cp    v3/implementation/.vscode/mcp.json <your-project>/.vscode/

# Gemini CLI
cp -r v3/implementation/.gemini         <your-project>/

# Opencode
cp -r v3/implementation/.opencode       <your-project>/

# Cursor
cp -r v3/implementation/.cursor         <your-project>/

# Pi (https://pi.dev)
cp -r v3/implementation/.pi             <your-project>/.pi/

# Always include
cp    v3/implementation/AGENTS.md       <your-project>/
cp -r v3/implementation/docs            <your-project>/
```

Set MCP env vars from the generated config, then run `/new-project "Your idea"`.

Per-release install notes: [`docs/releases/v3.0.1.md`](../../docs/releases/v3.0.1.md).

## Validation commands

Run from repository root:

```bash
python3 v3/implementation/scripts/check-v3.py --root v3/implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
```

Projection drift checks:

```bash
node v3/implementation/scripts/verify-v3.mjs --root v3/implementation
```

Migration compatibility check (optional):

```bash
node v3/implementation/scripts/verify-v3.mjs --root v2/implementation
```

## Instant use (v2-style)

v3 now ships the same drop-in surface as v2:

- canonical source: `knowledge/`, `platforms/`, `_extras/`
- generated outputs: `.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`, `.vscode/mcp.json`
- workspace conventions: `AGENTS.md`, `PREREQUISITES.md`, `SECURITY.md`, `docs/`

Copy for immediate use (GitHub Copilot example):

```bash
cp -r v3/implementation/.github         <your-project>/
mkdir -p <your-project>/.vscode
cp    v3/implementation/.vscode/mcp.json <your-project>/.vscode/
cp    v3/implementation/AGENTS.md       <your-project>/
cp -r v3/implementation/docs            <your-project>/
```

## CI integration

Recommended CI stage order:

1. `python3 v3/implementation/scripts/check-v3.py --root v3/implementation --required --schemas --cookbooks`
2. `python3 v3/implementation/scripts/check-v3.py --root v3/implementation --handoff-security`
3. `python3 v3/implementation/scripts/check-v3.py --root v3/implementation --hook-policy`
4. `python3 v3/implementation/scripts/check-v3.py --root v3/implementation --telemetry`
5. `python3 v3/implementation/scripts/check-v3.py --root v3/implementation --benchmarks`
6. `python3 v3/implementation/scripts/check-v3.py --root v3/implementation --registry`
7. `python3 v3/implementation/scripts/check-v3.py --root v3/implementation --packaging`
8. `python3 v3/implementation/scripts/check-v3.py --root v3/implementation --triggers`
9. `python3 v3/implementation/scripts/check-v3.py --root v3/implementation --adapters`
10. `node v3/implementation/scripts/verify-v3.mjs --root v3/implementation`
11. v3 functional tests:
   `python3 -m unittest tests.functional.test_v3_validation_gate -v`

## Package workflow

Install from local path:

```bash
python3 v3/implementation/scripts/package-v3.py install --root v3/implementation --source tests/fixtures/packs/sample-pack
```

Update by pack id:

```bash
python3 v3/implementation/scripts/package-v3.py update --root v3/implementation --pack-id sample-core-pack
```

Uninstall:

```bash
python3 v3/implementation/scripts/package-v3.py uninstall --root v3/implementation --pack-id sample-core-pack
```

List installed packs:

```bash
python3 v3/implementation/scripts/package-v3.py list --root v3/implementation
```

## Trigger workflow

Run a schedule or event trigger with policy guardrails and audit logging:

```bash
python3 v3/implementation/runtime/triggers/runner.py \
  --trigger v3/implementation/triggers/examples/schedule-daily.json \
  --policy v3/implementation/triggers/examples/policy-default.json \
  --queue /tmp/v3-trigger-queue.json \
  --audit-log /tmp/v3-trigger-audit.log
```

Simulate retry flow for testing:

```bash
python3 v3/implementation/runtime/triggers/runner.py \
  --trigger v3/implementation/triggers/examples/event-webhook.json \
  --policy v3/implementation/triggers/examples/policy-default.json \
  --queue /tmp/v3-trigger-queue.json \
  --audit-log /tmp/v3-trigger-audit.log \
  --simulate-failures 1
```

## Adapter smoke workflow

Antigravity prototype:

```bash
V3_EXPERIMENTAL_ADAPTERS=1 V3_ADAPTER_ANTIGRAVITY=1 \
python3 v3/implementation/adapters/smoke.py \
  --adapter antigravity \
  --input tests/fixtures/adapters/sample-input.json
```

Opencode prototype:

```bash
V3_EXPERIMENTAL_ADAPTERS=1 V3_ADAPTER_OPENCODE=1 \
python3 v3/implementation/adapters/smoke.py \
  --adapter opencode \
  --input tests/fixtures/adapters/sample-input.json
```

The gate must fail on unresolved references, missing required files, malformed
cookbook manifests, and projection drift.
