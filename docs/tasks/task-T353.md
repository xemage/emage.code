# Task T353 — Extend sync.mjs for Cline

**ID:** T353
**Owner:** backend-developer
**Status:** pending
**Priority:** P0
**Depends on:** T352
**Created:** 2026-08-08
**Based on:** `docs/plans/plan-028-cline-platform-integration.md` §0.6; `implementation/scripts/sync.mjs`
(read in full for this plan)

## Objective
Add the two pieces of Cline-specific logic `sync.mjs` is actually missing: an `emitMcp()` branch for
`format === 'cline'`, and a scoped `alwaysApply` default in `applyGenericFrontmatter()`. Everything
else Cline's manifest needs (`tools: "string"` rendering, `toolMap` expansion) **already works** —
verify this before writing any code, do not duplicate it.

## Context
- Phase: Implementation (plan-028, step 2 of 6). Depends on T352's `implementation/platforms/cline.json`
  existing with the exact shape specified there.
- `sync.mjs` auto-discovers platforms by reading `implementation/platforms/*.json` at runtime
  (`readdir(PLATFORMS)` — see the function around line 523). **You do not need to register `cline`
  anywhere else** — once the manifest exists and the format branches below are added, `--platform=cline`
  and the all-platforms `sync`/`--check` runs will pick it up automatically.
- **Already implemented — do not rewrite these**: `emitFrontmatter()` (line ~136) already has a
  `toolsFormat === 'string'` branch (`tools: ${val.join(', ')}` — a plain string, not a YAML list).
  `applyAgentFrontmatter()` (line ~240) already has a `cfg.tools === 'string'` branch that expands
  tool names through `cfg.toolMap` and joins any comma-containing map values into separate entries.
  Both were read in full while drafting this task and confirmed to already satisfy Cline's
  `frontmatter.agents.tools: "string"` + `toolMap` config from T352 with **zero code changes**. If you
  find yourself editing either function, stop — you're duplicating existing logic; the manifest config
  alone should be sufficient.

## Inputs
- `implementation/scripts/sync.mjs` — read the full file, not just the excerpts below, before editing.
- `implementation/platforms/cline.json` (from T352)

## Constraints
- **Do not restructure existing platform branches.** Add new code adjacent to the existing
  `claude-code` branches (in `emitMcp()`, that branch starts with `if (format === 'claude-code') {`),
  following the same pattern.
- **`applyGenericFrontmatter()` is shared by every platform** (cursor also uses it, with
  `renameKeys: {applyTo: "globs"}` but no `alwaysApply` in its `keepKeys`). The default-injection
  logic below **must** be gated on `cfg.keepKeys` containing `alwaysApply` — this is currently true
  only for `cline.json`. Do **not** gate it on a hardcoded `platform === 'cline'` check (the function
  doesn't receive a platform name today, and adding one would be a wider signature change than this
  fix needs) and do **not** apply it unconditionally (it would silently add `alwaysApply: false` to
  every future platform's rules output that happens to have `globs` set, which is wrong for any
  platform whose `keepKeys` doesn't list `alwaysApply`).
- Token budget: ≤ 30k.

## Expected Outputs
`implementation/scripts/sync.mjs`, modified with exactly two additions:

**1. In `emitMcp()`, immediately after the existing `if (format === 'claude-code') { ... }` block,
add:**
```javascript
if (format === 'cline') {
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
```
(This mirrors the existing `claude-code` branch exactly — Cline and Claude Code use the same
`mcpServers` shape for stdio and remote/HTTP servers.)

**2. In `applyGenericFrontmatter()`, after the existing `keepKeys` loop that builds `out`, add:**
```javascript
if (cfg.keepKeys?.includes('alwaysApply') && out.globs && out.alwaysApply === undefined) {
  out.alwaysApply = false;
}
```
(Gated on `cfg.keepKeys` — see Constraints above for why this exact gate, not a platform-name check.)

`_extras/cline/dot-clinerules` (new file) — the root `.clinerules` fallback content referenced by
`cline.json`'s `extras` entry. Minimum content:
```markdown
@AGENTS.md

## Cline

This project follows the emage.code multi-agent protocol defined in the imported `AGENTS.md` above.
Cline-specific notes: path-scoped rules also live in `.cline/rules/*.md` — check there for rules that
apply only to specific file globs. This root file is a fallback for Cline builds that do not yet read
`.cline/rules/` directly.
```
(Match the style of `.claude/CLAUDE.md`'s `@AGENTS.md`-import pattern — read that file for the exact
convention before writing this one.)

## Acceptance Criteria
- [ ] Confirmed by reading the current file that `emitFrontmatter()`'s `toolsFormat: 'string'` branch
      and `applyAgentFrontmatter()`'s `cfg.tools === 'string'` + `toolMap` branch already exist and
      were **not** modified
- [ ] `emitMcp()` has a new `format === 'cline'` branch matching the snippet above, placed adjacent to
      the `claude-code` branch
- [ ] `applyGenericFrontmatter()` has the gated `alwaysApply` default matching the snippet above
- [ ] `_extras/cline/dot-clinerules` created, contains an `@AGENTS.md` import line and a short
      Cline-specific note pointing at `.cline/rules/`
- [ ] `node implementation/scripts/sync.mjs --platform=cline` exits 0 with no errors
- [ ] `node implementation/scripts/sync.mjs` (all platforms, no `--platform` filter) exits 0 with no
      errors and no platform skipped
- [ ] `node implementation/scripts/sync.mjs --check` (all platforms) still exits 0 for the 6
      pre-existing platforms — i.e. the `alwaysApply` gate did **not** change any existing platform's
      output. Verify explicitly: run `git diff --stat` after the sync and confirm only `.cline/` paths
      (and `implementation/platforms/cline.json`, `_extras/cline/`, `implementation/scripts/sync.mjs`)
      appear — no diff under `.cursor/`, `.github/`, `.gemini/`, `.opencode/`, `.pi/`, `.claude/`
- [ ] Task brief updated with an `## Outcome` section

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. If the "already
implemented" claim above turns out to be wrong when you read the current file (e.g. someone changed
`emitFrontmatter`/`applyAgentFrontmatter` between this brief being written and this task starting),
that's a `technical` blocker of `minor` severity — report what actually differs, then proceed with
whatever minimal fix is needed, noting the discrepancy in the Outcome section.
