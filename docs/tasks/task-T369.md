# Task T369 — Add test coverage for MCP JSON merge behavior

**ID:** T369
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T368
**Created:** 2026-08-09
**Completed:** 2026-08-09
**Based on:** docs/plans/plan-031-install-mcp-json-merge-and-repo-update.md

## Objective
Prove T368's JSON merge behavior with automated tests, including the exact regression this plan
exists to prevent: an unknown pre-existing server key in `.vscode/mcp.json`/`.mcp.json` must survive
an `scripts/install.sh --update` run, while all generator-known keys still get added/updated
correctly.

## Inputs
- T368's implementation (`scripts/merge-mcp-json.py`, updated `scripts/install.sh`)
- `tests/functional/test_install_script.py` (existing test style/pattern to extend — see
  `test_update_preserves_merged_docs`, `test_claude_code_install_places_root_files` for precedent)

## Expected outputs
- New or extended test(s) in `tests/functional/` (extending `test_install_script.py` or a new
  sibling module, consistent with existing file organization)

## Acceptance criteria
1. A test creates a target `.vscode/mcp.json` (or `.mcp.json`) with a synthetic unknown server key
   (e.g. `"my-custom-server"`), runs `install.sh --update --platform github` (or `claude-code`), and
   asserts the unknown key is still present in the output afterward.
2. A test asserts all current generator-known server keys for that platform's MCP file (context7,
   hf-mcp-server if applicable, gitlab, playwright, fetch, memory, sequential-thinking, brave, etc.)
   are present and match the generated content after `--update`.
3. A test covers the fresh-install (non-`--update`) case still doing a plain copy.
4. Full suite (`python3 tests/run.py`) green with the new tests included.
5. No existing test is weakened to make new tests pass.
6. Work happens on the same `bugfix/T368-install-vscode-mcp-merge` branch (stacked on T368's work,
   per the atomicity precedent in `docs/tasks/completed-tasks.md` T353/T354) — never commit directly
   to `develop`.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
Added 5 new test methods to `tests/functional/test_install_script.py`:
`test_fresh_install_plain_copies_mcp_json` (byte-identical baseline for both `github`/`claude-code`
fresh installs — closes a content-check gap the existing `test_claude_code_install_places_root_files`
didn't cover), `test_update_preserves_unknown_mcp_server_key_github`/`_claude_code` (inject a
synthetic unknown server key + top-level `inputs` block, run `--update`, assert survival),
`test_update_refreshes_generator_known_mcp_keys_github`/`_claude_code` (corrupt `context7` to a
stale URL, run `--update`, assert it now matches `implementation/.vscode/mcp.json` /
`implementation/.mcp.json`'s live `context7` entry exactly — proving genuine refresh, not a no-op).
All synthetic values are non-secret placeholders (`https://example.invalid/mcp`, `fake_token`).

Full suite: 281 tests, OK (skipped=17). Orchestrator independently re-ran
`python3 tests/run.py --suite functional` and confirmed the same result, and read the full test diff
(180 insertions, test-file-only). Commit `0475264` on `bugfix/T368-install-vscode-mcp-merge`.
