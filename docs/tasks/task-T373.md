# Task T373 — Fix hardcoded platform list in `render_installed_agents.py`'s `all` branch

**ID:** T373
**Owner:** devops-engineer
**Status:** pending
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-09
**Based on:** docs/plans/plan-032-render-agents-cline-platform-map-fix.md (P032-01)

This brief is self-contained. You do not need to read plan-032 or any other task brief to execute
this task.

## Objective
`scripts/render_installed_agents.py` rewrites platform-specific reference strings into the
`AGENTS.md` file it installs into a target project. Its `render()` function has two code paths for
this: a per-platform branch that correctly looks up every path from the `PLATFORM_MAP` dict, and a
`platform == "all"` branch that instead hardcodes six platforms' paths as string literals — `cline`
(added to `PLATFORM_MAP` in v6.8.0) was never added to these five literals, so every
`--platform all` install/update silently omits Cline from the rendered `AGENTS.md`'s "Skill
Workflow", "Code Standards", "Security", "Knowledge Base", and "MCP Servers" sections, even though
`cline`'s actual `.cline/`/`.clinerules/` directories install correctly via a separate code path.
Fix the `all` branch to derive these five strings from `PLATFORM_MAP` instead of hardcoded
literals, so `cline` (and any future platform added to `PLATFORM_MAP`) is included automatically
with no further edit needed here.

## Inputs (exact paths, verified against the current file — re-verify if anything below doesn't
match what you see; see Blocker protocol)
The ONLY file you will edit: `/home/emage/Code/emage/emage.code/scripts/render_installed_agents.py`

Structure of that file as of this brief's authoring (line numbers are exact — if they don't match,
STOP, see Blocker protocol):
- `PLATFORM_MAP` dict: **lines 11-54**. Contains 7 entries in this order: `github`, `cursor`,
  `gemini`, `opencode`, `pi`, `claude-code`, `cline`. Each entry has four string fields: `skills`,
  `standards`, `security`, `mcp`. **Read-only reference — do not edit this dict.**
- `render()` function: starts at **line 64**.
- The buggy `platform == "all"` branch (what you will replace): **lines 65-98**.
- The correct per-platform `else` branch (reference pattern, already correct, **do not modify**):
  **lines 99-110**.
- `kb_ref` (unconditional, shared by both branches, **do not modify**): **lines 112-115**.
- Five `_replace_one()` calls that consume `skills_ref`/`code_ref`/`sec_ref`/`kb_ref`/`readme_ref`/
  `mcp_ref` by name (**do not modify — variable names must stay exactly as they are**):
  **lines 117-147**.
- `main()` / argparse, including the `--platform` `choices` list at **line 155**
  (`choices=["github", "cursor", "gemini", "opencode", "pi", "claude-code", "cline", "all"]`):
  **lines 151-173**. `cline` is already a valid choice (added in T355) — nothing to change here.

The exact current buggy code at lines 65-98 (quoted verbatim — this is what you are replacing):
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
Note: all six platforms are hardcoded; `cline` is absent from all five strings, despite
`PLATFORM_MAP["cline"]` already existing correctly at lines 48-53.

## Allow-list (files you may touch)
- `scripts/render_installed_agents.py` — and within it, ONLY the body of the
  `if platform == "all":` block (lines 65-98). Nothing else in this file, and no other file.

## Deny-list (do not touch — no exceptions)
- Do NOT edit `PLATFORM_MAP` (lines 11-54) — no new entries, no field renames, no reordering.
- Do NOT edit the `else:` / per-platform branch (lines 99-110) — must remain byte-for-byte
  identical in output before and after your change.
- Do NOT edit `kb_ref` (lines 112-115) or any of the five `_replace_one()` calls (lines 117-147).
- Do NOT edit `main()` / argparse (lines 151-173).
- Do NOT edit any other file: `scripts/install.sh`, `Makefile`, `README.md`,
  `implementation/scripts/sync.mjs`, `implementation/AGENTS.md`, root `AGENTS.md`, any test file,
  any other `PLATFORM_MAP`-like manifest. Test coverage is a separate task (T374, blocked by this
  one). Root `AGENTS.md` regeneration is a separate task (T376, blocked by T375).
- Do NOT create any new file.
- Do NOT run `node implementation/scripts/sync.mjs` without `--check` — omitting `--check` WRITES
  550 files to disk. Only ever run it as
  `node implementation/scripts/sync.mjs --root implementation --check` (verify-only mode).
- Do NOT push to `develop` or `main`. Do NOT open a merge request. Do NOT merge anything. Stop
  after a local commit on your feature branch (see Git workflow below).

## Exact target behavior
Replace lines 65-98 so all five ref strings are derived by iterating `PLATFORM_MAP` (dict
insertion order: `github`, `cursor`, `gemini`, `opencode`, `pi`, `claude-code`, `cline` — this
determines platform ordering in the output, matching the existing 6-platform order with `cline`
appended last). **No platform name may appear as a string literal anywhere in the new code** —
every path segment must be read from a `PLATFORM_MAP` entry's `skills`/`standards`/`security`/
`mcp` field.

