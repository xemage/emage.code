# 04 — sync.mjs design

## Goals

- Zero external dependencies (Node stdlib only).
- Deterministic — same inputs ⇒ byte-identical outputs.
- One-pass: read manifests, walk knowledge, emit per-platform.
- Cross-platform (Windows / macOS / Linux) — no shell-isms.
- Drift verification mode for CI.

## Pipeline

```
parseArgs → readServersYaml → for each manifest: syncPlatform()
                                  ├─ wipe outputDir (write mode only)
                                  ├─ project agents
                                  ├─ project commands
                                  ├─ project instructions
                                  ├─ project skills (preserveTree)
                                  ├─ emit MCP config
                                  ├─ copy extras
                                  └─ write .generated-manifest.json
```

## Frontmatter parser (subset)

emage.code's frontmatter only uses:
- scalar strings (quoted or unquoted)
- inline arrays `[a, b, c]`
- nested object blocks (e.g. Opencode's `tools:` with indented `key: bool`)

The parser handles these and refuses to attempt full YAML. This keeps the script <500 lines and audit-able. If knowledge files ever need richer YAML, swap to `js-yaml` (single dep).

## Frontmatter emitter

- Strings are quoted with double quotes; complex strings use `JSON.stringify` to escape.
- Arrays are inline: `key: [a, b, c]`.
- Nested object form (`tools:` for Opencode) emits one indented `key: true` per entry.

## MCP emitter

A switch on `manifest.mcp.format` picks an emitter:

| Format | Outer key | Env-var template |
|--------|-----------|------------------|
| `vscode` | `servers` | `${env:VAR}` |
| `cursor` | `mcpServers` | `${env:VAR}` |
| `gemini` | `mcpServers` (+ `hooks`) | `${env:VAR}` |
| `opencode` | `mcp` (+ `$schema`, `instructions`) | `{env:VAR}` |

Adding a fifth format ⇒ one new branch in `emitMcp()`.

## Drift detection (`--check`)

In check mode the script generates content in memory and compares with the file already on disk (binary-safe `Buffer.equals`). Any mismatch is collected; non-empty list ⇒ exit 1. The `verify.mjs` shim exists to give CI a stable command.

## Determinism guards

- File walking sorts `readdir` results implicitly via stable `for…of` after we accumulate (we sort the manifest's `files` list before serializing).
- The `.generated-manifest.json` deliberately uses a placeholder `<deterministic>` for `generatedAt` — if we wrote a real timestamp, every sync would drift in CI.
- JSON output uses `JSON.stringify(obj, null, 2) + '\n'` for stable trailing newline.

## Failure modes & remedies

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `verify` flags drift right after `sync` | non-deterministic content (timestamp, random) | inspect the diff; remove the source of nondeterminism |
| Frontmatter key dropped from output | not in `keepKeys` for that platform | add to `keepKeys` in the platform manifest |
| MCP server missing from a platform | tag mismatch | add tag to either `servers.yaml` entry or platform `mcp.tags` |
| Nested object frontmatter parsed weirdly | exceeds parser subset | extend `parseYamlBlock` or switch to `js-yaml` |

## Future work

- `--platform=<name>` for partial syncs (already implemented; document in README usage).
- `knowledge:lint` script that schema-validates frontmatter against `knowledge/schemas/*.json`.
- Plugin hook for platform-specific post-processors (e.g., to compile a single `AGENTS.md` per platform).
