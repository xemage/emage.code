# Task T293 — Update CONTRIBUTING.md and AGENTS.md platform references

**ID:** T293
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T292
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T293

## Why this task exists
`CONTRIBUTING.md` documents which folders are generated (must list `.claude/`
now) and the "Adding a new platform" recipe (currently claims "No script
changes are needed", which was **not** true for this platform — T285/T286 had
to add two new engine modes). The root `AGENTS.md` is the repository's own
`platform=all`-rendered reference copy (compare it to the output of
`scripts/render_installed_agents.py --platform all` — the platform-list
phrasing matches exactly) and lists every generated platform folder and MCP
config path in five places; each needs the `.claude/` / `.mcp.json` addition
so the repo's own conventions doc stays consistent with what T291 now renders
for installed projects.

## STOP-RULES (read before touching anything)
- Confirm T292 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T293 (missing dependency)`.
- **R2** This task touches **EXACTLY TWO FILES**: `CONTRIBUTING.md`, `AGENTS.md`
  (repository root). Do **NOT** touch `implementation/AGENTS.md` — that file
  uses generic `knowledge/`-relative phrasing, not per-platform paths, and
  needs no change.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `docs: T293 add claude-code to CONTRIBUTING.md and AGENTS.md`

## Edit 1 — `CONTRIBUTING.md` "Where to make changes" table

**FIND this exact line (occurs exactly once):**
```markdown
| **Never** edit by hand | `.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/` (generated under `implementation/`) | these are generated |
```

**REPLACE WITH exactly this line:**
```markdown
| **Never** edit by hand | `.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`, `.claude/` (generated under `implementation/`) | these are generated |
```

## Edit 2 — `CONTRIBUTING.md` "Sync engine" section

**FIND this exact line (occurs exactly once):**
```markdown
The platform folders (`.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`)
are **generated**. CI fails if they drift from `knowledge/`.
```

**REPLACE WITH exactly this line:**
```markdown
The platform folders (`.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`,
`.claude/`) are **generated**. CI fails if they drift from `knowledge/`.
```

## Edit 3 — `CONTRIBUTING.md` "Adding a new platform" section

**FIND this exact block (occurs exactly once):**
```markdown
## Adding a new platform

1. Create `implementation/platforms/<name>.json` (use `cursor.json` as a template)
2. Run `make sync`
3. Verify the generated `<name>/` folder
4. Add a row to the README "Supported platforms" table
5. Document any platform-specific quirks in a new ADR under `docs/decisions/`

No script changes are needed — the sync engine is fully manifest-driven.
```

**REPLACE WITH exactly this block:**
```markdown
## Adding a new platform

1. Create `implementation/platforms/<name>.json` (use `cursor.json` as a template)
2. Run `make sync`
3. Verify the generated `<name>/` folder
4. Add a row to the README "Supported platforms" table
5. Document any platform-specific quirks in a new ADR under `docs/decisions/`

