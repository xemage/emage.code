# Task T296 — Release docs: `docs/releases/v6.4.0.md` + version markers

**ID:** T296
**Owner:** release-manager
**Status:** done
**Priority:** P0
**Depends on:** T295
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T296;
`docs/releases/_template.md`, `docs/releases/v6.3.0.md` as structural
templates; `scripts/verify-release-docs.py` as the acceptance gate.

## Why this task exists
Per the "Documentation release contract" (`README.md` and
`docs/wiki/README.md`), no release tag may be published until: (1) a
per-release brief exists at `docs/releases/vX.Y.Z.md` with `## Install` and
`## Highlights` sections, and (2) the `Latest release: vX.Y.Z` marker is
updated in `README.md`, `docs/wiki/README.md`, and `docs/wiki/home.md`. This
task produces both, for `v6.4.0`, gated by `scripts/verify-release-docs.py`.

## STOP-RULES (read before touching anything)
- Confirm T295 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T296 (missing dependency)`.
- **R2** This task touches **EXACTLY FOUR FILES**: creates
  `docs/releases/v6.4.0.md`; edits `README.md`, `docs/wiki/README.md`,
  `docs/wiki/home.md` (marker bump only — do not re-touch the platform tables
  edited in T292).
- Do NOT create the git tag in this task — that is T297.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `docs: T296 add v6.4.0 release brief and bump version markers`

## Edit 1 — create `docs/releases/v6.4.0.md`

Create with this exact content:

```markdown
# v6.4.0

Latest release: v6.4.0

## Install

Choose your platform:

| Platform | Command |
|----------|---------|
| GitHub Copilot | `scripts/install.sh --target <dir> --platform github` |
| Cursor | `scripts/install.sh --target <dir> --platform cursor` |
| Gemini CLI | `scripts/install.sh --target <dir> --platform gemini` |
| Opencode | `scripts/install.sh --target <dir> --platform opencode` |
| Pi | `scripts/install.sh --target <dir> --platform pi` |
| Claude Code | `scripts/install.sh --target <dir> --platform claude-code` |
| All platforms | `scripts/install.sh --target <dir> --platform all` |

Update an existing install: add `--update` flag.

## Highlights

**Plan 015 — Add Claude Code as a Supported Platform** (T285–T297): Claude
Code (Anthropic's CLI coding agent) joins Cursor, GitHub Copilot, Gemini CLI,
Opencode, and Pi as a sixth platform projected automatically from the
canonical `implementation/knowledge/` tree.

- **Two new sync-engine capabilities** (T285–T286): `implementation/scripts/sync.mjs`
  gained a `tools: "string"` subagent frontmatter mode (comma-separated tool
  list, Claude Code's native convention) and a `"claude-code"` MCP output
  format (`.mcp.json` at the project root, with explicit `"type": "http"` for
  remote servers).
- **New platform manifest and projection** (T287–T288): `implementation/platforms/claude-code.json`
  projects agents to `.claude/agents/`, commands to `.claude/commands/`,
  instructions to `.claude/rules/` (the `applyTo` → `paths` rename), and
  skills to `.claude/skills/`, exactly like the five existing platforms.
- **`CLAUDE.md` bridge file** (T289): Claude Code reads `CLAUDE.md`, not
  `AGENTS.md` — `implementation/CLAUDE.md` imports `AGENTS.md` via `@AGENTS.md`
  and documents Claude Code-specific invocation conventions (`@agent-name`
  subagents, `/command` skills, `.claude/rules/` path-scoped instructions).
- **Installer and AGENTS.md rewrite support** (T290–T291): `scripts/install.sh
  --platform claude-code` installs `.claude/`, `.mcp.json`, and `CLAUDE.md`;
  `scripts/render_installed_agents.py` rewrites `AGENTS.md` platform
  references for Claude Code the same way it already does for the other five
  platforms.
- **Docs and test coverage** (T292–T295): README, wiki quick-start,
  CONTRIBUTING, and root AGENTS.md now list Claude Code alongside the other
  platforms; the functional test suite gained Claude Code-specific assertions
  for the `tools: string` shape, the `.mcp.json` shape, and installer path
  rewriting, and the full validation/test gate was re-run clean.

## Breaking changes

None.

## Internal

- `implementation/scripts/sync.mjs`'s "no script changes needed to add a
  platform" claim (README, CONTRIBUTING) was corrected: most platforms are
  manifest-only, but a platform whose `tools`/MCP shape doesn't match an
  existing engine mode needs a new branch added first, as this platform did.
```

## Edit 2 — bump `README.md` marker

**FIND this exact line (occurs exactly once):**
```markdown
Latest release: v6.3.0
```

**REPLACE WITH exactly this line:**
```markdown
Latest release: v6.4.0
```

## Edit 3 — bump `docs/wiki/README.md` marker

**FIND this exact line (occurs exactly once — line 6, do NOT touch the
`vX.Y.Z` placeholder later in the same file):**
```markdown
Latest release: v6.3.0
```

**REPLACE WITH exactly this line:**
```markdown
Latest release: v6.4.0
```

## Edit 4 — bump `docs/wiki/home.md` marker and platform-list mention

**FIND this exact block (occurs exactly once):**
```markdown
Latest release: v6.3.0

## What is emage.code?

emage.code projects a single canonical knowledge base into the major AI coding assistants (GitHub Copilot, Gemini CLI, Opencode, Cursor, Pi) so that every assistant runs the *same* dev team with the *same* protocols.
```

**REPLACE WITH exactly this block:**
```markdown
Latest release: v6.4.0

## What is emage.code?

emage.code projects a single canonical knowledge base into the major AI coding assistants (GitHub Copilot, Gemini CLI, Opencode, Cursor, Pi, Claude Code) so that every assistant runs the *same* dev team with the *same* protocols.
```

## Expected outputs
- `docs/releases/v6.4.0.md` created with the exact content in Edit 1.
- `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md` each have their
  marker bumped to `Latest release: v6.4.0`.

## Acceptance criteria
1. Verify command:
   ```bash
   test -f docs/releases/v6.4.0.md && echo RELEASE_BRIEF_EXISTS
   ```
   Expected output: `RELEASE_BRIEF_EXISTS`
2. Verify command — each marker file updated:
   ```bash
   grep -Fc "Latest release: v6.4.0" README.md docs/wiki/README.md docs/wiki/home.md docs/releases/v6.4.0.md
   ```
   Expected output: `README.md:1`, `docs/wiki/README.md:1`,
   `docs/wiki/home.md:1`, `docs/releases/v6.4.0.md:1`.
3. Verify command — no file still references the old marker:
   ```bash
   grep -Fc "Latest release: v6.3.0" README.md docs/wiki/README.md docs/wiki/home.md
   ```
   Expected output: `0` for all three.
4. **This is the real gate — must pass exactly as CI runs it:**
   ```bash
   python3 scripts/verify-release-docs.py --tag v6.4.0
   ```
   Expected output ends with `release-docs-verify: all documentation checks passed`
   and exit code `0`. If it fails, read the printed error lines — they name
   the exact missing file, marker, section, or broken link — and fix only
   that, re-running the command until clean.
5. `git status --porcelain` lists exactly: one new file
   (`docs/releases/v6.4.0.md`) and three modified files (`README.md`,
   `docs/wiki/README.md`, `docs/wiki/home.md`).

## Revert rule
If any verify command fails:
```bash
rm -f docs/releases/v6.4.0.md
git checkout -- README.md docs/wiki/README.md docs/wiki/home.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
</content>
