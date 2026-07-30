# Task T289 — Add `CLAUDE.md` pass-through guidance for installed projects

**ID:** T289
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T288
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T289;
Claude Code docs confirm: "Claude Code reads `CLAUDE.md`, not `AGENTS.md`."

## Why this task exists
Every other platform reads `AGENTS.md` (or an equivalent rendered file)
directly. Claude Code does **not** read `AGENTS.md` — it reads `CLAUDE.md`
(or `.claude/CLAUDE.md`) at the project root. Per the official Claude Code
docs, the supported bridge pattern is a `CLAUDE.md` that imports `AGENTS.md`
via `@AGENTS.md` syntax. This task adds that bridge file to the
`implementation/` tree so it gets installed by `scripts/install.sh` when the
`claude-code` platform is selected (wired in T290).

## STOP-RULES (read before touching anything)
- Confirm T288 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T289 (missing dependency)`.
- **R2** This task creates **EXACTLY ONE NEW FILE**: `implementation/CLAUDE.md`.
  Do not edit `implementation/AGENTS.md` or any other file.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `docs(claude-code): T289 add CLAUDE.md AGENTS.md import bridge`

## Objective
Create `implementation/CLAUDE.md` with this exact content:

```markdown
@AGENTS.md

## Claude Code

This project follows the emage.code multi-agent protocol defined in the
imported `AGENTS.md` above. Claude Code-specific notes:

- Subagents live in `.claude/agents/*.md` — invoke one explicitly with
  `@<agent-slug>` (e.g. `@orchestrator`, `@backend-developer`) or let Claude
  delegate automatically based on each subagent's `description`.
- Skills live in `.claude/skills/*/SKILL.md`; slash commands live in
  `.claude/commands/*.md`. Both are invoked with `/<name>`.
- Path-scoped instructions live in `.claude/rules/*.md` (frontmatter `paths:`).
- MCP servers are declared in `.mcp.json` at the project root. Set the
  required environment variables before starting a session (see
  `.mcp.json` for the `env` keys each server expects).
- Start every new project with `/new-project` or `/discover-skills`, exactly
  as with every other supported platform.
```

## Expected outputs
- `implementation/CLAUDE.md` created with the exact content above.

## Acceptance criteria
1. Verify command — file exists:
   ```bash
   test -f implementation/CLAUDE.md && echo FILE_EXISTS
   ```
   Expected output: `FILE_EXISTS`
2. Verify command — import line is the first line:
   ```bash
   head -1 implementation/CLAUDE.md
   ```
   Expected output: `@AGENTS.md`
3. Verify command — section heading present:
   ```bash
   grep -Fc "## Claude Code" implementation/CLAUDE.md
   ```
   Expected output: `1`
4. Verify command — mentions `.mcp.json` and `.claude/agents`:
   ```bash
   grep -Fc ".mcp.json" implementation/CLAUDE.md
   grep -Fc ".claude/agents" implementation/CLAUDE.md
   ```
   Expected output: `1` for each (at least; `.mcp.json` may appear twice, that
   is acceptable — the check is "at least 1", not "exactly 1").
5. `git status --porcelain` lists exactly one new file: `implementation/CLAUDE.md`.

## Revert rule
If any verify command fails:
```bash
rm -f implementation/CLAUDE.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
