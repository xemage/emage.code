# Task T355 v2 — Update Install Script for Cline (corrected format)

**ID:** T355
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Depends on:** T354
**Created:** 2026-08-08 (revised 2026-08-09 for corrected Cline format)
**Based on:** `docs/plans/plan-028-cline-platform-integration-v2.md` §2; `scripts/install.sh`, `Makefile`

## Objective
Add `cline` to `scripts/install.sh`'s platform allowlist and `Makefile`'s install target, copying
**both** `.cline/` (skills + MCP staging file) and the root-level `.clinerules/` directory into the
target project — not a single `.clinerules` dotfile (that was v1's design, now dropped).

## Context
- Phase: Implementation (plan-028-v2, step 4 of 6).
- `scripts/install.sh`'s `--platform` handling is a hardcoded allowlist, not auto-discovered. Three
  specific edits, same locations as v1's brief described, but the `install_cline()` body differs:
  copying a directory (`.clinerules/`) rather than a single file.
- No existing platform prints a platform-specific post-install message; do not add one for Cline
  either (see v1's brief for the same reasoning — still applies).

## Inputs
- `scripts/install.sh` — read the full file before editing, at minimum: usage text (~line 16),
  `install_tree_into()` (~line 141) and an existing `install_<platform>()` function (~line 255) for
  the pattern, the `case "$PLATFORM" in` block (~line 283)
- `Makefile` — the `install:` target's usage/help text

## Constraints
- Do not touch `implementation/platforms/cline.json` or `implementation/scripts/sync.mjs`.
- Do not add a Cline-specific echo/print block.
- Token budget: ≤ 15k.

## Expected Outputs
Three edits to `scripts/install.sh`, plus `Makefile` and `README.md` updates:

**1. Usage text** — add `cline` to the pipe-separated platform list.

**2. New function**, alongside the other `install_<platform>()` functions, copying **two** trees
(both via the existing `install_tree_into()` helper — no new copy mechanism needed since
`.clinerules/` is a plain directory, same shape as any other generated tree):
```bash
install_cline() {
  install_tree_into "$IMPLEMENTATION/.cline" "$TARGET/.cline"
  install_tree_into "$IMPLEMENTATION/.clinerules" "$TARGET/.clinerules"
}
```

**3. `case "$PLATFORM" in` block** — add:
```bash
  cline) install_common; install_cline ;;
```
and add `install_cline` to the `all)` arm's call list alongside the other 6.

**4. `Makefile`** — add `cline` to the install-target's usage/help text, matching the existing style.

**5. `README.md`** — add a `Cline | cline` row to the `--platform` value table (near the "Install"
section).

## Acceptance Criteria
- [ ] `scripts/install.sh` usage text includes `cline`
- [ ] `install_cline()` added, using `install_tree_into` for **both** `$IMPLEMENTATION/.cline` and
      `$IMPLEMENTATION/.clinerules` (two calls, not one)
- [ ] `case "$PLATFORM" in` has a `cline)` arm; `install_cline` is called from the `all)` arm
- [ ] `bash -n scripts/install.sh` exits 0
- [ ] `scripts/install.sh --target /tmp/emage-cline-test --platform cline` exits 0 and produces both
      `/tmp/emage-cline-test/.cline/` and `/tmp/emage-cline-test/.clinerules/` (clean up afterward)
- [ ] `scripts/install.sh --target /tmp/emage-all-test --platform all` still exits 0, includes both
      `.cline/` and `.clinerules/` alongside the 6 pre-existing platform trees (clean up afterward)
- [ ] `Makefile` install-target help text includes `cline`
- [ ] `README.md`'s `--platform` value table has a `Cline | cline` row
- [ ] No Cline-specific post-install echo/print block added
- [ ] Task brief updated with an `## Outcome` section

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. If
`$IMPLEMENTATION/.clinerules` or `$IMPLEMENTATION/.cline` is missing or empty when this task starts,
that's a `dependency` blocker of `critical` severity — do not install an empty/missing tree.

## Outcome

**Status:** done

Verified `implementation/.cline/` (skills + `mcp.json` + `.generated-manifest.json`) and
`implementation/.clinerules/` (4 rule files) were populated on `develop` before starting — no
dependency blocker.

Implemented all three `scripts/install.sh` edits, the `Makefile` help-text edit, and the
`README.md` `--platform` value table row exactly as specified in Expected Outputs.

**Deviation from brief (reported, not a blocker):** the brief's file scope (`scripts/install.sh`,
`Makefile`, `README.md`) omitted `scripts/render_installed_agents.py`, which `install_common()` →
`install_agents_doc()` invokes with `--platform "$PLATFORM"` and which hard-validates `$PLATFORM`
against an argparse `choices` list plus a `PLATFORM_MAP` dict — neither of which included `cline`.
Without touching this file, `scripts/install.sh --target ... --platform cline` fails at the
`install_common` step before ever reaching `install_cline()`, which would have made the brief's own
acceptance criteria un-satisfiable. Added a `cline` entry to `PLATFORM_MAP` (mirroring the
`claude-code` entry's shape: `.cline/skills/`, `.clinerules/coding-standards.md`,
`.clinerules/security-guidelines.md`, `.cline/mcp.json`) and added `"cline"` to the `--platform`
argparse `choices` list. This file is not one of the two files the brief explicitly forbade touching
(`implementation/platforms/cline.json`, `implementation/scripts/sync.mjs`).

## Acceptance Criteria — Verified

- [x] `scripts/install.sh` usage text includes `cline`
- [x] `install_cline()` added, using `install_tree_into` for both `$IMPLEMENTATION/.cline` and
      `$IMPLEMENTATION/.clinerules` (two calls)
- [x] `case "$PLATFORM" in` has a `cline)` arm; `install_cline` is called from the `all)` arm
- [x] `bash -n scripts/install.sh` exits 0
- [x] `scripts/install.sh --target /tmp/emage-cline-test --platform cline` exits 0, produces both
      `.cline/` and `.clinerules/` under the target (temp dir removed after verification)
- [x] `scripts/install.sh --target /tmp/emage-all-test --platform all` exits 0, includes both
      `.cline/` and `.clinerules/` alongside the 6 pre-existing platform trees (temp dir removed
      after verification)
- [x] `Makefile` install-target help text includes `cline`
- [x] `README.md`'s `--platform` value table has a `Cline | cline` row
- [x] No Cline-specific post-install echo/print block added (verified via grep)
- [x] Task brief updated with this `## Outcome` section

## Artifacts Produced
- `scripts/install.sh` (edited)
- `Makefile` (edited)
- `README.md` (edited)
- `scripts/render_installed_agents.py` (edited — deviation, see above)
- `docs/tasks/task-T355.md` (this file, `## Outcome` section added)
