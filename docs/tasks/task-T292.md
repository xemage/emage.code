# Task T292 — Update README.md and docs/wiki/quick-start.md platform tables

**ID:** T292
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T291
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T292

## Why this task exists
`README.md` and `docs/wiki/quick-start.md` both list every supported platform
in tables (output folder/format, and `--platform` install value). These are
user-facing docs, not generated — they must be hand-updated to mention
`claude-code` now that it is installable (T290/T291 done).

## STOP-RULES (read before touching anything)
- Confirm T291 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T292 (missing dependency)`.
- **R2** This task touches **EXACTLY TWO FILES**: `README.md`,
  `docs/wiki/quick-start.md`. Do not touch `CONTRIBUTING.md` or `AGENTS.md`
  (those are T293) and do not bump the `Latest release:` version marker (that
  is T296, done at release-cut time).
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `docs: T292 add claude-code to platform tables`

## Edit 1 — `README.md` "Supported platforms" table + the "no script changes" claim

**FIND this exact block (occurs exactly once):**
```markdown
| Platform | Output folder | Format |
|----------|---------------|--------|
| GitHub Copilot (VS Code) | `.github/` + `.vscode/mcp.json` | `.agent.md`, `.prompt.md`, `.instructions.md` |
| Gemini CLI | `.gemini/` | `.md` (no `tools` field), `settings.json` with hooks |
| Opencode | `.opencode/` | `.md` (object `tools`), `opencode.json` |
| Cursor | `.cursor/` | `.mdc`, `applyTo` → `globs`, `mcp.json` |
| Pi | `.pi/` | agents, prompts, instructions, skills (`.md`) |

Adding a new platform = adding a `platforms/<name>.json` manifest under
`implementation/`. No script changes required.
```

**REPLACE WITH exactly this block:**
```markdown
| Platform | Output folder | Format |
|----------|---------------|--------|
| GitHub Copilot (VS Code) | `.github/` + `.vscode/mcp.json` | `.agent.md`, `.prompt.md`, `.instructions.md` |
| Gemini CLI | `.gemini/` | `.md` (no `tools` field), `settings.json` with hooks |
| Opencode | `.opencode/` | `.md` (object `tools`), `opencode.json` |
| Cursor | `.cursor/` | `.mdc`, `applyTo` → `globs`, `mcp.json` |
| Pi | `.pi/` | agents, prompts, instructions, skills (`.md`) |
| Claude Code | `.claude/` + `.mcp.json` | `.md` (string `tools`), subagents + skills + rules |

Adding a new platform = adding a `platforms/<name>.json` manifest under
`implementation/`. Usually no script changes are required; add a new
`tools`/MCP format branch to `sync.mjs` only if the platform's frontmatter or
MCP shape doesn't match an existing mode (see `implementation/scripts/sync.mjs`).
```

## Edit 2 — `README.md` install `--platform` value table

**FIND this exact block (occurs exactly once):**
```markdown
| Platform | `--platform` value |
|----------|-------------------|
| Cursor | `cursor` |
| GitHub Copilot (VS Code) | `github` |
| Gemini CLI | `gemini` |
| Opencode | `opencode` |
| Pi | `pi` |
| All platforms | `all` |
```

**REPLACE WITH exactly this block:**
```markdown
| Platform | `--platform` value |
|----------|-------------------|
| Cursor | `cursor` |
| GitHub Copilot (VS Code) | `github` |
| Gemini CLI | `gemini` |
| Opencode | `opencode` |
| Pi | `pi` |
| Claude Code | `claude-code` |
| All platforms | `all` |
```

## Edit 3 — `docs/wiki/quick-start.md` install `--platform` value table

**FIND this exact block (occurs exactly once):**
```markdown
| Platform | `--platform` value |
|----------|------------------|
| Cursor | `cursor` |
| GitHub Copilot (VS Code) | `github` |
| Gemini CLI | `gemini` |
| Opencode | `opencode` |
| Pi | `pi` |
| All platforms | `all` |
```

**REPLACE WITH exactly this block:**
```markdown
| Platform | `--platform` value |
|----------|------------------|
| Cursor | `cursor` |
| GitHub Copilot (VS Code) | `github` |
| Gemini CLI | `gemini` |
| Opencode | `opencode` |
| Pi | `pi` |
| Claude Code | `claude-code` |
| All platforms | `all` |
```

## Edit 4 — `docs/wiki/quick-start.md` manual-copy table

**FIND this exact block (occurs exactly once):**
```markdown
| Platform | What to copy from `implementation/` |
|----------|-------------------------------------|
| GitHub Copilot | `.github/` + `.vscode/mcp.json` |
| Gemini CLI | `.gemini/` |
| Opencode | `.opencode/` |
| Cursor | `.cursor/` |
| Pi | `.pi/` |

Plus always: `AGENTS.md` and `docs/`.
```

**REPLACE WITH exactly this block:**
```markdown
| Platform | What to copy from `implementation/` |
|----------|-------------------------------------|
| GitHub Copilot | `.github/` + `.vscode/mcp.json` |
| Gemini CLI | `.gemini/` |
| Opencode | `.opencode/` |
| Cursor | `.cursor/` |
| Pi | `.pi/` |
| Claude Code | `.claude/` + `.mcp.json` + `CLAUDE.md` |

Plus always: `AGENTS.md` and `docs/`.
```

## Edit 5 — `docs/wiki/quick-start.md` troubleshooting line

**FIND this exact line (occurs exactly once):**
```markdown
- **Agents not loading?** Confirm format: `.mdc` (Cursor), `.agent.md` (Copilot), `.md` (Gemini/Opencode/Pi).
```

**REPLACE WITH exactly this line:**
```markdown
- **Agents not loading?** Confirm format: `.mdc` (Cursor), `.agent.md` (Copilot), `.md` (Gemini/Opencode/Pi/Claude Code).
```

## Expected outputs
- `README.md` modified with the 2 edits above.
- `docs/wiki/quick-start.md` modified with the 3 edits above.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -Fc "Claude Code" README.md
   ```
   Expected output: `2` or more.
2. Verify command:
   ```bash
   grep -Fc "claude-code" README.md
   ```
   Expected output: `1` or more.
3. Verify command:
   ```bash
   grep -Fc "Claude Code" docs/wiki/quick-start.md
   ```
   Expected output: `2` or more.
4. Verify command:
   ```bash
   grep -Fc "claude-code" docs/wiki/quick-start.md
   ```
   Expected output: `1` or more.
5. Verify command — version marker was NOT touched by this task:
   ```bash
   grep -Fc "Latest release: v6.3.0" README.md
   ```
   Expected output: `1`
6. Local link check (mirrors CI `markdown-links` job):
   ```bash
   python3 - <<'PY'
   import re
   for f in ("README.md", "docs/wiki/quick-start.md"):
       text = open(f, encoding="utf-8").read()
       print(f, "OK" if text.count("|") % 2 == 0 or True else "TABLE_MALFORMED")
   PY
   ```
   (Sanity only — a human/agent should visually confirm both tables render as
   valid Markdown tables with consistent column counts.)
7. `git status --porcelain` lists exactly two modified files:
   `README.md`, `docs/wiki/quick-start.md`.

## Revert rule
If any verify command fails:
```bash
git checkout -- README.md docs/wiki/quick-start.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
</content>
