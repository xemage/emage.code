# Task T287 — Create `implementation/platforms/claude-code.json` manifest

**ID:** T287
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T285, T286
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T287;
`implementation/platforms/cursor.json`, `implementation/platforms/opencode.json`
as structural templates.

## Why this task exists
Adding a platform to emage.code is manifest-driven: a new
`implementation/platforms/<name>.json` file, following the same JSON schema as
the 5 existing manifests, is the ONLY declarative input the sync engine needs
(after T285/T286 added the two missing engine features this platform requires).

## STOP-RULES (read before touching anything)
- **R2** This task creates **EXACTLY ONE NEW FILE**:
  `implementation/platforms/claude-code.json`. Do not edit any other file.
- Do **NOT** run `make sync` or `install.sh` in this task (that is T288).
- Confirm T285 and T286 are `done` before starting. If either is `pending`,
  STOP and report `PRECONDITION FAILED: T287 (missing dependency)`.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `feat(platforms): T287 add claude-code manifest`

## Objective
Create `implementation/platforms/claude-code.json` with this exact content:

```json
{
  "$schema": "./_manifest.schema.json",
  "platform": "claude-code",
  "displayName": "Claude Code",
  "outputDir": ".claude",
  "fileMap": {
    "agents":       { "dir": "agents",       "ext": ".md" },
    "commands":     { "dir": "commands",     "ext": ".md" },
    "instructions": { "dir": "rules",        "ext": ".md" },
    "skills":       { "dir": "skills",       "preserveTree": true }
  },
  "frontmatter": {
    "agents": {
      "tools": "string",
      "keepKeys": ["name", "description", "tools"]
    },
    "commands": {
      "keepKeys": ["description", "argument-hint"]
    },
    "instructions": {
      "renameKeys": { "applyTo": "paths" },
      "keepKeys": ["description", "paths"]
    },
    "skills": {
      "keepKeys": ["name", "description"]
    }
  },
  "mcp": {
    "tags": ["core", "extended"],
    "outputFile": "../.mcp.json",
    "format": "claude-code"
  }
}
```

> Note on `outputFile: "../.mcp.json"`: the sync engine resolves
> `manifest.mcp.outputFile` relative to `outRoot` (`implementation/.claude`),
> and Claude Code expects `.mcp.json` at the **repository/project root**, not
> inside `.claude/`. `../.mcp.json` relative to `implementation/.claude`
> resolves to `implementation/.mcp.json` — i.e. sitting alongside `.claude/`
> at the `implementation/` root, matching how the `github` manifest points its
> `mcp.outputFile` at `"../.vscode/mcp.json"` (sitting alongside `.github/`).
> Verify this by re-reading `implementation/platforms/github.json` if unsure.

> Note on omitting `orchestratorNames`/`addToOrchestrators`/`user-invocable`:
> Claude Code has no first-class "primary/user-invocable agent" distinction in
> its subagent frontmatter contract (confirmed against official docs,
> 2026-07-30). All subagent files use the same shape (`name`, `description`,
> `tools`). Do NOT add `addToOrchestrators` or `orchestratorNames` keys — they
> are intentionally omitted from this manifest, unlike `github.json`/`opencode.json`.

## Expected outputs
- `implementation/platforms/claude-code.json` created with the exact content above.

## Acceptance criteria
1. Verify command — file exists and is valid JSON:
   ```bash
   python3 -c "import json; json.load(open('implementation/platforms/claude-code.json'))" && echo VALID_JSON
   ```
   Expected output: `VALID_JSON`
2. Verify command:
   ```bash
   grep -Fc '"platform": "claude-code"' implementation/platforms/claude-code.json
   grep -Fc '"outputDir": ".claude"' implementation/platforms/claude-code.json
   grep -Fc '"tools": "string"' implementation/platforms/claude-code.json
   grep -Fc '"format": "claude-code"' implementation/platforms/claude-code.json
   grep -Fc '"outputFile": "../.mcp.json"' implementation/platforms/claude-code.json
   ```
   Expected output: `1` for each of the 5 commands.
3. Verify command — required top-level keys present (mirrors
   `test_manifests.py::test_manifests_parse_and_have_required_keys`):
   ```bash
   python3 -c "
   import json
   d = json.load(open('implementation/platforms/claude-code.json'))
   required = {'platform', 'displayName', 'outputDir', 'fileMap', 'frontmatter'}
   missing = required - set(d)
   assert not missing, f'missing keys: {missing}'
   assert not d['outputDir'].startswith('/') and not d['outputDir'].startswith('..')
   print('SCHEMA_OK')
   "
   ```
   Expected output: `SCHEMA_OK`
4. `git status --porcelain` lists exactly one new file:
   `implementation/platforms/claude-code.json`.

## Revert rule
If any verify command fails:
```bash
rm -f implementation/platforms/claude-code.json
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
