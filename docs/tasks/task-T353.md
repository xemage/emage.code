# Task T353 v2 — Extend sync.mjs for Cline (corrected format)

**ID:** T353
**Owner:** backend-developer
**Status:** done
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

## Outcome

**Status:** Complete. No structural deviation encountered — the current `implementation/scripts/sync.mjs`
matched the brief's assumed shape of `syncPlatform()` and `emitMcp()` almost exactly (only cosmetic
line-number drift), so all three changes were applied verbatim per the Expected Outputs snippets, no
adaptation needed.

**Branch note:** the local branch name `agent/backend-developer/T352-v2` was already checked out in a
sibling worktree (`.../worktrees/agent-ab21a6e2172f62c6d`, at commit `c9acc08`) at the time this task
started, so git refused to check out that same branch name a second time in this worktree. Worked
around by checking out a differently-named local branch (`t353-work`) tracking
`origin/agent/backend-developer/T352-v2` at the same commit, then pushing the result back to the
correct remote branch name `agent/backend-developer/T352-v2` (updating MR !141 in place) — no new MR
opened, no branch rename on the remote side.

### Changes made (`implementation/scripts/sync.mjs`)
1. `emitMcp()` — added a `format === 'cline'` branch, adjacent to the existing `claude-code` branch,
   matching the brief's snippet exactly (mcpServers with `type: 'http'` for remote transport,
   `command`/`args`/`env` for local, `env` mapped via `${env:VAR}`).
2. `agents` and `commands` loops in `syncPlatform()` — each wrapped in
   `if (manifest.fileMap.agents) { ... }` / `if (manifest.fileMap.commands) { ... }` guards; loop
   bodies unchanged, only re-indented under the new guard.
3. `instructions` loop in `syncPlatform()` — added `insRoot` computation:
   `insMap.rootRelative ? path.resolve(ROOT, insMap.dir) : path.join(outRoot, insMap.dir)`, with the
   descendant-of-ROOT safety assertion (`insRoot === ROOT || !insRoot.startsWith(rootWithSep)` →
   throw) guarding the scoped `fs.rm(insRoot, ...)` wipe before the write loop; all `insMap.dir`
   references in the loop body switched to use `insRoot` (built from `path.join(insRoot, ...)`
   instead of `path.join(outRoot, insMap.dir, ...)`).

`applyGenericFrontmatter()` was **not** touched — confirmed via `git diff implementation/scripts/sync.mjs`,
no hunk overlaps its function body (lines ~278-291); the only `applyGenericFrontmatter(` diff lines are
call sites shifting under the new `commands`/`instructions` guard indentation, not the function
definition.

### `grep -n "fileMap.agents\|fileMap.commands" implementation/scripts/sync.mjs` output
```
432:  if (manifest.fileMap.agents) {
433:    const agentMap = manifest.fileMap.agents;
450:  if (manifest.fileMap.commands) {
451:    const cmdMap = manifest.fileMap.commands;
```
Both hits are the two guard sites added in this change (§2 above) — no other references to
`fileMap.agents`/`fileMap.commands` exist anywhere else in the file.

### Acceptance criteria — results
- [x] `emitMcp()` has a new `format === 'cline'` branch matching the snippet above
- [x] `agents` and `commands` loops guarded by `if (manifest.fileMap.agents)` /
      `if (manifest.fileMap.commands)` — loop bodies otherwise unchanged
- [x] `instructions` loop uses `insRoot` per the snippet, descendant-of-ROOT assertion in place before
      any `fs.rm` call
- [x] `applyGenericFrontmatter()` not modified (verified via `git diff`, see above)
- [x] `node implementation/scripts/sync.mjs --platform=cline` exits 0; created `.clinerules/*.md`
      (`coding-standards.md`, `git-workflow.md`, `poc-guidelines.md`, `security-guidelines.md`) as a
      sibling of the other generated platform dirs at `ROOT` (i.e. `implementation/.clinerules`,
      sibling of `implementation/.cursor`, `implementation/.github`, etc. — `ROOT` resolves to
      `implementation/` by default, since `__dirname` is derived from the script's own location, not
      cwd), not nested under `.cline/`; `.cline/` contained `skills/`, `mcp.json`,
      `.generated-manifest.json` as expected. `.generated-manifest.json`'s `files` list correctly shows
      `../.clinerules/<name>.md` entries per the brief's documented expected side effect.
- [x] `node implementation/scripts/sync.mjs` (all platforms) exits 0, wrote 550 files across all 7
      platforms (`claude-code`, `cline`, `cursor`, `gemini`, `github`, `opencode`, `pi`), none skipped
- [x] `node implementation/scripts/sync.mjs --check` exits 0 for all 7 platforms — "OK - no drift
      across 550 files." `git status --porcelain` after a real sync run showed only
      `implementation/.cline/` and `implementation/.clinerules/` (new, untracked) plus the modified
      `implementation/scripts/sync.mjs` — nothing under `implementation/.cursor/`,
      `implementation/.github/`, `implementation/.gemini/`, `implementation/.opencode/`,
      `implementation/.pi/`, `implementation/.claude/` changed (all 6 pre-existing platforms
      byte-identical to their prior committed output).
- [x] Safety assertion manually verified in a scratch test (not committed): temporarily set
      `fileMap.instructions.dir` to `"."` in `implementation/platforms/cline.json` and re-ran
      `node implementation/scripts/sync.mjs --platform=cline` — threw
      `Error: Refusing rootRelative fileMap target outside or equal to ROOT: <ROOT path>` and exited
      1, no wipe occurred. Repeated with `dir: ".."` — threw the same error class for the
      resolved-parent-of-ROOT path, also exited 1, no wipe. `cline.json` was restored from a backup
      copy in the scratchpad directory afterward; `git diff --stat -- implementation/platforms/cline.json`
      showed no changes remaining, confirming the scratch edit was not left in the diff.
- [x] Task brief updated with this `## Outcome` section
- [x] `grep -n "fileMap.agents\|fileMap.commands"` output included above

### Scope note
Per the top-level dispatch instructions, the generated `implementation/.cline/` and
`implementation/.clinerules/` output produced during the acceptance-criteria test runs above was
deleted before the final commit (not part of this task's Expected Outputs — plan-028-v2 assigns
committing the generated output to T354, which consumes this task's `sync.mjs` changes). Only
`implementation/scripts/sync.mjs` and this task brief's `## Outcome` section are included in the
commit. `implementation/platforms/cline.json` and `docs/tasks/task-T352.md` were not re-touched.

**Blocker status:** None.
