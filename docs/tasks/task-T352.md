# Task T352 — Create Cline Platform Manifest

**ID:** T352
**Owner:** backend-developer
**Status:** pending
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-08
**Based on:** `docs/plans/plan-028-cline-platform-integration.md` §0, §2; `implementation/platforms/cursor.json`,
`implementation/platforms/pi.json`, `implementation/platforms/claude-code.json` (shape references)

## Objective
Author `implementation/platforms/cline.json`, the manifest that tells `implementation/scripts/sync.mjs`
how to project canonical knowledge into Cline's native on-disk format. This is a pure JSON-authoring
task — no `sync.mjs` changes (that's T353).

## Context
- Phase: Implementation (plan-028, step 1 of 6).
- This repo already supports 6 platforms via manifests in `implementation/platforms/*.json`:
  `cursor`, `github`, `gemini`, `opencode`, `pi`, `claude-code`. Read `cursor.json` and `pi.json` in
  full before starting — they are the closest shape references.
- **Step 0, before writing anything**: fetch https://docs.cline.bot (the rules/custom-instructions
  and MCP-configuration pages) and confirm the assumed Cline config format below is still current:
  - `.cline/rules/*.md` — conditional rules, YAML frontmatter, replacing a legacy single-file
    `.clinerules`
  - `.cline/skills/*/SKILL.md`
  - `.cline/agents/*.md`
  - `cline_mcp_settings.json` — MCP server config
  If the live docs describe a **materially different** format (different directory names, different
  frontmatter keys, a different MCP config filename/shape), **stop and report an
  `unclear_requirements` blocker** per the Blocker Protocol below — do not silently adapt the manifest
  to a guess. If the format matches (even with minor wording differences), proceed.

## Inputs
- `implementation/platforms/cursor.json`, `implementation/platforms/pi.json`,
  `implementation/platforms/claude-code.json` — read all three for shape reference before writing.
- `implementation/knowledge/mcp/servers.yaml` — the MCP server registry this manifest's `mcp` block
  projects. Do not add new servers or new tags to this file; T352 only references the existing
  `core`/`extended` tags.

## Constraints
- **Do not create `implementation/platforms/_manifest.schema.json`.** It does not exist for *any*
  platform in this repo today (every existing manifest's `"$schema"` field points at a file that
  isn't there — a pre-existing, harmless, repo-wide convention). Keep the same `"$schema":
  "./_manifest.schema.json"` field in `cline.json` for consistency with the other 6 manifests, but do
  not attempt to make it resolve to a real file — that is out of scope for this task.
- **Do not modify `implementation/scripts/sync.mjs`, `scripts/install.sh`, or any docs file.** Those
  are T353/T355/T356.
- **Do not add anything RAG/vault/Obsidian-related** to the `mcp` block or anywhere else in the file.
- File must be valid JSON and must not introduce any manifest key that doesn't already appear in at
  least one of `cursor.json`, `pi.json`, or `claude-code.json` — if Cline genuinely needs a new key
  shape (e.g. `toolMap`, which is new but is a sub-key of the existing `frontmatter.agents` block, not
  a new top-level manifest key), that is fine; inventing an unrelated new top-level manifest concept
  is not — flag it as a blocker instead.
- Token budget: ≤ 20k.

## Expected Outputs
`implementation/platforms/cline.json`, with exactly this content (adjust only if Step 0's live-docs
check surfaces a material difference, in which case report the blocker instead of silently adjusting):

```json
{
  "$schema": "./_manifest.schema.json",
  "platform": "cline",
  "displayName": "Cline",
  "outputDir": ".cline",
  "fileMap": {
    "agents": { "dir": "agents", "ext": ".md" },
    "commands": { "dir": "commands", "ext": ".md" },
    "instructions": { "dir": "rules", "ext": ".md" },
    "skills": { "dir": "skills", "preserveTree": true }
  },
  "frontmatter": {
    "agents": {
      "tools": "string",
      "keepKeys": ["name", "description", "tools"],
      "toolMap": {
        "read": "read_file",
        "search": "search_files",
        "edit": "apply_diff",
        "execute": "execute_command",
        "agent": "use_subagent",
        "web": "browser_action",
        "todo": "use_skill"
      }
    },
    "commands": {
      "keepKeys": ["description", "argument-hint"]
    },
    "instructions": {
      "renameKeys": { "applyTo": "globs" },
      "keepKeys": ["description", "globs", "alwaysApply"]
    },
    "skills": {
      "keepKeys": ["name", "description"]
    }
  },
  "mcp": {
    "tags": ["core", "extended"],
    "outputFile": "cline_mcp_settings.json",
    "format": "cline"
  },
  "extras": [
    { "from": "_extras/cline/dot-clinerules", "to": "../.clinerules" }
  ]
}
```

Note: the `mcp.format` value `"cline"` does not exist yet in `sync.mjs`'s `emitMcp()` — that's
expected, T353 adds it. T352 only needs the manifest to declare it.

## Acceptance Criteria
- [ ] Step 0 live-docs check performed and recorded in this brief's Outcome section (what was
      checked, what was found, confirmed-current or blocker-reported)
- [ ] `implementation/platforms/cline.json` exists and is valid JSON:
      `python3 -m json.tool < implementation/platforms/cline.json` exits 0
- [ ] `platform` is `"cline"`, `displayName` is `"Cline"`, `outputDir` is `".cline"`
- [ ] `fileMap` matches the block above exactly (4 entries: agents/commands/instructions/skills)
- [ ] `frontmatter.instructions.renameKeys` is `{"applyTo": "globs"}` and `keepKeys` includes
      `alwaysApply` (this is what T353 will gate its default-injection logic on — must be present)
- [ ] `frontmatter.agents.tools` is the string `"string"` (not `"array"` or `"object"`) and
      `toolMap` matches the 7-entry block above exactly
- [ ] `mcp` block matches exactly: `tags: ["core", "extended"]`, `outputFile:
      "cline_mcp_settings.json"`, `format: "cline"`
- [ ] `extras` has exactly one entry: `{"from": "_extras/cline/dot-clinerules", "to":
      "../.clinerules"}`
- [ ] No other file in the repo modified
- [ ] Task brief updated with an `## Outcome` section

## Blocker Protocol
Report blockers per `AGENTS.md`: type (`technical` | `dependency` | `unclear_requirements` |
`external`) + severity (`critical` | `major` | `minor`). Max 2 retries before escalation. A material
mismatch between this brief's assumed Cline format and the live docs at https://docs.cline.bot is an
`unclear_requirements` blocker — report it with the specific discrepancy found; do not adapt the
manifest to a guess and proceed silently.
