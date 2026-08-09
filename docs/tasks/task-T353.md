# Task T353 v2 — Extend sync.mjs for Cline (corrected format)

**ID:** T353
**Owner:** backend-developer
**Status:** pending
**Priority:** P0
**Depends on:** T352
**Created:** 2026-08-08 (revised 2026-08-09 for corrected Cline format)
**Based on:** `docs/plans/plan-028-cline-platform-integration-v2.md` §2; `implementation/scripts/sync.mjs`
(`syncPlatform()`, lines ~412-511 as of 2026-08-09 — re-read the current file, line numbers may have
shifted)

## Objective
Add two small, **generic** capabilities to `sync.mjs`'s `syncPlatform()` — not Cline-hardcoded — plus
one Cline-specific `emitMcp()` branch:
1. A `rootRelative: true` flag on a `fileMap` entry: resolve that entry's output directory against
   the repo root instead of the platform's `outputDir`, with a scoped wipe-then-regenerate safety net
   matching the existing whole-`outputDir` behavior.
2. Make the `agents` and `commands` fileMap loops **optional** — skip if the manifest doesn't declare
   that content type, instead of crashing on `undefined.dir`.
3. `emitMcp()` gains a `format === 'cline'` branch (this part is unchanged from the original v1
   design — only the *destination filename*, decided by T352's manifest, changed, not this function's
   logic).

## Context
- Phase: Implementation (plan-028-v2, step 2 of 6). Depends on T352's `cline.json` v2 existing with
  the exact shape from that brief: `fileMap.instructions = {dir: ".clinerules", ext: ".md",
  rootRelative: true}`, `fileMap.skills = {dir: "skills", preserveTree: true}`, no `agents`/`commands`.
