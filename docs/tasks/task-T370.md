# Task T370 — Update docs describing installer MCP merge behavior

**ID:** T370
**Owner:** technical-writer
**Status:** in_review
**Priority:** P1
**Depends on:** T368
**Created:** 2026-08-09
**Completed:** —
**Based on:** docs/plans/plan-031-install-mcp-json-merge-and-repo-update.md

## Objective
Ensure repo docs accurately describe the new merge behavior for `.vscode/mcp.json` and `.mcp.json`
under `scripts/install.sh --update`, if current text describes or implies the old overwrite
behavior.

## Inputs
- T368's implementation and diff
- `README.md` ("Install" and "Supported platforms" sections)
- `CONTRIBUTING.md`

## Expected outputs
- Doc diff to `README.md`/`CONTRIBUTING.md`, OR an explicit statement in the task report (with the
  specific text checked and quoted) that no doc changes were needed.

## Acceptance criteria
1. Every doc location that currently describes `--update` behavior for platform/MCP files is
   checked.
2. If updated, doc text is accurate and specific about what merges vs. what is replaced (not vague
   "merges intelligently" language) — consistent with this repo's existing precise documentation
   style (e.g. the existing `--update` warning list in `scripts/install.sh`'s
   `validate_before_update()`).
3. Work happens on the same `bugfix/T368-install-vscode-mcp-merge` branch — never commit directly to
   `develop`.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
Checked `README.md` and `CONTRIBUTING.md` in full. Neither actively described the old overwrite
behavior (both were silent on it) — nothing needed correcting per se, but the delegate judged (and
orchestrator agreed) that documenting the real, changed behavior earns its place given a reader
following the `--update` example previously had no way to know hand-edits were unsafe. Added a
precise paragraph to `README.md` immediately after the `--update` code block, describing the merge
(unknown keys preserved recursively, generator-known keys refreshed, platform directory trees still
replaced wholesale) with a pointer to `scripts/merge-mcp-json.py`. Confirmed `install.sh`'s
`validate_before_update()` directory-replacement warning list (`.github .cursor .gemini .opencode
.pi .claude`) is still accurate as-is (it never claimed to cover the two single-file MCP configs).
Did not touch CONTRIBUTING.md (no natural home for runtime install-behavior detail there).

Technical Writer role had no Bash/git tool access this session (same gap as T356/T364) — could not
commit. Orchestrator independently reviewed the README.md diff (11 insertions, accurate and
consistent with the actual `merge-mcp-json.py` algorithm) and committed on the delegate's behalf.
Commit `1222f61` on `bugfix/T368-install-vscode-mcp-merge`.
