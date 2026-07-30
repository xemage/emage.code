# Task T286 — sync.mjs: add `.mcp.json` MCP output format for Claude Code

**ID:** T286
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T285
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T286

## Why this task exists
Claude Code reads MCP server configuration from a **repo-root** `.mcp.json`
file shaped like:
```json
{
  "mcpServers": {
    "gitlab": { "command": "npx", "args": ["-y", "@zereight/mcp-gitlab"], "env": { "GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_PERSONAL_ACCESS_TOKEN}" } },
    "context7": { "type": "http", "url": "https://mcp.context7.com/mcp" }
  }
}
```
This is close to, but not identical to, the existing `"cursor"` MCP format
(which nests under `.cursor/mcp.json`, not repo root, and does not need a
`"type": "http"` key for remote servers — Cursor infers it from `url`
presence). Claude Code **requires an explicit `"type"` field** for remote
(HTTP) servers, or it treats the entry as a misconfigured stdio server. This
task adds a new `"claude-code"` MCP format branch to `emitMcp` in `sync.mjs`.

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `implementation/scripts/sync.mjs`
- Do **NOT** create `implementation/platforms/claude-code.json` in this task —
  that is T287.
- Do **NOT** run `make sync`, `install.sh`, or the test suite in this task.
- **R5** If the exact find-text below is not found, STOP and report
  `PRECONDITION FAILED: T286`.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `feat(sync): T286 add claude-code .mcp.json MCP output format`

## Objective
Add a new format branch, `"claude-code"`, to the `emitMcp` function so a
platform manifest can declare `"format": "claude-code"` in its `mcp` config
and get a `.mcp.json`-shaped payload with `mcpServers`, where remote servers
get an explicit `"type": "http"` key and stdio servers get `command`/`args`/
`env` (same env-mapping convention as the existing formats: `${env:VAR}`
style placeholders via `mapEnv`).

## Edit — add the new format branch to `emitMcp`

**FIND this block (occurs exactly once, immediately before the final `throw`):**
```js
  if (format === 'opencode') {
    const mcp = {};
    for (const [name, s] of Object.entries(filtered)) {
      if (s.transport === 'remote') mcp[name] = { type: 'remote', url: s.url };
      else {
        mcp[name] = { type: 'local', command: [s.command, ...(s.args || [])] };
        if (s.env) mcp[name].environment = mapEnv(s.env, '{env:VAR}');
      }
    }
    return { __mcpObject: mcp };
  }

  throw new Error(`Unknown MCP format: ${format}`);
```

**REPLACE WITH exactly this block:**
```js
  if (format === 'opencode') {
    const mcp = {};
    for (const [name, s] of Object.entries(filtered)) {
      if (s.transport === 'remote') mcp[name] = { type: 'remote', url: s.url };
      else {
        mcp[name] = { type: 'local', command: [s.command, ...(s.args || [])] };
        if (s.env) mcp[name].environment = mapEnv(s.env, '{env:VAR}');
      }
    }
    return { __mcpObject: mcp };
  }

  if (format === 'claude-code') {
    const mcpServers = {};
    for (const [name, s] of Object.entries(filtered)) {
      if (s.transport === 'remote') mcpServers[name] = { type: 'http', url: s.url };
      else {
        mcpServers[name] = { command: s.command, args: s.args || [] };
        if (s.env) mcpServers[name].env = mapEnv(s.env, '${env:VAR}');
      }
    }
    return JSON.stringify({ mcpServers }, null, 2) + '\n';
  }

  throw new Error(`Unknown MCP format: ${format}`);
```

## Expected outputs
- `implementation/scripts/sync.mjs` modified with the edit above.
- Nothing else changed. No manifest references `"format": "claude-code"` yet,
  so no generated output changes.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -Fc "format === 'claude-code'" implementation/scripts/sync.mjs
   ```
   Expected output: `1`
2. Verify command:
   ```bash
   grep -Fc "type: 'http', url: s.url" implementation/scripts/sync.mjs
   ```
   Expected output: `1`
3. Syntax check:
   ```bash
   node --check implementation/scripts/sync.mjs
   ```
   Expected: no output, exit code `0`.
4. Regression check — no existing platform emits `"claude-code"` format yet:
   ```bash
   node implementation/scripts/sync.mjs --root implementation --check
   ```
   Expected: exit `0`, `OK - no drift across N files.`
5. `git status --porcelain` lists exactly one modified file:
   `implementation/scripts/sync.mjs`.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/scripts/sync.mjs
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
