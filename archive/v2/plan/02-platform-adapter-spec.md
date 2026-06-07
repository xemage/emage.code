# 02 — Platform adapter spec

## Manifest schema

Each `platforms/<name>.json` declares one platform:

```jsonc
{
  "platform": "<id>",                 // unique slug, used by --platform=
  "displayName": "<Pretty name>",
  "outputDir": ".<id>",                // relative to v2/implementation/

  "fileMap": {
    "agents":       { "dir": "<sub>", "ext": "<.ext>" },
    "commands":     { "dir": "<sub>", "ext": "<.ext>" },
    "instructions": { "dir": "<sub>", "ext": "<.ext>" },
    "skills":       { "dir": "<sub>", "preserveTree": true }
  },

  "frontmatter": {
    "agents": {
      "tools": "array" | "object" | "drop",  // how to emit `tools`
      "keepKeys": ["name", "description", "tools", "agents"],
      "addToOrchestrators": { "user-invocable": true }, // optional
      "orchestratorNames": ["orchestrator", "poc-orchestrator"]
    },
    "commands":     { "keepKeys": [...] },
    "instructions": { "renameKeys": { "applyTo": "globs" }, "keepKeys": [...] },
    "skills":       { "keepKeys": ["name", "description"] }
  },

  "mcp": {
    "tags": ["core", "extended"],     // which `servers.yaml` entries to emit
    "outputFile": "<path>",            // relative to outputDir (or "../.vscode/mcp.json")
    "format": "vscode"|"gemini"|"opencode"|"cursor",
    "extraFields": { ... }             // merged into the emitted file (Opencode only currently)
  },

  "extras": [
    { "from": "_extras/<path>", "to": "<path-inside-outputDir>" }
  ]
}
```

## Frontmatter transforms

| Knob | Effect |
|------|--------|
| `tools: "array"` | Emit canonical array form: `tools: [a, b, c]` |
| `tools: "object"` | Emit object form: `tools:\n  a: true\n  b: true` |
| `tools: "drop"` | Omit `tools` (Gemini) |
| `keepKeys` | Whitelist; unknown keys in source are dropped from output |
| `renameKeys` | Map `{ src: dst }` applied before `keepKeys` |
| `addToOrchestrators` | Merge object into output frontmatter when agent name ∈ `orchestratorNames` |

## MCP `format` reference

| Format | Outer shape | Server entry shape |
|--------|------------|--------------------|
| `vscode` | `{ "servers": { ... } }` | `{ command, args, env }` for stdio; `{ url }` for remote |
| `cursor` | `{ "mcpServers": { ... } }` | same as vscode |
| `gemini` | `{ "hooks": {...}, "mcpServers": { ... } }` | same as vscode |
| `opencode` | `{ "$schema": "...", "instructions": [...], "mcp": { ... } }` | `{ "type": "local"\|"remote", "command": [...], "environment": {...} }` or `{ "type": "remote", "url": "..." }` |

Env-var placeholders use `${env:VAR}` for vscode/cursor/gemini and `{env:VAR}` for opencode — emitted automatically based on `format`.

## Skills

Skills are special: they preserve the source folder tree (`preserveTree: true`). Every `SKILL.md` inside `knowledge/skills/` is rewritten with the platform's frontmatter rules; non-`SKILL.md` files (assets, examples) are copied verbatim.

## Validation

Each manifest is validated against `_manifest.schema.json` (TODO — not strictly enforced today; manifests are short enough that errors surface immediately during sync).
