# Task T288 — Run `make sync`; verify `implementation/.claude` is generated correctly

**ID:** T288
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T287
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T288

## Why this task exists
The manifest from T287 is inert until the sync engine runs and materializes
`implementation/.claude/**` and `implementation/.mcp.json`. This task runs the
generator and asserts the output is structurally correct before any downstream
task (installer, tests, docs) depends on it.

## STOP-RULES (read before touching anything)
- Confirm T287 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T288 (missing dependency)`.
- This task only **runs commands and commits generated output** — do not
  hand-edit any file under `implementation/.claude/` or `implementation/.mcp.json`.
  If output looks wrong, the fix belongs in `implementation/platforms/claude-code.json`
  (T287) or `implementation/scripts/sync.mjs` (T285/T286) — STOP and report as a
  blocker referencing which upstream task needs rework. Do NOT patch generated
  files directly.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `chore(sync): T288 generate implementation/.claude projection`

## Objective
Run the sync engine for all platforms (regenerating everything, since the
sync engine deletes and rewrites each platform's output directory), confirm no
drift in the 5 pre-existing platforms, and confirm the new `claude-code`
platform materializes with the expected file set.

## Steps

1. Run the generator (from repo root):
   ```bash
   node implementation/scripts/sync.mjs --root implementation
   ```
   Expected: line `[claude-code] wrote N files -> .claude` appears in output,
   alongside similar lines for `cursor`, `github`, `gemini`, `opencode`, `pi`.
   Exit code `0`.

2. Confirm the output directory exists and has the expected top-level shape:
   ```bash
   ls implementation/.claude
   ```
   Expected: contains `agents`, `commands`, `rules`, `skills`,
   `.generated-manifest.json` (no `mcp.json` inside `.claude/` — it lives one
   level up, see step 3).

3. Confirm the MCP file landed at `implementation/.mcp.json` (NOT inside
   `.claude/`):
   ```bash
   test -f implementation/.mcp.json && echo MCP_FILE_OK
   test ! -f implementation/.claude/mcp.json && echo NO_NESTED_MCP_OK
   ```
   Expected output: `MCP_FILE_OK` then `NO_NESTED_MCP_OK`.

4. Spot-check one agent file for the `tools: a, b, c` string shape:
   ```bash
   head -6 implementation/.claude/agents/backend-developer.md
   ```
   Expected: a line matching `tools: read, search, edit, execute, web, mcp__fetch`
   (comma-space separated, no brackets, no quotes).

5. Spot-check one instruction file for the `paths:` rename (mirrors Cursor's
   `applyTo` → `globs` rename, but to `paths` for Claude Code):
   ```bash
   head -4 implementation/.claude/rules/coding-standards.md
   ```
   Expected: a line matching `paths: [**/*.{ts,js,py,java,cs,go,rs,rb,php,swift,kt}]`
   (or equivalent array syntax) — NOT `applyTo:`.

6. Spot-check the MCP file for the remote-server `type: http` shape:
   ```bash
   python3 -c "
   import json
   d = json.load(open('implementation/.mcp.json'))
   assert 'mcpServers' in d
   assert d['mcpServers']['context7']['type'] == 'http'
   assert d['mcpServers']['context7']['url'] == 'https://mcp.context7.com/mcp'
   assert 'command' in d['mcpServers']['gitlab']
   print('MCP_SHAPE_OK')
   "
   ```
   Expected output: `MCP_SHAPE_OK`

7. Re-run in check mode to confirm the commit-worthy output matches a second
   generation deterministically:
   ```bash
   node implementation/scripts/sync.mjs --root implementation --check
   ```
   Expected: exit `0`, `OK - no drift across N files.` (run this AFTER staging/
   committing the generated files in step 8, or immediately after step 1 before
   any manual edits — the check must pass either way since generation is
   idempotent).

8. Stage and commit ALL newly generated files under `implementation/.claude/`
   and the new `implementation/.mcp.json`, plus any diff in the other 5
   platform output directories (there should be none, but include them if
   `git status` shows changes — that would indicate drift and must be reported
   as a blocker, not silently committed).

## Expected outputs
- `implementation/.claude/**` (new directory tree: `agents/`, `commands/`,
  `rules/`, `skills/`, `.generated-manifest.json`)
- `implementation/.mcp.json` (new file)
- No changes to `implementation/.cursor/`, `implementation/.github/`,
  `implementation/.gemini/`, `implementation/.opencode/`, `implementation/.pi/`

## Acceptance criteria
1. All 8 steps above produce their expected output exactly.
2. Verify command — file count sanity (agents/commands/rules/skills counts
   must match the other platforms' counts, since content is projected 1:1):
   ```bash
   diff <(ls implementation/.claude/agents | sort) <(ls implementation/.cursor/agents | sed 's/\.mdc$/.md/' | sort) && echo AGENT_COUNT_MATCH
   ```
   Expected output: `AGENT_COUNT_MATCH`
3. `git status --porcelain` shows ONLY additions under `implementation/.claude/`
   and `implementation/.mcp.json` (no modifications to other platform dirs).

## Revert rule
If any verify command fails:
```bash
git clean -fd implementation/.claude implementation/.mcp.json
git checkout -- implementation/.cursor implementation/.github implementation/.gemini implementation/.opencode implementation/.pi
```
then STOP and report which step failed and its exact output.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.
If the blocker is caused by T285/T286/T287 being wrong, name the exact task ID
to re-open rather than patching generated output by hand.

## Execution notes
<filled during execution>
