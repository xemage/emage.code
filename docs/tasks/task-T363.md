# Task T363 — Update tests and fixtures for audited transport expectations (P030-04)

**ID:** T363
**Owner:** qa-engineer
**Priority:** P0
**Status:** done
**Depends on:** T362
**Created:** 2026-08-09
**Completed:** 2026-08-09
**Based on:** docs/plans/plan-030-mcp-remote-transport-alignment.md

## Objective
Align the test suite with the corrected, per-platform-audited remote transport expectations from
T360, so tests assert the real doc-confirmed value per platform instead of a single hardcoded
`"type": "http"` assumption everywhere (or, for `vscode`, now assert the field's presence at all).

## Context
- Phase: QA
- Search the test suite (`tests/functional/`, `tests/unit/`, `tests/performance/`) for any
  assertion referencing MCP remote-server transport shape — likely candidates include
  `tests/functional/test_platform_projections.py`, `tests/functional/test_manifests.py`, and any
  test that snapshots `.mcp.json` / `mcp.json` / `settings.json` content. Confirm the actual file
  set by grepping for `"http"`, `mcpServers`, `httpUrl`, `transport`, `context7`, `hf-mcp-server`
  across `tests/`.

## Inputs
- `docs/tasks/task-T360.md` (audit table — authoritative expected values per platform)
- Regenerated projections from T362
- Existing tests referencing `"type": "http"` or remote MCP shape

## Constraints
- Do not weaken any assertion to "avoid checking transport semantics" — if a platform's correct
  shape is more specific than before (e.g. a required field that was previously unchecked), the
  test should get stricter, not looser.
- Token budget: see T361.

## Expected Outputs
- Updated test assertions/fixtures reflecting the audited per-platform expected transport encoding.

## Acceptance Criteria
1. Every test asserting MCP remote-server shape for `cline`, `vscode`/`github`, and `gemini`
   asserts the T360-confirmed correct value (not the old stale value).
2. Every test asserting MCP remote-server shape for `claude-code`, `cursor`, `opencode` continues
   to assert their (confirmed-still-correct) existing value — no accidental change.
3. Full test suite passes: `python3 tests/run.py -v` exits 0.
4. No test was deleted or weakened to make it pass without genuinely reflecting the corrected
   generator behavior.

## Blocker Protocol
Report blockers as: type + severity + proposed mitigation. Max 2 retries.

## Execution notes

**Executed by:** qa-engineer, 2026-08-09. Only `tests/functional/test_platform_projections.py` had
transport-shape assertions; the existing `test_platform_mcp_configs_have_expected_shape` checked
key presence only, not shape — the exact coverage gap that let the stale `cline`/`vscode`/`gemini`
encodings ship undetected. Strengthened it to exact-shape assertions for `gemini`, `opencode`,
`vscode`, and added a new `test_remote_mcp_transport_shape_for_previously_uncovered_platforms`
covering `cursor`, `pi`, `cline`, and `claude-code` (all previously zero coverage). Added a
`_remote_server_urls()` helper sourcing expected URLs from `servers.yaml` rather than hardcoding
literals. Regression-detection self-verified: mutated `implementation/.cline/mcp.json` back to the
old `"type": "http"` value, reran, confirmed the new test fails with a clear diff, restored the
file. Committed as `0f64e7c`.

Full suite: 294 tests, 2 pre-existing/unrelated failures at delegation time (confirmed via `git
stash` to fail identically before this task's changes too) — both are ledger-health checks:
`test_every_active_task_has_a_plan` (T363/T365/T366/T367 not literally referenced in any
`docs/plans/*.md`) and `test_task_owners_are_real_agents` (T367's owner field
`"orchestrator, release-manager"` is multi-value, not a single recognized slug). Flagged correctly
as out of this task's scope (task-ledger edits are orchestrator-only per `AGENTS.md`).

**Orchestrator fix (immediately after, same session):** added a "Task ID Index" section to
`docs/plans/plan-030-mcp-remote-transport-alignment.md` mapping T360-T367 to their P030-0N steps
(same fix pattern as the T283 precedent for plan-014), and changed T367's ledger `Owner` to the
single valid slug `release-manager` (joint orchestrator execution is documented in the task brief
prose and in `completed-tasks.md`'s own multi-agent column format, not the active-ledger schema).
Re-ran the full suite after both fixes: `Ran 294 tests ... OK (skipped=17)` — zero failures.

**Orchestrator independent re-verification of the test diff itself:** read `git show 0f64e7c` in
full; every asserted shape matches T360's audit table exactly (gemini `httpUrl`, vscode `type:
http`, cline `type: streamableHttp`, cursor/pi `{url}` only, claude-code `type: http`, opencode
`type: remote`). No assertion was weakened.
