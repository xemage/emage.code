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

## Outcome

**Status:** BLOCKED — `implementation/platforms/cline.json` was **not** created. Step 0's live-docs
check found a material mismatch between this brief's assumed Cline config format and the current
content at https://docs.cline.bot, so per the Blocker Protocol above the manifest was not written
and no guess was substituted.

### Step 0 — what was checked
Fetched and reviewed the live pages (via `WebFetch`/`fetch_txt`, `docs.cline.bot/llms.txt` page
index, and direct page fetches on 2026-08-08):
- `https://docs.cline.bot/customization/cline-rules.md` (rules format)
- `https://docs.cline.bot/mcp/configuring-mcp-servers` (MCP config format)
- `https://docs.cline.bot/customization/skills.md` (skills format)
- `https://docs.cline.bot/llms.txt` (full doc-site page index, to check for a dedicated
  "Agents"/subagents on-disk-format page)

### What was found — discrepancies vs. this brief's assumptions

1. **Rules directory name and location (material mismatch).** Brief assumed `.cline/rules/*.md`
   (nested under a `.cline` output dir, `outputDir: ".cline"` + `fileMap.instructions.dir: "rules"`).
   Live docs state rules live in **`.clinerules/`** — a directory at the **project root**, not
   nested under `.cline/`. Cline processes all `.md`/`.txt` files inside `.clinerules/` directly.
2. **Rules frontmatter keys (material mismatch).** Brief assumed Cursor-style frontmatter
   (`description`, `globs` renamed from `applyTo`, `alwaysApply` retained via `keepKeys`). Live docs
   document exactly **one** conditional-rules frontmatter key: **`paths`** (an array of glob
   patterns). There is no documented `description`, `globs`, or `alwaysApply` key in Cline's rules
   frontmatter schema — rules without frontmatter are simply always active.
3. **Legacy single-file relationship (material mismatch).** Brief assumed `.cline/rules/*.md`
   "replaces a legacy single-file `.clinerules`", and the manifest's `extras` block mapped a
   fallback file to `../.clinerules` (singular, no trailing slash — implying a single dotfile).
   Live docs describe no such legacy single-file Cline format being superseded; `.clinerules/` (the
   **directory**) is itself the current, primary, documented format. (Other tools' single-file
   formats — `.cursorrules`, `.windsurfrules`, `AGENTS.md` — are auto-*detected* for cross-tool
   compatibility, which is a different concept from a superseded Cline-native legacy format.) The
   brief's `extras` entry as written would not even be structurally valid against the live format
   (a directory vs. a file at the same path).
4. **MCP config output filename (material mismatch).** Brief assumed `outputFile:
   "cline_mcp_settings.json"`. Live docs state the CLI reads `~/.cline/mcp.json`, and IDE extensions
   are configured through a settings panel UI — no project-relative file literally named
   `cline_mcp_settings.json` is documented anywhere on the current site.
5. **Skills format — confirmed current, no mismatch.** `.cline/skills/<name>/SKILL.md` with
   `name` + `description` YAML frontmatter matches the brief's assumption exactly (project-level
   skills recommended at `.cline/skills/`, global fallback at `~/.cline/skills/`).
6. **Agents on-disk format — unconfirmed, not found.** The full doc-site page index
   (`llms.txt`) has no page describing a `.cline/agents/*.md` on-disk subagent-definition format;
   the closest match, "Agent Teams" (`/cli/agent-teams`), documents CLI-level orchestration of
   multiple running agent *processes*, not a project-repo file format for agent definitions. This
   could not be confirmed or denied as matching the brief's assumption from the pages checked.

### Classification

- **Type:** `unclear_requirements`
- **Severity:** `major` (work on this task cannot proceed without new direction; it does not block
  unrelated work elsewhere in the repo)
- **Rationale:** items 1, 2, and 4 above are exactly the trigger conditions named in this brief's
  own Step 0 instructions and Blocker Protocol — "different directory names, different frontmatter
  keys, a different MCP config filename/shape" — so per explicit brief instruction this was not
  adapted into a best-guess manifest.

### Suggested resolution
Re-author the manifest's assumed shape against the confirmed-current format before re-attempting
T352:
- `fileMap.instructions` should emit to project-root `.clinerules/` rather than nested under
  `outputDir: ".cline"` (or `outputDir` needs to become `.` for the `instructions` file-map entry
  specifically — this is a `sync.mjs` capability question for whoever re-scopes T353 too, since
  today every fileMap entry is emitted under the platform's single `outputDir`).
- `frontmatter.instructions` should key off `paths` (glob array), not `applyTo`/`globs`/
  `alwaysApply` — the `renameKeys`/`alwaysApply` gating described in plan-028 §0 item 6 (and wired
  for T353) does not apply to Cline as currently documented.
- `extras` entry mapping to `../.clinerules` should be dropped or re-thought as a directory-based
  concept, not a single dotfile.
- `mcp.outputFile` should be reconsidered — possibly `mcp.json` under a `.cline` output dir (to
  match `~/.cline/mcp.json`'s trailing segment) rather than `cline_mcp_settings.json`.
- Confirm whether a `.cline/agents/*.md` format exists at all (may need to ask Cline maintainers or
  check the OSS repo directly, since the public docs site does not appear to define one).

No code changes were made. `implementation/platforms/cline.json` was not created. Only this task
brief was modified, to record the Step 0 findings and blocker per this task's own instructions.

**Acceptance criteria status:**
- [x] Step 0 live-docs check performed and recorded in this section
- [ ] `implementation/platforms/cline.json` exists and is valid JSON — **not attempted**, blocked
- [ ] `platform`/`displayName`/`outputDir` — **not attempted**, blocked
- [ ] `fileMap` — **not attempted**, blocked
- [ ] `frontmatter.instructions.renameKeys`/`keepKeys` — **not attempted**, blocked
- [ ] `frontmatter.agents.tools`/`toolMap` — **not attempted**, blocked
- [ ] `mcp` block — **not attempted**, blocked
- [ ] `extras` — **not attempted**, blocked
- [x] No other file in the repo modified
- [x] Task brief updated with an `## Outcome` section

**Blocker status:** `unclear_requirements` / `major` — awaiting orchestrator direction on how to
reconcile the manifest shape with Cline's confirmed-current on-disk format before this task (and
downstream T353–T357) can proceed.
