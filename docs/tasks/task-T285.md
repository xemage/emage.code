# Task T285 — sync.mjs: add `tools: "string"` frontmatter mode

**ID:** T285
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** —
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T285

## Why this task exists
Claude Code subagent files (`.claude/agents/<name>.md`) declare their allowed
tools as a **comma-separated string** in YAML frontmatter, e.g.:
```yaml
tools: Read, Grep, Glob
```
The sync engine (`implementation/scripts/sync.mjs`) currently only supports
two `tools` output shapes:
- `"array"` → `tools: [read, search, edit]` (used by cursor, github, pi)
- `"object"` → `tools:\n  read: true\n  search: true` (used by opencode)

There is no `"string"` mode. Without it, a Claude Code manifest with
`"tools": "string"` would silently fall through to the `else` branch and emit
an array, which Claude Code does not parse as a tool list correctly.

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `implementation/scripts/sync.mjs`
- Do **NOT** create `implementation/platforms/claude-code.json` in this task —
  that is T287.
- Do **NOT** run `make sync`, `install.sh`, or the test suite in this task.
  You are only editing the sync engine source.
- **R5** If any exact find-text below is not found, STOP and report
  `PRECONDITION FAILED: T285`.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `feat(sync): T285 add tools=string frontmatter mode for Claude Code`

## Objective
Add a third `tools` emission mode, `"string"`, to `sync.mjs` so a platform
manifest can declare `"tools": "string"` in its `frontmatter.agents` config and
get `tools: Read, Grep, Glob` (comma-and-space-separated, first letter of each
tool capitalized per Claude Code convention is NOT required — keep the raw
tool slugs as-is, e.g. `read, search, edit`, exactly as they appear in the
source `tools:` array — do not rename or capitalize them).

## Edit 1 — `applyAgentFrontmatter` (tools mode selection)

**FIND this block (occurs exactly once):**
```js
  if (cfg.tools === 'drop') {
    delete out.tools;
  } else if (cfg.tools === 'object') {
    if (Array.isArray(tools)) out.tools = tools;
  } else {
    if (Array.isArray(tools)) out.tools = tools;
  }
```

**REPLACE WITH exactly this block:**
```js
  if (cfg.tools === 'drop') {
    delete out.tools;
  } else if (cfg.tools === 'object') {
    if (Array.isArray(tools)) out.tools = tools;
  } else if (cfg.tools === 'string') {
    if (Array.isArray(tools)) out.tools = tools;
  } else {
    if (Array.isArray(tools)) out.tools = tools;
  }
```

> Note: at this stage `out.tools` still holds the raw array — the array-to-string
> serialization happens in `emitFrontmatter` (Edit 2), keyed off `toolsFormat`.
> This edit only ensures the `"string"` branch does not fall into `drop`.

## Edit 2 — `emitFrontmatter` (string serialization)

**FIND this block (occurs exactly once):**
```js
function emitFrontmatter(obj, opts = { toolsFormat: 'array' }) {
  const lines = ['---'];
  for (const [key, val] of Object.entries(obj)) {
    if (val === undefined || val === null) continue;
    if (key === 'tools' && opts.toolsFormat === 'object' && Array.isArray(val)) {
      lines.push('tools:');
      for (const t of val) lines.push(`  ${t}: true`);
      continue;
    }
    if (Array.isArray(val)) {
```

**REPLACE WITH exactly this block:**
```js
function emitFrontmatter(obj, opts = { toolsFormat: 'array' }) {
  const lines = ['---'];
  for (const [key, val] of Object.entries(obj)) {
    if (val === undefined || val === null) continue;
    if (key === 'tools' && opts.toolsFormat === 'object' && Array.isArray(val)) {
      lines.push('tools:');
      for (const t of val) lines.push(`  ${t}: true`);
      continue;
    }
    if (key === 'tools' && opts.toolsFormat === 'string' && Array.isArray(val)) {
      lines.push(`tools: ${val.join(', ')}`);
      continue;
    }
    if (Array.isArray(val)) {
```

## Edit 3 — wire `toolsFormat` selection to `"string"`

**FIND this block (occurs exactly once):**
```js
    const newData = applyAgentFrontmatter(data, baseName, agentCfg);
    const fm = emitFrontmatter(newData, {
      toolsFormat: agentCfg.tools === 'object' ? 'object' : 'array',
    });
```

**REPLACE WITH exactly this block:**
```js
    const newData = applyAgentFrontmatter(data, baseName, agentCfg);
    const fm = emitFrontmatter(newData, {
      toolsFormat: agentCfg.tools === 'object' ? 'object' : agentCfg.tools === 'string' ? 'string' : 'array',
    });
```

## Expected outputs
- `implementation/scripts/sync.mjs` modified with the 3 edits above.
- Nothing else changed. No new files. No generated output changed (no manifest
  references `"tools": "string"` yet).

## Acceptance criteria
1. Verify command:
   ```bash
   grep -Fc "cfg.tools === 'string'" implementation/scripts/sync.mjs
   ```
   Expected output: `1`
2. Verify command:
   ```bash
   grep -Fc "opts.toolsFormat === 'string'" implementation/scripts/sync.mjs
   ```
   Expected output: `1`
3. Verify command:
   ```bash
   grep -Fc "agentCfg.tools === 'string' ? 'string' : 'array'" implementation/scripts/sync.mjs
   ```
   Expected output: `1`
4. Syntax check (must not throw):
   ```bash
   node --check implementation/scripts/sync.mjs
   ```
   Expected: no output, exit code `0`.
5. Regression check — existing platforms must be byte-for-byte unaffected
   (no manifest uses `"tools": "string"` yet, so this change is inert):
   ```bash
   node implementation/scripts/sync.mjs --root implementation --check
   ```
   Expected: exit `0`, `OK - no drift across N files.`
6. `git status --porcelain` lists exactly one modified file:
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
