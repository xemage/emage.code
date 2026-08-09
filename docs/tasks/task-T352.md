# Task T352 v2 — Create Cline Platform Manifest (corrected format)

**ID:** T352
**Owner:** backend-developer
**Status:** pending
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-08 (revised 2026-08-09 for corrected Cline format)
**Based on:** `docs/plans/plan-028-cline-platform-integration-v2.md` §0, §2 (supersedes v1's brief,
kept below the fold as historical record — see `## Outcome (v1 attempt)` at the bottom of this file)

## Objective
Author `implementation/platforms/cline.json` covering only what's confirmed to exist in Cline's
documented format: project rules and skills, plus an MCP staging file. No `agents`, `commands`, or
`extras` block — those are explicitly out of scope this pass (§2 of the v2 plan).

## Context
- Phase: Implementation (plan-028-v2, step 1 of 6).
- **The live-docs verification this brief would normally ask you to do in a "Step 0" has already
  been done twice** — once by the delegate who attempted T352 v1 (2026-08-08), once independently by
  the orchestrator re-fetching the same pages (2026-08-08/09). Both confirmed the same format. You do
  not need to re-fetch https://docs.cline.bot before writing the manifest. If you have any reason to
  suspect the format has changed since (e.g. you notice something inconsistent while working), stop
  and report an `unclear_requirements` blocker rather than guessing — same discipline as before, just
  not a mandatory re-check this time since it was just done.