- **This is a v2 replacement of T353's original brief** — the original asked for an
  `applyGenericFrontmatter()` `alwaysApply` gate, which is now moot (Cline has no `alwaysApply`
  concept; `applyGenericFrontmatter()` needs **zero changes** — its existing `renameKeys`/`keepKeys`
  handling already covers `applyTo`→`paths` with no code change, exactly like it already handles
  Cursor's `applyTo`→`globs`). Do not add any `alwaysApply` logic.
- `sync.mjs` auto-discovers platforms via `readdir(platforms/)` — no separate registration needed
  once the manifest exists and these engine additions land.

## Inputs
- `implementation/scripts/sync.mjs` — read the full file, especially `syncPlatform()`, before editing
- `implementation/platforms/cline.json` (T352's v2 output)

## Constraints
- **Both new engine capabilities must be generic**, not conditioned on `manifest.platform === 'cline'`
  anywhere. Read them off the manifest shape (`insMap.rootRelative`, presence/absence of
  `manifest.fileMap.agents`/`.commands`) so any future platform manifest can use them the same way.
- **Safety-critical**: before any `fs.rm(insRoot, { recursive: true, force: true })` call for a
  `rootRelative` entry, assert the resolved absolute path is a strict descendant of `ROOT` (not equal
  to `ROOT` itself, not outside it) and throw rather than proceed if that assertion fails. A manifest
  typo must never be able to wipe the repo root. Do not skip this check to save code — it's the one
  hard requirement in this brief.
- Do not restructure the whole-`outputDir` wipe at the top of `syncPlatform()` — it stays as-is; the
  `rootRelative` wipe is a separate, additional, narrower operation for that one entry only.
- Before assuming the `agents`/`commands` loops are the only places `manifest.fileMap.agents` /
  `.commands` are referenced, `grep -n "fileMap.agents\|fileMap.commands"
  implementation/scripts/sync.mjs` yourself and check every hit.
- Token budget: ≤ 30k.

## Expected Outputs
`implementation/scripts/sync.mjs`, modified with three changes. Read the current file first — exact
line numbers below are from the version read while writing this brief and may have shifted slightly;
match by content, not line number.

**1. `emitMcp()`** — add, adjacent to the existing `claude-code` branch:
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

**2. `agents` and `commands` loops in `syncPlatform()`** — wrap each existing loop body in a
guard, e.g.:
```javascript
if (manifest.fileMap.agents) {
  const agentMap = manifest.fileMap.agents;
  const agentCfg = manifest.frontmatter.agents;
  for (const file of await walk(path.join(KNOWLEDGE, 'agents'))) {
    // ... existing body, unchanged ...
  }
}
```
(Same pattern for `commands`.) Do not change the loop bodies themselves, only add the guard.

**3. `instructions` loop in `syncPlatform()`** — replace:
```javascript
const insMap = manifest.fileMap.instructions;
for (const file of await walk(path.join(KNOWLEDGE, 'instructions'))) {
  if (!file.endsWith('.md')) continue;
  const baseName = path.basename(file, '.md');
  const raw = await fs.readFile(file, 'utf8');
  const { data, body } = parseFrontmatter(raw);
  const newData = applyGenericFrontmatter(data, manifest.frontmatter.instructions);
  const outPath = path.join(outRoot, insMap.dir, baseName + insMap.ext);
  await emitFile(outPath, emitFrontmatter(newData) + body);
  filesWritten.push(outPath);
}
```
with:
```javascript
const insMap = manifest.fileMap.instructions;
const insRoot = insMap.rootRelative ? path.resolve(ROOT, insMap.dir) : path.join(outRoot, insMap.dir);
if (insMap.rootRelative) {
  const rootWithSep = ROOT.endsWith(path.sep) ? ROOT : ROOT + path.sep;
  if (insRoot === ROOT || !insRoot.startsWith(rootWithSep)) {
    throw new Error(`Refusing rootRelative fileMap target outside or equal to ROOT: ${insRoot}`);
  }
  if (!CHECK_ONLY) {
    await fs.rm(insRoot, { recursive: true, force: true });
  }
}
for (const file of await walk(path.join(KNOWLEDGE, 'instructions'))) {
  if (!file.endsWith('.md')) continue;
  const baseName = path.basename(file, '.md');
  const raw = await fs.readFile(file, 'utf8');
  const { data, body } = parseFrontmatter(raw);
  const newData = applyGenericFrontmatter(data, manifest.frontmatter.instructions);
  const outPath = path.join(insRoot, baseName + insMap.ext);
  await emitFile(outPath, emitFrontmatter(newData) + body);
  filesWritten.push(outPath);
}
```
Note: this changes behavior for **every** platform's `instructions` loop, but only when
`insMap.rootRelative` is truthy — for the 6 existing platforms (none of which set that flag),
`insRoot` evaluates to exactly `path.join(outRoot, insMap.dir)`, identical to today's behavior. Verify
this explicitly (see acceptance criteria).

**Expected side effect, not a bug**: the `.generated-manifest.json` written under `.cline/` records
each file's path via `path.relative(outRoot, f)`; for the root-relative `.clinerules/*.md` files this
correctly produces `../.clinerules/<name>.md` (a valid relative path pointing outside `outRoot`). Do
not "fix" this — it's correct, just note it so T354 doesn't flag it as a defect.

## Acceptance Criteria
- [ ] `emitMcp()` has a new `format === 'cline'` branch matching the snippet above
- [ ] `agents` and `commands` loops in `syncPlatform()` are each guarded by
      `if (manifest.fileMap.agents)` / `if (manifest.fileMap.commands)` — loop bodies otherwise
      unchanged
- [ ] `instructions` loop uses `insRoot` computed per the snippet above, with the descendant-of-ROOT
      assertion in place before any `fs.rm` call
- [ ] `applyGenericFrontmatter()` was **not** modified (confirm by checking `git diff` touches no
      lines in that function)
- [ ] `node implementation/scripts/sync.mjs --platform=cline` exits 0, creates `.clinerules/*.md` at
      the **repo root** (sibling of `implementation/`, not nested under `.cline/`) and `.cline/`
      containing `skills/`, `mcp.json`, `.generated-manifest.json`
- [ ] `node implementation/scripts/sync.mjs` (all platforms) exits 0, no platform skipped
- [ ] `node implementation/scripts/sync.mjs --check` (all platforms) still exits 0 for the 6
      pre-existing platforms — confirm via `git diff --stat` after a real sync run: only `.clinerules/`
      and `.cline/` paths (plus `implementation/platforms/cline.json`,
      `implementation/scripts/sync.mjs`) appear, nothing under `.cursor/`, `.github/`, `.gemini/`,
      `.opencode/`, `.pi/`, `.claude/`
- [ ] Manually verify the safety assertion: temporarily (in a scratch test, not committed) set
      `insMap.dir` to `"."` or `".."` in a local test and confirm `sync.mjs` throws rather than
      deleting `ROOT` — revert the scratch change before finishing, do not leave it in the diff
- [ ] Task brief updated with an `## Outcome` section
- [ ] `grep -n "fileMap.agents\|fileMap.commands" implementation/scripts/sync.mjs` output included in
      the Outcome section, confirming every reference was accounted for

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. If the current
`sync.mjs` differs structurally from what this brief assumes (e.g. `syncPlatform()` has been
refactored since 2026-08-09), that's a `technical` blocker of `minor` severity — report the
difference, adapt the same two capabilities to the current structure, and note the adaptation in the
Outcome section.