Most platforms are fully manifest-driven and need no script changes. If the
platform's subagent `tools` frontmatter or MCP config shape doesn't match an
existing mode in `implementation/scripts/sync.mjs` (see the `tools` and MCP
`format` branches — e.g. `claude-code` added a `"string"` tools mode and a
`"claude-code"` MCP format), add a new branch there first, as its own commit,
before writing the manifest.
```

## Edit 4 — `AGENTS.md` (root) Skill Workflow line

**FIND this exact line (occurs exactly once):**
```markdown
MUST check applicable skills in the active platform projection (`.github/skills/`, `.cursor/skills/`, `.gemini/skills/`, `.opencode/skills/`, `.pi/skills/`) (or invoke `/discover-skills`).
```

**REPLACE WITH exactly this line:**
```markdown
MUST check applicable skills in the active platform projection (`.github/skills/`, `.cursor/skills/`, `.gemini/skills/`, `.opencode/skills/`, `.pi/skills/`, `.claude/skills/`) (or invoke `/discover-skills`).
```

## Edit 5 — `AGENTS.md` (root) Code Standards line

**FIND this exact line (occurs exactly once):**
```markdown
- See platform instruction projections: `.github/instructions/coding-standards.instructions.md`, `.cursor/rules/coding-standards.mdc`, `.gemini/instructions/coding-standards.md`, `.opencode/instructions/coding-standards.md`, `.pi/instructions/coding-standards.md`.
```

**REPLACE WITH exactly this line:**
```markdown
- See platform instruction projections: `.github/instructions/coding-standards.instructions.md`, `.cursor/rules/coding-standards.mdc`, `.gemini/instructions/coding-standards.md`, `.opencode/instructions/coding-standards.md`, `.pi/instructions/coding-standards.md`, `.claude/rules/coding-standards.md`.
```

## Edit 6 — `AGENTS.md` (root) Security line

**FIND this exact line (occurs exactly once):**
```markdown
- See platform security instruction projections: `.github/instructions/security-guidelines.instructions.md`, `.cursor/rules/security-guidelines.mdc`, `.gemini/instructions/security-guidelines.md`, `.opencode/instructions/security-guidelines.md`, `.pi/instructions/security-guidelines.md`, and `implementation/SECURITY.md`.
```

**REPLACE WITH exactly this line:**
```markdown
- See platform security instruction projections: `.github/instructions/security-guidelines.instructions.md`, `.cursor/rules/security-guidelines.mdc`, `.gemini/instructions/security-guidelines.md`, `.opencode/instructions/security-guidelines.md`, `.pi/instructions/security-guidelines.md`, `.claude/rules/security-guidelines.md`, and `implementation/SECURITY.md`.
```

## Edit 7 — `AGENTS.md` (root) Knowledge Base generated-folders line

**FIND this exact line (occurs exactly once):**
```markdown
- Per-platform folders (`.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`) are **generated** by `scripts/sync.mjs`. **Do not edit them by hand.**
```

**REPLACE WITH exactly this line:**
```markdown
- Per-platform folders (`.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`, `.claude/`) are **generated** by `scripts/sync.mjs`. **Do not edit them by hand.**
```

## Edit 8 — `AGENTS.md` (root) Knowledge Base runtime-references line

**FIND this exact line (occurs exactly once):**
```markdown
- Use the installed platform folders (`.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`) as runtime references in this target project.
```

**REPLACE WITH exactly this line:**
```markdown
- Use the installed platform folders (`.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.claude/`) as runtime references in this target project.
```

## Edit 9 — `AGENTS.md` (root) MCP Servers line

**FIND this exact line (occurs exactly once):**
```markdown
Declared in platform MCP configs (`.vscode/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`). Each server is tagged:
```

**REPLACE WITH exactly this line:**
```markdown
Declared in platform MCP configs (`.vscode/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`, `.mcp.json`). Each server is tagged:
```

## Expected outputs
- `CONTRIBUTING.md` modified with the 3 edits above.
- `AGENTS.md` (repository root) modified with the 6 edits above.

## Acceptance criteria
1. Verify command (plain `grep`, NOT `-F` — the pattern relies on BRE
   alternation `\|` and an escaped literal dot `\.`, both of which `-F`
   fixed-string mode would treat as literal backslash characters and never
   match):
   ```bash
   grep -c "claude-code\|\.claude/" CONTRIBUTING.md
   ```
   Expected output: `3` or more.
2. Verify command (plain `grep`, NOT `-F` — see note above):
   ```bash
   grep -c "\.claude/" AGENTS.md
   ```
   Expected output: `5` (edits 4-8, one `.claude/` mention each).
3. Verify command (plain `grep`, NOT `-F` — see note above):
   ```bash
   grep -c "\.mcp\.json" AGENTS.md
   ```
   Expected output: `1` or more (edit 9).
4. Verify command — `implementation/AGENTS.md` untouched:
   ```bash
   git diff --quiet implementation/AGENTS.md && echo IMPLEMENTATION_AGENTS_UNCHANGED
   ```
   Expected output: `IMPLEMENTATION_AGENTS_UNCHANGED`
5. `git status --porcelain` lists exactly two modified files:
   `CONTRIBUTING.md`, `AGENTS.md`.

## Revert rule
If any verify command fails:
```bash
git checkout -- CONTRIBUTING.md AGENTS.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
</content>
