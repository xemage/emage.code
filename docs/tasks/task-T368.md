# Task T368 — Implement JSON merge path for `.vscode/mcp.json` and `.mcp.json`

**ID:** T368
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-09
**Completed:** 2026-08-09
**Based on:** docs/plans/plan-031-install-mcp-json-merge-and-repo-update.md

## Objective
`scripts/install.sh` currently does a plain `cp` overwrite of `.vscode/mcp.json` (in
`install_github()`, ~line 262) and `.mcp.json` (in `install_claude_code()`, ~line 279), even in
`--update` mode. This clobbers any pre-existing target-only keys. This repo's own root
`.vscode/mcp.json` already carries a hand-added `cwso` server entry and `inputs` block with no
generator source, which a naive re-copy or `--update` run would silently delete — confirmed already
sidestepped manually in `docs/tasks/task-T362.md`. Implement a JSON-key-preserving merge path for
both files, invoked only in `--update` mode when the destination file already exists.

## Inputs
- `scripts/install.sh` (`install_github`, `install_claude_code`, `merge_tree_preserve_existing`,
  `merge_task_docs`, `install_tree_into` for the existing update-mode-branching pattern)
- `implementation/scripts/sync.mjs` (`emitMcp()` — read the `vscode` and `claude-code`/`cline`
  format branches to confirm exact output shape before writing merge code)
- `.vscode/mcp.json` (repo root — has hand-added `cwso` + `inputs`, ground truth for the
  regression this fix must prevent)
- `.mcp.json` (repo root — audit against `implementation/.mcp.json` for any hand-added content
  before concluding whether the same fix is needed there)
- `docs/plans/plan-031-install-mcp-json-merge-and-repo-update.md` (Approach section — algorithm
  already specified: recursive merge, source wins on shared keys, dest-only keys at any level
  preserved)

## Expected outputs
- `scripts/merge-mcp-json.py` (new helper, following the existing convention of dedicated Python
  helpers for structured merges, e.g. `scripts/merge-task-docs.py`)
- `scripts/install.sh` diff wiring the helper into `install_github()`/`install_claude_code()` for
  `--update` mode only (fresh installs keep the plain copy)

## Acceptance criteria
1. Fresh (non-`--update`) install of `github` or `claude-code` platform still does a plain copy —
   unchanged behavior.
2. `--update` install of either platform merges: any pre-existing destination key not present in
   generated source is preserved (including nested keys inside `servers`/`mcpServers`, e.g. a
   synthetic unknown server entry, and top-level keys like `inputs`); every generator-sourced key is
   present and current afterward (overwritten/added from source).
3. No literal secret value is ever written by the merge logic — verify the merge script never reads
   or inlines real env var values; only placeholder syntax (`${input:...}`/`${env:...}`) may appear.
4. `.mcp.json` gets the same class of fix applied, or the task report states explicitly (with
   evidence — e.g. a byte-diff against `implementation/.mcp.json`) why it isn't needed today, without
   leaving that code path structurally different from `.vscode/mcp.json`'s in a way that would
   silently reintroduce the same bug if someone later hand-edits root `.mcp.json`.
5. No unrelated refactor of `install.sh`.
6. Work happens on a `bugfix/T368-install-vscode-mcp-merge` branch off `develop` (per
   `git-workflow.md`) — never commit directly to `develop`.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
Implemented `scripts/merge-mcp-json.py`: recursive merge, shared dict keys recurse, source wins on
scalar/array leaf conflicts, dest-only keys preserved at any nesting level, source-only keys added.
Never reads/interpolates env vars — placeholders pass through untouched. Wired into
`scripts/install.sh` via new `merge_or_copy_mcp_json()` helper, applied symmetrically to
`install_github()` (`.vscode/mcp.json`) and `install_claude_code()` (`.mcp.json`); falls back to
plain `cp` on fresh install or when dest doesn't exist yet.

`.mcp.json` audit: `diff .mcp.json implementation/.mcp.json` in the worktree produced zero output —
root `.mcp.json` is currently byte-identical to generator output, no hand-added content today. Only
`.vscode/mcp.json` has live drift (`cwso` block + `inputs` array, missing `context7.type`). The same
merge code path was still applied to `.mcp.json` so the overwrite risk doesn't quietly persist there.

Orchestrator independently re-verified: ran `bash -n scripts/install.sh` and
`python3 -m py_compile scripts/merge-mcp-json.py` (both clean); performed an independent smoke test
(fresh `github` install into a temp dir, injected a synthetic `cwso` entry + `inputs` block +
stripped `context7.type`, ran `--update`, confirmed `cwso`/`inputs` survived and `context7` picked up
`"type": "http"`). Diff scope confirmed minimal: only `scripts/install.sh` (+22/-2) and the new
`scripts/merge-mcp-json.py` (+82) touched. Commit `fe289b4` on
`bugfix/T368-install-vscode-mcp-merge`.
