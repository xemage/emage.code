# 01 — Shared knowledge architecture

## Topology

```
                 ┌──────────────────┐
                 │   knowledge/     │  ← single source of truth
                 │  (canonical MD)  │
                 └────────┬─────────┘
                          │
              ┌───────────┼───────────────────────────┐
              ▼           ▼           ▼               ▼
     platforms/        platforms/  platforms/   platforms/
     github.json       gemini.json opencode.json  cursor.json
              │           │           │               │
              ▼           ▼           ▼               ▼
   scripts/sync.mjs reads manifest + knowledge → emits each platform folder
              │           │           │               │
              ▼           ▼           ▼               ▼
        .github/      .gemini/    .opencode/      .cursor/   (committed)
```

## Knowledge taxonomy

| Folder | What | One file per |
|--------|------|--------------|
| `agents/` | Agent personality + role + tool grants | agent |
| `commands/` | Slash-command prompts (user entry points) | command |
| `instructions/` | Always-on or glob-scoped guidance | topic |
| `skills/<name>/SKILL.md` | Reusable capability — invokable from any agent | skill |
| `mcp/servers.yaml` | MCP server registry with `core` / `extended` tags | (single) |
| `schemas/*.schema.json` | JSON-schema validation for frontmatter | content type |

## Canonical frontmatter

| Type | Required keys | Optional keys |
|------|---------------|---------------|
| Agent | `name`, `description` | `tools` (array), `agents` (array) |
| Command | `description` | `agent`, `argument-hint` |
| Instruction | `description` | `applyTo` (glob) |
| Skill | `name`, `description` | — |

`tools` is **always** an array in `knowledge/`. Per-platform transforms convert to:
- Gemini → drop the field entirely
- Opencode → object form `{ tool: true }`
- GitHub / Cursor → keep array
Per-platform transforms also rename `applyTo` → `globs` for Cursor (`.mdc` rules).

## Projection invariants

For every projection `knowledge/X → platform/Y`:
1. **Body is byte-identical.** Only frontmatter and filename change.
2. **No content gets duplicated** in the platform folder; everything traces back to one canonical file.
3. **Generation is deterministic.** Same inputs ⇒ same outputs. The committed `.generated-manifest.json` in each platform folder lists every emitted file path so reviewers can see the surface area at a glance.

## What lives outside `knowledge/`

- `_extras/` — per-platform files that don't map to a canonical knowledge type (e.g. GitHub's `hooks/post-edit-reminder.json`).
- `.vscode/settings.json` — editor-only, not generated, but documented in `SECURITY.md`.
- `docs/` — runtime workspace state (per-project task lists, plans, ADRs, …). Templates are versioned; instances are not.

## Adding a platform

1. Create `platforms/<name>.json` (start by copying `cursor.json`).
2. Choose extensions (`fileMap.<type>.ext`) and folder layout (`fileMap.<type>.dir`).
3. Declare `frontmatter` transforms (`tools`, `keepKeys`, `renameKeys`).
4. Declare `mcp` profile (`tags`, `outputFile`, `format`).
5. Optional `extras` for non-knowledge files.
6. `node scripts/sync.mjs --platform=<name>`.
7. Smoke-test by copying the generated folder into a test project and running `/new-feature` with the target tool.

No edits to `sync.mjs` are required for new platforms whose MCP config matches one of the four supported `format` values (`vscode`, `gemini`, `opencode`, `cursor`). Genuinely new MCP shapes require adding a new branch to `emitMcp()`.
