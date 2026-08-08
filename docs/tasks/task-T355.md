# Task T355 — Update Install Script for Cline

**ID:** T355
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Depends on:** T354
**Created:** 2026-08-08
**Based on:** `docs/plans/plan-028-cline-platform-integration.md` §0.5; `scripts/install.sh`, `Makefile`

## Objective
Add `cline` to `scripts/install.sh`'s platform allowlist and `Makefile`'s install target so
`scripts/install.sh --target <dir> --platform cline` and `make install TARGET=<dir> PLATFORM=cline`
work, matching the existing pattern used by all 6 current platforms.

## Context
- Phase: Implementation (plan-028, step 4 of 6).
- **`scripts/install.sh`'s `--platform` handling is a hardcoded allowlist, not auto-discovered** —
  unlike `sync.mjs`, which reads `implementation/platforms/*.json` at runtime. You must edit three
  specific places; there is no single config to change.
- No existing platform (`cursor`, `github`, `gemini`, `opencode`, `pi`, `claude-code`) prints a
  platform-specific post-install message — they all share the same generic "Installed emage.code
  ($PLATFORM) into $TARGET" + "Next: configure MCP env vars..." lines at the end of the script. Do
  **not** add a special-cased `echo` block for Cline; that would be inconsistent with every other
  platform and isn't needed — the "copy `cline_mcp_settings.json` to Cline's settings dir" instruction
  belongs in `docs/wiki/cline-setup.md` (T356's job), not in the installer's stdout.

## Inputs
- `scripts/install.sh` — read the full file before editing, at minimum the three locations below
- `Makefile` — the `install:` target and its usage/help text

## Constraints
- Do not touch `implementation/platforms/cline.json` or `implementation/scripts/sync.mjs` — those are
  done (T352/T353).
- Do not add a Cline-specific echo/print block (see Context above).
- Token budget: ≤ 15k.

## Expected Outputs
Three exact edits to `scripts/install.sh`:

**1. Usage text (near line 16)** — add `cline` to the pipe-separated list:
```
  --platform <name>    cursor | github | gemini | opencode | pi | claude-code | cline | all (default: all)
```

**2. New function**, placed alongside the existing `install_cursor()` / `install_github()` /
`install_pi()` / `install_claude_code()` functions (~line 255-281 currently), following the same
`install_tree_into` pattern used by every other platform:
```bash
install_cline() {
  install_tree_into "$IMPLEMENTATION/.cline" "$TARGET/.cline"
  run cp "$IMPLEMENTATION/.clinerules" "$TARGET/.clinerules"
}
```

**3. `case "$PLATFORM" in` block (~line 283)** — add one line to the named-platform cases, and add
`install_cline` to the `all)` case's function-call list:
```bash
  cline) install_common; install_cline ;;
```
And inside the existing `all)` block, add `install_cline` alongside the other 6 `install_*` calls.

**4. `Makefile`** — update the `install:` target's usage/help text (the line listing valid `PLATFORM`
values) to include `cline` in the same pipe-separated list style as the other platforms.

**5. `README.md`** — add a `cline` row to whichever table maps `--platform` values to platform names
(the one near the platform-support table, listing e.g. `Cursor | cursor`, `Claude Code |
claude-code`) — row: `Cline | cline`.

## Acceptance Criteria
- [ ] `scripts/install.sh` usage text includes `cline` in the platform list
- [ ] `install_cline()` function added, matching the exact pattern of the other 6 `install_*`
      functions (uses `install_tree_into`, copies `.clinerules`)
- [ ] `case "$PLATFORM" in` has a `cline)` arm and `install_cline` is called from the `all)` arm
- [ ] `bash -n scripts/install.sh` (syntax check) exits 0
- [ ] `scripts/install.sh --target /tmp/emage-cline-test --platform cline` exits 0 and produces
      `/tmp/emage-cline-test/.cline/` and `/tmp/emage-cline-test/.clinerules` (clean up the temp
      target afterward; do not leave it behind)
- [ ] `scripts/install.sh --target /tmp/emage-all-test --platform all` still exits 0 and includes
      `.cline/` alongside all 6 pre-existing platform trees (clean up afterward)
- [ ] `Makefile`'s install-target help text includes `cline`
- [ ] `README.md`'s `--platform` value table has a `Cline | cline` row
- [ ] No Cline-specific post-install `echo`/print block added (see Context — intentionally out of
      scope for this task)
- [ ] Task brief updated with an `## Outcome` section

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. If
`IMPLEMENTATION/.cline` (the generated output T354 validated) is missing or empty when this task
starts, that's a `dependency` blocker of `critical` severity — do not proceed by installing an empty
directory.
