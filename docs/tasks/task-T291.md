# Task T291 — scripts/render_installed_agents.py: add `claude-code` mapping

**ID:** T291
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T290
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T291

## Why this task exists
`scripts/render_installed_agents.py` rewrites the generic `AGENTS.md` platform
references (skills dir, coding-standards path, security-guidelines path, MCP
config path) into platform-specific paths at install time. It has a
`PLATFORM_MAP` dict keyed by platform name and an `argparse` `choices` list.
Without a `claude-code` entry, `install_agents_doc()` (called by
`install_common()`, which every platform branch — including
`install_claude_code()` from T290 — invokes) would crash with
`ValueError: unsupported platform for AGENTS rewrite: claude-code`.

## STOP-RULES (read before touching anything)
- Confirm T290 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T291 (missing dependency)`.
- **R2** This task touches **EXACTLY ONE FILE**: `scripts/render_installed_agents.py`
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `feat(install): T291 add claude-code AGENTS.md rewrite mapping`

## Edit 1 — add `claude-code` entry to `PLATFORM_MAP`

**FIND this exact block (occurs exactly once):**
```python
    "pi": {
        "skills": ".pi/skills/",
        "standards": ".pi/instructions/coding-standards.md",
        "security": ".pi/instructions/security-guidelines.md",
        "mcp": ".pi/mcp.json",
    },
}
```

**REPLACE WITH exactly this block:**
```python
    "pi": {
        "skills": ".pi/skills/",
        "standards": ".pi/instructions/coding-standards.md",
        "security": ".pi/instructions/security-guidelines.md",
        "mcp": ".pi/mcp.json",
    },
    "claude-code": {
        "skills": ".claude/skills/",
        "standards": ".claude/rules/coding-standards.md",
        "security": ".claude/rules/security-guidelines.md",
        "mcp": ".mcp.json",
    },
}
```

## Edit 2 — extend the `platform == "all"` reference strings

**FIND this exact block (occurs exactly once):**
```python
    if platform == "all":
        skills_ref = (
            "MUST check applicable skills in the active platform projection "
            "(`.github/skills/`, `.cursor/skills/`, `.gemini/skills/`, "
            "`.opencode/skills/`, `.pi/skills/`) "
            "(or invoke `/discover-skills`)."
        )
        code_ref = (
            "- See platform instruction projections: "
            "`.github/instructions/coding-standards.instructions.md`, "
            "`.cursor/rules/coding-standards.mdc`, "
            "`.gemini/instructions/coding-standards.md`, "
            "`.opencode/instructions/coding-standards.md`, "
            "`.pi/instructions/coding-standards.md`."
        )
        sec_ref = (
            "- See platform security instruction projections: "
            "`.github/instructions/security-guidelines.instructions.md`, "
            "`.cursor/rules/security-guidelines.mdc`, "
            "`.gemini/instructions/security-guidelines.md`, "
            "`.opencode/instructions/security-guidelines.md`, "
            "`.pi/instructions/security-guidelines.md`, and `implementation/SECURITY.md`."
        )
        readme_ref = (
            "- Use the installed platform folders (`.github/`, `.cursor/`, `.gemini/`, "
            "`.opencode/`, `.pi/`) as runtime references in this target project."
        )
        mcp_ref = (
            "Declared in platform MCP configs "
            "(`.vscode/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, "
            "`.opencode/opencode.json`, `.pi/mcp.json`). Each server is tagged:"
        )
```

**REPLACE WITH exactly this block:**
```python
    if platform == "all":
        skills_ref = (
            "MUST check applicable skills in the active platform projection "
            "(`.github/skills/`, `.cursor/skills/`, `.gemini/skills/`, "
            "`.opencode/skills/`, `.pi/skills/`, `.claude/skills/`) "
            "(or invoke `/discover-skills`)."
        )
        code_ref = (
            "- See platform instruction projections: "
            "`.github/instructions/coding-standards.instructions.md`, "
            "`.cursor/rules/coding-standards.mdc`, "
            "`.gemini/instructions/coding-standards.md`, "
            "`.opencode/instructions/coding-standards.md`, "
            "`.pi/instructions/coding-standards.md`, "
            "`.claude/rules/coding-standards.md`."
        )
        sec_ref = (
            "- See platform security instruction projections: "
            "`.github/instructions/security-guidelines.instructions.md`, "
            "`.cursor/rules/security-guidelines.mdc`, "
            "`.gemini/instructions/security-guidelines.md`, "
            "`.opencode/instructions/security-guidelines.md`, "
            "`.pi/instructions/security-guidelines.md`, "
            "`.claude/rules/security-guidelines.md`, and `implementation/SECURITY.md`."
        )
        readme_ref = (
            "- Use the installed platform folders (`.github/`, `.cursor/`, `.gemini/`, "
            "`.opencode/`, `.pi/`, `.claude/`) as runtime references in this target project."
        )
        mcp_ref = (
            "Declared in platform MCP configs "
            "(`.vscode/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, "
            "`.opencode/opencode.json`, `.pi/mcp.json`, `.mcp.json`). Each server is tagged:"
        )
