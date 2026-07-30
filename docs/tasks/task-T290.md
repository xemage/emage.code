# Task T290 — scripts/install.sh: add `claude-code` platform

**ID:** T290
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T289
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T290

## Why this task exists
`scripts/install.sh` is the installer used by every downstream project. It has
one `install_<platform>()` function per platform plus a `case` dispatch. With
`implementation/.claude/`, `implementation/.mcp.json` (T288), and
`implementation/CLAUDE.md` (T289) now present, the installer needs a matching
`install_claude_code()` function and dispatch wiring, or `--platform
claude-code` will fail with `error: unknown platform 'claude-code'`.

Note the **`CLAUDE.md` root-file requirement**: unlike other platforms, Claude
Code does not read `AGENTS.md` directly — it reads `CLAUDE.md` at the project
root (T289's bridge file, which itself does `@AGENTS.md`). If
`install_claude_code()` only copies `.claude/` and `.mcp.json` and forgets
`CLAUDE.md`, the installed project would be silently broken for Claude Code
users (no project instructions loaded at all). Do not skip that copy.

## STOP-RULES (read before touching anything)
- Confirm T289 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T290 (missing dependency)`.
- **R2** This task touches **EXACTLY TWO FILES**: `scripts/install.sh` and
  `Makefile`. Do not edit any other file.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `feat(install): T290 add claude-code platform support`

## Edit 1 — `scripts/install.sh` usage text

**FIND this exact line (occurs exactly once):**
```
  --platform <name>    cursor | github | gemini | opencode | pi | all (default: all)
```

**REPLACE WITH exactly this line:**
```
  --platform <name>    cursor | github | gemini | opencode | pi | claude-code | all (default: all)
```

## Edit 2 — `scripts/install.sh` `validate_before_update` directory list

**FIND this exact line (occurs exactly once):**
```bash
    for d in .github .cursor .gemini .opencode .pi; do
```

**REPLACE WITH exactly this line:**
```bash
    for d in .github .cursor .gemini .opencode .pi .claude; do
```

## Edit 3 — `scripts/install.sh` add `install_claude_code()` function

**FIND this exact block (occurs exactly once):**
```bash
install_pi() {
  install_tree_into "$IMPLEMENTATION/.pi" "$TARGET/.pi"
}
```

**REPLACE WITH exactly this block:**
```bash
install_pi() {
  install_tree_into "$IMPLEMENTATION/.pi" "$TARGET/.pi"
}

install_claude_code() {
  install_tree_into "$IMPLEMENTATION/.claude" "$TARGET/.claude"
  run cp "$IMPLEMENTATION/.mcp.json" "$TARGET/.mcp.json"
  run cp "$IMPLEMENTATION/CLAUDE.md" "$TARGET/CLAUDE.md"
}
```

## Edit 4 — `scripts/install.sh` dispatch `case` statement

**FIND this exact block (occurs exactly once):**
```bash
case "$PLATFORM" in
  cursor) install_common; install_cursor ;;
  github) install_common; install_github ;;
  gemini) install_common; install_gemini ;;
  opencode) install_common; install_opencode ;;
  pi) install_common; install_pi ;;
  all)
    install_common
    install_cursor
    install_github
    install_gemini
    install_opencode
    install_pi
    ;;
  *)
    echo "error: unknown platform '$PLATFORM'" >&2
    exit 1
    ;;
esac
```

**REPLACE WITH exactly this block:**
```bash
case "$PLATFORM" in
  cursor) install_common; install_cursor ;;
  github) install_common; install_github ;;
  gemini) install_common; install_gemini ;;
  opencode) install_common; install_opencode ;;
  pi) install_common; install_pi ;;
  claude-code) install_common; install_claude_code ;;
  all)
    install_common
    install_cursor
    install_github
    install_gemini
    install_opencode
    install_pi
    install_claude_code
    ;;
  *)
    echo "error: unknown platform '$PLATFORM'" >&2
    exit 1
    ;;
esac
```

## Edit 5 — `Makefile` usage string

**FIND this exact line (occurs exactly once):**
```
	@test -n "$(TARGET)" || (echo "Usage: make install TARGET=<dir> [PLATFORM=all|cursor|github|gemini|opencode|pi]" && exit 1)
```

**REPLACE WITH exactly this line:**
```
	@test -n "$(TARGET)" || (echo "Usage: make install TARGET=<dir> [PLATFORM=all|cursor|github|gemini|opencode|pi|claude-code]" && exit 1)
```

## Expected outputs
- `scripts/install.sh` modified with the 4 edits above.
- `Makefile` modified with the 1 edit above.

## Acceptance criteria
1. Syntax check:
   ```bash
   bash -n scripts/install.sh
   ```
   Expected: no output, exit code `0`.
2. Verify command (counts matching *lines*, not occurrences — Edit 1's usage
   line and Edit 4's `claude-code)` case label are the only two lines
   containing the literal hyphenated substring `claude-code`; Edit 2 uses
   `.claude` and Edit 3/4's function name uses `install_claude_code`, neither
   of which contains a hyphen):
   ```bash
   grep -Fc "claude-code" scripts/install.sh
   ```
   Expected output: `2`.
3. Verify command:
   ```bash
   grep -Fc 'cp "$IMPLEMENTATION/CLAUDE.md" "$TARGET/CLAUDE.md"' scripts/install.sh
   ```
   Expected output: `1`
4. Verify command:
   ```bash
   grep -Fc "claude-code" Makefile
   ```
   Expected output: `1`
5. Dry-run check — dispatch reaches `install_claude_code()` and queues the
   right copy operations. **Use `--dry-run`, not a real install**:
   `install_common()` → `install_agents_doc()` calls
   `scripts/render_installed_agents.py --platform claude-code`, which does
   not accept `claude-code` until T291 lands (T291 depends on T290, so it is
   not done yet). Under `--dry-run`, `install.sh`'s `run()` helper only
   `echo`s each command instead of executing it — so `render_installed_agents.py`
   is never actually invoked, and this check is safe to run before T291
   exists. The real end-to-end install (files actually landing on disk) is
   verified once both halves exist — see T291 acceptance criterion 4 and
   T294's installer tests.
   ```bash
   rm -rf /tmp/emage-t290-check
   bash scripts/install.sh --target /tmp/emage-t290-check --platform claude-code --dry-run | tee /tmp/emage-t290-dryrun.log
   grep -Fc "/.claude" /tmp/emage-t290-dryrun.log
   grep -Fc "/.mcp.json" /tmp/emage-t290-dryrun.log
   grep -Fc "/CLAUDE.md" /tmp/emage-t290-dryrun.log
   grep -Fc -- "--platform claude-code" /tmp/emage-t290-dryrun.log
   rm -rf /tmp/emage-t290-check /tmp/emage-t290-dryrun.log
   ```
   Expected: each of the 4 `grep -Fc` commands prints `1` or more.
6. Dry-run check — `--platform all` still queues claude-code's copy too:
   ```bash
   rm -rf /tmp/emage-t290-all-check
   bash scripts/install.sh --target /tmp/emage-t290-all-check --platform all --dry-run | tee /tmp/emage-t290-all-dryrun.log
   grep -Fc "/.claude" /tmp/emage-t290-all-dryrun.log
   rm -rf /tmp/emage-t290-all-check /tmp/emage-t290-all-dryrun.log
   ```
   Expected: `grep -Fc` prints `1` or more.
7. `git status --porcelain` lists exactly two modified files:
   `scripts/install.sh`, `Makefile`.

## Revert rule
If any verify command fails:
```bash
git checkout -- scripts/install.sh Makefile
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
</content>