Reference implementation (produces the exact required output for all 7 current platforms — you
may implement it differently as long as the output strings under "Exact expected output" below
match byte-for-byte):
```python
    if platform == "all":
        skills_paths = [cfg["skills"] for cfg in PLATFORM_MAP.values()]
        skills_ref = (
            "MUST check applicable skills in the active platform projection ("
            + ", ".join(f"`{p}`" for p in skills_paths)
            + ") (or invoke `/discover-skills`)."
        )

        standards_paths = [cfg["standards"] for cfg in PLATFORM_MAP.values()]
        code_ref = (
            "- See platform instruction projections: "
            + ", ".join(f"`{p}`" for p in standards_paths)
            + "."
        )

        security_paths = [cfg["security"] for cfg in PLATFORM_MAP.values()]
        sec_ref = (
            "- See platform security instruction projections: "
            + ", ".join(f"`{p}`" for p in security_paths)
            + ", and `implementation/SECURITY.md`."
        )

        roots: list[str] = []
        for cfg in PLATFORM_MAP.values():
            for field in ("skills", "standards", "security"):
                root = cfg[field].split("/")[0] + "/"
                if root not in roots:
                    roots.append(root)
        readme_ref = (
            "- Use the installed platform folders ("
            + ", ".join(f"`{r}`" for r in roots)
            + ") as runtime references in this target project."
        )

        mcp_paths = [cfg["mcp"] for cfg in PLATFORM_MAP.values()]
        mcp_ref = (
            "Declared in platform MCP configs ("
            + ", ".join(f"`{p}`" for p in mcp_paths)
            + "). Each server is tagged:"
        )
```

**CRITICAL — do NOT use the `mcp` field when deriving `readme_ref`'s root-folder list.** Only
iterate `skills`, `standards`, `security` for that specific string. This was verified directly
against the current file: including `mcp` would incorrectly add a spurious `.vscode/` entry (from
`github`'s `mcp` field, `.vscode/mcp.json`) to the Knowledge-Base runtime-reference bullet — that
folder is an MCP config location, never a "platform projection root" in this bullet's existing
meaning — and `claude-code`'s `mcp` field (`.mcp.json`, a bare file at repo root with no `/`) would
produce a nonsensical `.mcp.json/` pseudo-root. Excluding `mcp` from this one derivation avoids
both problems and is the only correct approach. `mcp` IS still used for `mcp_ref` itself (a
separate string, above) — just not for `readme_ref`.

## Exact expected output (verify byte-for-byte with the test commands below)
With `--platform all`, the rendered text must contain these five exact strings (platform order
within each: github, cursor, gemini, opencode, pi, claude-code, cline):

1. **skills_ref**: `` MUST check applicable skills in the active platform projection (`.github/skills/`, `.cursor/skills/`, `.gemini/skills/`, `.opencode/skills/`, `.pi/skills/`, `.claude/skills/`, `.cline/skills/`) (or invoke `/discover-skills`). ``
2. **code_ref**: `` - See platform instruction projections: `.github/instructions/coding-standards.instructions.md`, `.cursor/rules/coding-standards.mdc`, `.gemini/instructions/coding-standards.md`, `.opencode/instructions/coding-standards.md`, `.pi/instructions/coding-standards.md`, `.claude/rules/coding-standards.md`, `.clinerules/coding-standards.md`. ``
3. **sec_ref**: `` - See platform security instruction projections: `.github/instructions/security-guidelines.instructions.md`, `.cursor/rules/security-guidelines.mdc`, `.gemini/instructions/security-guidelines.md`, `.opencode/instructions/security-guidelines.md`, `.pi/instructions/security-guidelines.md`, `.claude/rules/security-guidelines.md`, `.clinerules/security-guidelines.md`, and `implementation/SECURITY.md`. ``
4. **readme_ref**: `` - Use the installed platform folders (`.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.claude/`, `.cline/`, `.clinerules/`) as runtime references in this target project. ``
5. **mcp_ref**: `` Declared in platform MCP configs (`.vscode/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`, `.mcp.json`, `.cline/mcp.json`). Each server is tagged: ``

## Expected output (deliverable)
A git diff touching exactly one file, `scripts/render_installed_agents.py`, scoped to lines 65-98.

## Tests to run (literal commands, run from repo root `/home/emage/Code/emage/emage.code`)

1. Syntax check (after your change):
   ```
   python3 -m py_compile scripts/render_installed_agents.py
   ```
   PASS = exits 0, no output.

2. Capture BEFORE baselines — run these BEFORE you edit the file:
   ```
   mkdir -p /tmp/t373-check
   python3 scripts/render_installed_agents.py --source implementation/AGENTS.md --dest /tmp/t373-check/github-before.md --platform github
   python3 scripts/render_installed_agents.py --source implementation/AGENTS.md --dest /tmp/t373-check/cline-before.md --platform cline
   ```

3. After your change, render `all` and check Cline is present:
   ```
   python3 scripts/render_installed_agents.py --source implementation/AGENTS.md --dest /tmp/t373-check/all.md --platform all
   grep -c '\.cline/skills/' /tmp/t373-check/all.md
   grep -c '\.clinerules/coding-standards\.md' /tmp/t373-check/all.md
   grep -c '\.clinerules/security-guidelines\.md' /tmp/t373-check/all.md
   grep -c '\.cline/mcp\.json' /tmp/t373-check/all.md
   grep -c '\.clinerules/' /tmp/t373-check/all.md
   ```
   PASS = every `grep -c` prints `1`.

4. After your change, confirm the existing six platforms are still present (no regression):
   ```
   grep -c '`\.github/skills/`' /tmp/t373-check/all.md
   grep -c '`\.cursor/skills/`' /tmp/t373-check/all.md
   grep -c '`\.gemini/skills/`' /tmp/t373-check/all.md
   grep -c '`\.opencode/skills/`' /tmp/t373-check/all.md
   grep -c '`\.pi/skills/`' /tmp/t373-check/all.md
   grep -c '`\.claude/skills/`' /tmp/t373-check/all.md
   ```
   PASS = every one prints `1`.

5. After your change, prove the single-platform branch is untouched:
   ```
   python3 scripts/render_installed_agents.py --source implementation/AGENTS.md --dest /tmp/t373-check/github-after.md --platform github
   python3 scripts/render_installed_agents.py --source implementation/AGENTS.md --dest /tmp/t373-check/cline-after.md --platform cline
   diff /tmp/t373-check/github-before.md /tmp/t373-check/github-after.md
   diff /tmp/t373-check/cline-before.md /tmp/t373-check/cline-after.md
   ```
   PASS = both `diff` commands print nothing (empty diff = byte-identical).

6. Full existing test suite baseline (must still pass — current baseline as of this brief: 299
   tests, `OK (skipped=18)`, exit 0; your change must not reduce this):
   ```
   python3 tests/run.py
   ```
   PASS = exits 0. Do not investigate or fix pre-existing skips — out of scope.

## Acceptance criteria (all must be true)
- [ ] `git diff` shows changes in exactly one file: `scripts/render_installed_agents.py`.
- [ ] The five exact output strings under "Exact expected output" are present verbatim in a
      `--platform all` render.
- [ ] `diff` between pre-fix and post-fix `--platform github` output is empty; same for
      `--platform cline`.
- [ ] No platform-name string literal (`"github"`, `"cursor"`, `"gemini"`, `"opencode"`, `"pi"`,
      `"claude-code"`, `"cline"`) appears inside the lines you changed. Confirm with:
      `grep -n '"github"\|"cursor"\|"gemini"\|"opencode"\|"pi"\|"claude-code"\|"cline"' scripts/render_installed_agents.py`
      — matches inside `PLATFORM_MAP` (lines 11-54, untouched) are expected and fine; there must be
      no matches in your new lines 65-98 replacement.
- [ ] `python3 -m py_compile scripts/render_installed_agents.py` exits 0.
- [ ] `python3 tests/run.py` exits 0.

## Blocker protocol
STOP and report a blocker (do not improvise a different fix) if:
- The actual current file content doesn't match the verbatim code quoted above (line numbers
  shifted, variable names differ, `PLATFORM_MAP` entries changed) → `type: dependency`,
  `severity: major` — the brief's premise is stale and needs re-verification against `develop`'s
  current tip before proceeding.