- Confirmed format (this is what you're encoding, not a hypothesis):
  - Rules live in **`.clinerules/` at the project root** — a directory, not nested under `.cline/`.
    Files are `.md`/`.txt`, optionally with YAML frontmatter containing exactly one conditional key,
    `paths` (a glob array). Files with no frontmatter are always active.
  - Skills live in `.cline/skills/<name>/SKILL.md` with `name` + `description` frontmatter —
    unchanged from v1, this part was never wrong.
  - MCP server config is a **global** file (`~/.cline/mcp.json` for the CLI); there is no documented
    project-relative MCP config file. This manifest generates a **staging file**,
    `.cline/mcp.json`, that a human copies/merges into the real global config — `sync.mjs` never
    writes outside the repo.

## Inputs
- `implementation/platforms/cursor.json` — closest shape reference for the `renameKeys` pattern
  (`applyTo` → a different key name), even though the target key name differs (`paths`, not
  `globs`).
- `implementation/platforms/claude-code.json` — reference for `mcp.format` shape (its `emitMcp`
  branch is what Cline's will mirror, per T353).

## Constraints
- **Do not add `fileMap.agents`, `fileMap.commands`, or `extras`.** No confirmed format exists for
  Cline subagents or slash commands, and there is no legacy-fallback-file concept to project either
  (that was a v1 mistake — `.clinerules/` the directory is itself the primary current format, not a
  fallback target).
- **Do not create `implementation/platforms/_manifest.schema.json`** — same reasoning as v1, it
  doesn't exist for any platform in this repo.
- **Do not modify `implementation/scripts/sync.mjs`, `scripts/install.sh`, or any docs file** — those
  are T353/T355/T356.
- Token budget: ≤ 10k (smaller than v1 — fewer fileMap types to encode).

## Expected Outputs
`implementation/platforms/cline.json`:

```json
{
  "$schema": "./_manifest.schema.json",
  "platform": "cline",
  "displayName": "Cline",
  "outputDir": ".cline",
  "fileMap": {
    "instructions": { "dir": ".clinerules", "ext": ".md", "rootRelative": true },
    "skills": { "dir": "skills", "preserveTree": true }
  },
  "frontmatter": {
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
    "outputFile": "mcp.json",
    "format": "cline"
  }
}
```

Note on `fileMap.instructions.dir`: this is `.clinerules` (no `../` prefix) because T353 adds a
`rootRelative: true` flag that resolves `dir` against the repo root directly, not against `outputDir`
— a cleaner, more explicit design than the `../`-escape trick considered and rejected during
re-planning. `mcp.format: "cline"` does not exist yet in `sync.mjs`'s `emitMcp()` — that's expected,
T353 adds it, same as v1.

## Acceptance Criteria
- [ ] `implementation/platforms/cline.json` exists and is valid JSON
      (`python3 -m json.tool < implementation/platforms/cline.json` exits 0)
- [ ] `platform` is `"cline"`, `displayName` is `"Cline"`, `outputDir` is `".cline"`
- [ ] `fileMap` has exactly two entries: `instructions` (`dir: ".clinerules"`, `ext: ".md"`,
      `rootRelative: true`) and `skills` (`dir: "skills"`, `preserveTree: true`) — no `agents`, no
      `commands`
- [ ] `frontmatter.instructions.renameKeys` is `{"applyTo": "paths"}` and `keepKeys` is exactly
      `["description", "paths"]` — no `alwaysApply`, no `globs`
- [ ] `frontmatter.skills.keepKeys` is `["name", "description"]`
- [ ] No `frontmatter.agents`, no `frontmatter.commands`
- [ ] `mcp` block matches exactly: `tags: ["core", "extended"]`, `outputFile: "mcp.json"`,
      `format: "cline"`
- [ ] No `extras` key present at all
- [ ] No other file in the repo modified
- [ ] Task brief updated with an `## Outcome (v2)` section (add this as a new section — do not
      delete or edit the existing `## Outcome (v1 attempt)` section below, it's kept as history)

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. If you find a
reason to doubt the confirmed format above, that's an `unclear_requirements` blocker — report the
specific new discrepancy found, citing what you checked, rather than guessing.

---

## Outcome (v1 attempt, 2026-08-08 — historical, format later found wrong, do not use)

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
- **Severity:** `major`

### Resolution
Orchestrator independently re-verified findings 1, 2, and 4 above against the same live docs
(2026-08-08/09), confirmed them, escalated to the user via `AskUserQuestion`, and received direction:
redesign now with reduced scope. See `docs/plans/plan-028-cline-platform-integration-v2.md` and the
`## Outcome (v2)` section above (once filled in) for what actually shipped.

## Outcome (v2, 2026-08-09)

**Status:** DONE — `implementation/platforms/cline.json` created exactly per the corrected format in
this brief's Expected Outputs section (§ above), based on
`docs/plans/plan-028-cline-platform-integration-v2.md` §0/§2.

### What was produced
- `implementation/platforms/cline.json` — new file. `fileMap` has exactly two entries
  (`instructions`: `.clinerules`, root-relative, `.md`; `skills`: `skills`, `preserveTree`). No
  `agents`, `commands`, or `extras`. `frontmatter.instructions` renames `applyTo` → `paths` and keeps
  only `["description", "paths"]`. `frontmatter.skills` keeps `["name", "description"]`. `mcp` block
  is `{"tags": ["core", "extended"], "outputFile": "mcp.json", "format": "cline"}`.
- Task brief updated with this section (no edits to the `## Outcome (v1 attempt)` section above).

### Acceptance criteria — results
- [x] `implementation/platforms/cline.json` exists and is valid JSON — verified with
      `python3 -m json.tool < implementation/platforms/cline.json` (exit 0)
- [x] `platform` is `"cline"`, `displayName` is `"Cline"`, `outputDir` is `".cline"`
- [x] `fileMap` has exactly two entries: `instructions` (`dir: ".clinerules"`, `ext: ".md"`,
      `rootRelative: true`) and `skills` (`dir: "skills"`, `preserveTree: true`) — no `agents`, no
      `commands`
- [x] `frontmatter.instructions.renameKeys` is `{"applyTo": "paths"}` and `keepKeys` is exactly
      `["description", "paths"]` — no `alwaysApply`, no `globs`
- [x] `frontmatter.skills.keepKeys` is `["name", "description"]`
- [x] No `frontmatter.agents`, no `frontmatter.commands`
- [x] `mcp` block matches exactly: `tags: ["core", "extended"]`, `outputFile: "mcp.json"`,
      `format: "cline"`
- [x] No `extras` key present at all
- [x] No other file in the repo modified besides this brief's own `## Outcome (v2)` addition
- [x] Task brief updated with this `## Outcome (v2)` section, `## Outcome (v1 attempt)` left untouched

All checks verified programmatically (JSON structural assertions against every field above) before
commit; see MR for the diff.

### Notes
- Did not re-fetch docs.cline.bot — per this brief's Context section, the format had already been
  independently confirmed twice (v1 delegate + orchestrator) and no new inconsistency was observed
  while authoring the manifest, so the live re-check was not triggered.
- `mcp.format: "cline"` and `fileMap.instructions.rootRelative: true` are consumed by `sync.mjs` only
  once T353 lands; this task does not modify `sync.mjs` (explicitly out of scope per Constraints).
- **Blocker status:** None.