```

## Edit 3 — `argparse` `choices` list

**FIND this exact line (occurs exactly once):**
```python
    parser.add_argument("--platform", required=True, choices=["github", "cursor", "gemini", "opencode", "pi", "all"])
```

**REPLACE WITH exactly this line:**
```python
    parser.add_argument("--platform", required=True, choices=["github", "cursor", "gemini", "opencode", "pi", "claude-code", "all"])
```

## Expected outputs
- `scripts/render_installed_agents.py` modified with the 3 edits above.

## Acceptance criteria
1. Syntax check:
   ```bash
   python3 -m py_compile scripts/render_installed_agents.py
   ```
   Expected: no output, exit code `0`.
2. Verify command:
   ```bash
   grep -Fc '"claude-code": {' scripts/render_installed_agents.py
   ```
   Expected output: `1`
3. Verify command:
   ```bash
   grep -Fc '"claude-code", "all"' scripts/render_installed_agents.py
   ```
   Expected output: `1`
4. Functional check — render for `claude-code` succeeds and produces the
   expected path rewrites:
   ```bash
   python3 scripts/render_installed_agents.py \
     --source implementation/AGENTS.md \
     --dest /tmp/emage-t291-AGENTS.md \
     --platform claude-code
   grep -Fc ".claude/skills/" /tmp/emage-t291-AGENTS.md
   grep -Fc ".claude/rules/coding-standards.md" /tmp/emage-t291-AGENTS.md
   grep -Fc ".claude/rules/security-guidelines.md" /tmp/emage-t291-AGENTS.md
   grep -Fc ".mcp.json" /tmp/emage-t291-AGENTS.md
   rm -f /tmp/emage-t291-AGENTS.md
   ```
   Expected: each `grep -Fc` prints `1` or more, no Python traceback.
5. Regression check — `all` platform render still succeeds and includes the
   new claude-code refs:
   ```bash
   python3 scripts/render_installed_agents.py \
     --source implementation/AGENTS.md \
     --dest /tmp/emage-t291-AGENTS-all.md \
     --platform all
   grep -Fc "\`.claude/skills/\`" /tmp/emage-t291-AGENTS-all.md
   rm -f /tmp/emage-t291-AGENTS-all.md
   ```
   Expected output: `1`
6. **Real end-to-end functional check** (both T290 and T291 are now in place,
   so this is the first point where a live install actually works):
   ```bash
   rm -rf /tmp/emage-t291-e2e
   bash scripts/install.sh --target /tmp/emage-t291-e2e --platform claude-code
   test -d /tmp/emage-t291-e2e/.claude/agents && echo CLAUDE_AGENTS_OK
   test -f /tmp/emage-t291-e2e/.mcp.json && echo MCP_OK
   test -f /tmp/emage-t291-e2e/CLAUDE.md && echo CLAUDE_MD_OK
   test -f /tmp/emage-t291-e2e/AGENTS.md && echo AGENTS_MD_OK
   grep -Fc ".claude/skills/" /tmp/emage-t291-e2e/AGENTS.md
   rm -rf /tmp/emage-t291-e2e
   ```
   Expected: `CLAUDE_AGENTS_OK`, `MCP_OK`, `CLAUDE_MD_OK`, `AGENTS_MD_OK`, then
   a `grep -Fc` count of `1` or more — in that order.
7. `git status --porcelain` lists exactly one modified file:
   `scripts/render_installed_agents.py`.

## Revert rule
If any verify command fails:
```bash
git checkout -- scripts/render_installed_agents.py
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
</content>