- Any test in steps 3-5 fails after your change → `type: technical`, `severity: major`, include
  exact command output.
- `python3 tests/run.py` fails for reasons unrelated to your change → `type: technical`,
  `severity: minor` — note it, do not attempt to fix unrelated failures, proceed only if your own
  change's tests pass.
- You believe a different root-folder derivation than "skills+standards+security, excluding mcp"
  is needed → `type: unclear_requirements`, `severity: major` — do not silently deviate; this
  approach was specifically verified against this file to avoid the `.vscode/` and bare-`.mcp.json`
  edge cases documented above.

Max 2 retries before escalating to the orchestrator with full context (what was tried, exact
error/output).

## Git workflow
1. Create branch `bugfix/T373-render-agents-cline-platform-map` from the current tip of `develop`.
2. Make the change; run all tests above; confirm all pass.
3. Commit with a Conventional Commit message, e.g.:
   ```
   fix(install): derive render_installed_agents.py all-branch platform refs from PLATFORM_MAP

   The `platform == "all"` branch hardcoded six platforms' reference strings as
   literals, omitting `cline` (added in v6.8.0, T352-T357) from all five. Derive
   skills_ref/code_ref/sec_ref/readme_ref/mcp_ref from PLATFORM_MAP instead, so
   cline is included and any future platform addition needs no matching edit here.

   Refs T373
   ```
4. Do NOT push. Do NOT open a merge request. Do NOT merge to `develop` or `main`. Stop after the
   local commit and report completion (branch name, commit SHA, full test output) back to the
   orchestrator. T374 will check out this same branch and stack its own commit on top of it — do
   not delete or rename the branch.

## Constraints
- Token budget: ≤10k tokens.
- File ownership: `scripts/render_installed_agents.py` only, scoped to lines 65-98, as above.
- No unrelated refactor of this file or any other.
