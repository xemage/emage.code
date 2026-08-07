# Task T314 — Fix MCP tool-result envelope unwrapping in CwsoMcpClient/CwsoClient

**ID:** T314
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** — (blocks T214)
**Created:** 2026-08-02
**Completed:** 2026-08-02
**Based on:** `docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md` (Wave 5, T214),
live probe by orchestrator + independent confirmation by the coordinating/supervising session
(both against the real CWSO stack, `deploy/docker-compose-t226.yml`, 2026-08-02).

## Objective

Fix a real, reproducible bug in this repo's own CWSO client code: `CwsoMcpClient.call_tool()` and
`CwsoMcpClient.list_tools()` (`implementation/runtime/cwso/mcp_client.py`) return the raw JSON-RPC
`result` object unmodified. Against the real, live CWSO MCP server, every `tools/call` result is
wrapped in the standard MCP tool-result envelope `{"content": [{"type": "text", "text":
"<json-encoded-payload>"}]}` — the actual payload (e.g. `workspace_uuid`, `blob_oid`, `commit_oid`,
`tree_oid`) is a JSON string nested inside `content[0].text`, not a top-level key. Because neither
`CwsoMcpClient` nor `CwsoClient` (`implementation/runtime/cwso/client.py`) ever unwraps this
envelope, every one of `CwsoClient`'s typed wrapper methods
(`create_shadow_workspace`/`write_shadow_file`/`read_shadow_file`/`commit_shadow`/
`drop_shadow_workspace`/`query_ast`/`merge_concurrent_results`/etc.) silently returns the wrong
shape against the real server — the documented return keys are never present at the top level.
This was never caught by the existing unit test suite (`tests/unit/test_cwso_client.py`,
`tests/unit/test_cwso_concurrent_merge.py`, 55 passed) because those tests mock
`CwsoMcpClient`/`call_tool` to return already-flattened dicts directly, hiding the real server's
actual response shape. This blocks T214 (Pattern A live integration test), which needs every typed
accessor to work against the real live endpoint.

## Inputs

- `implementation/runtime/cwso/mcp_client.py` (`call_tool`, `list_tools`, `rpc`)
- `implementation/runtime/cwso/client.py` (all typed wrapper methods, via `call_tool`)
- Live-confirmed evidence (both independently, by orchestrator and by the coordinating session):
  ```
  client.create_shadow_workspace() ->
  {"content": [{"type": "text", "text": "{\"workspace_uuid\":\"<uuid>\",\"base_tree_oid\":null}"}]}
  ```
- `tests/unit/test_cwso_client.py`, `tests/unit/test_cwso_concurrent_merge.py` (existing, mocked —
  do not break; these must keep passing)
- `tests/functional/test_cwso_client_live.py` (existing live-gated test scaffold, currently asserts
  flat keys like `workspace_uuid` directly on the result — this test module documents the
  *intended* contract that the fix must actually satisfy)

## Expected outputs

- Fixed `implementation/runtime/cwso/mcp_client.py`: `call_tool()` (and, if applicable,
  `list_tools()`) unwraps the standard MCP envelope — when the JSON-RPC `result` dict has a
  `content` key whose value is a list of `{"type": "text", "text": "<json>"}` items, parse
  `content[0]["text"]` as JSON and return that parsed dict as the effective result. Include a
  **defensive fallback**: if `result` does NOT match this envelope shape (e.g. a future server
  version returns an already-flat dict, or `content[0].text` is not valid JSON), return `result`
  unmodified rather than raising — do not make the client more fragile than it already is.
- No changes required to `implementation/runtime/cwso/client.py`'s typed wrappers themselves if the
  fix is made at the `mcp_client.py` transport layer (preferred — keeps the unwrap logic in one
  place). If you judge the fix belongs in `client.py` instead, justify why in your response before
  proceeding.
- Existing unit tests (`test_cwso_client.py`, `test_cwso_concurrent_merge.py`) must still pass
  unmodified (they mock at the `CwsoMcpClient`/`call_tool` boundary with already-flat dicts — the
  new unwrap logic must not double-unwrap or otherwise break that mocking contract; if it does,
  the mocks may need a one-line adjustment to also return an enveloped shape, but do not weaken any
  assertion to make this pass artificially).
- A new unit test (in `tests/unit/test_cwso_client.py` or a new
  `tests/unit/test_cwso_mcp_client_envelope.py`) that asserts, with a mocked HTTP transport, that a
  `tools/call` JSON-RPC result shaped as
  `{"content": [{"type": "text", "text": "{\"workspace_uuid\": \"abc\"}"}]}` is correctly unwrapped
  to `{"workspace_uuid": "abc"}` by `CwsoMcpClient.call_tool()`, AND that an already-flat result
  (no `content` key) passes through unchanged (defensive-fallback case).
- Real, live re-verification against the actual running CWSO stack
  (`deploy/docker-compose-t226.yml`, currently healthy) using the `CWSO_JWT_SECRET` environment
  variable (already set in this session — do NOT read `../CWSO/.env.jwt.dev` or any `.env*` file;
  `CwsoClient.from_env()` picks up `CWSO_JWT_SECRET` automatically): call
  `create_shadow_workspace()` for real and confirm the returned dict now has a top-level
  `workspace_uuid` key (not nested under `content`), then `drop_shadow_workspace()` it to clean up
  (this tool call is expected to work normally — an earlier apparent block on it did not reproduce
  for the coordinating session and should not be treated as a standing restriction).

## Acceptance criteria

1. `python3 -m pytest tests/unit/test_cwso_client.py tests/unit/test_cwso_concurrent_merge.py tests/unit/test_ast_conflict_check.py -q` → still all passing (55+ new envelope test), paste literal output.
2. New unit test for envelope unwrap + defensive fallback passes, paste literal output.
3. Live re-verification: real `create_shadow_workspace()` call against the live stack returns a
   dict with a top-level `workspace_uuid` (paste the actual returned dict, real UUID visible), and
   the corresponding `drop_shadow_workspace()` call succeeds (paste actual response). Leave no
   orphaned workspace behind — always drop what you create in this task's verification.
4. `docker ps --filter "name=cwso-"` unchanged before/after (paste both) — the live stack must not
   be disturbed by this task's verification.
5. No changes outside `implementation/runtime/cwso/mcp_client.py`, `implementation/runtime/cwso/client.py` (only if justified per Expected Outputs), and the new/updated test file(s).

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Merge ownership (binding for this task)

Do NOT run `git push`, do NOT open a merge request, do NOT run any `glab mr merge`/merge command.
Work on the current branch (`bugfix/t314-mcp-envelope-unwrap`, already checked out), commit
locally, and stop. The orchestrator pushes, opens the MR, polls CI, and merges personally.

## Execution notes

Executed 2026-08-02 by backend-developer subagent (delegated by orchestrator); fix and evidence
independently re-verified by the orchestrator directly against the live CWSO stack before ledger
completion. Branch: `bugfix/t314-mcp-envelope-unwrap`.

### Root cause and fix
`CwsoMcpClient.call_tool()` (`implementation/runtime/cwso/mcp_client.py`) returned the raw
JSON-RPC `result` object unmodified. The real, live CWSO MCP server wraps every `tools/call`
result in the standard MCP envelope `{"content": [{"type": "text", "text":
"<json-encoded-payload>"}]}` — confirmed independently by the orchestrator, by the coordinating
session, and reproduced again by backend-developer. Fix: added
`CwsoMcpClient._unwrap_tool_result()` (static helper), wired into `call_tool()`, which parses
`content[0]["text"]` as JSON and returns that as the effective result, with a defensive fallback
(returns `result` unmodified) if the shape doesn't match — no top-level `content` key, `content`
not a non-empty list, first item not `{"type": "text", ...}`, `text` not valid JSON, or parsed JSON
not a dict. `list_tools()` was empirically confirmed to NOT use the envelope (`tools/list` returns
flat `{"tools": [...]}` already) and was correctly left unchanged. No changes to `client.py` were
needed — existing mocked unit tests patch at the `CwsoMcpClient.call_tool` boundary directly, so
they never exercised the real transport body and remained valid unmodified.

### Unit test verification (backend-developer, confirmed again independently by orchestrator)
```
$ python3 -m pytest tests/unit/test_cwso_client.py tests/unit/test_cwso_concurrent_merge.py tests/unit/test_ast_conflict_check.py tests/unit/test_cwso_mcp_client_envelope.py -q
...........................................................              [100%]
59 passed in 0.23s
```
New envelope-unwrap tests (4, in `tests/unit/test_cwso_mcp_client_envelope.py`) cover: unwrap of a
real-shaped envelope, pass-through when already flat, pass-through when `content` isn't a list,
pass-through when `content[0].text` isn't valid JSON.

### Live re-verification (orchestrator's own independent run, 2026-08-02)
```
$ docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"   # before
NAMES               STATUS
cwso-rollout        Up 13 hours (healthy)
cwso-orchestrator   Up 13 hours (healthy)
cwso-git-shadow     Up 13 hours
cwso-merge-engine   Up 13 hours
cwso-sia-executor   Up 13 hours

$ python3 <verify script using CwsoClient.from_env()-equivalent construction with CWSO_JWT_SECRET>
create_result_keys: ['base_tree_oid', 'workspace_uuid']
workspace_uuid: 198adb71-5b6c-4df7-9e04-3fcebeba5268
drop_result: {"dropped": true}
ORCHESTRATOR_INDEPENDENT_VERIFICATION_OK

$ docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"   # after — identical
NAMES               STATUS
cwso-rollout        Up 13 hours (healthy)
cwso-orchestrator   Up 13 hours (healthy)
cwso-git-shadow     Up 13 hours
cwso-merge-engine   Up 13 hours
cwso-sia-executor   Up 13 hours
```
`create_shadow_workspace()` now returns a top-level `workspace_uuid` (no `content` envelope);
`drop_shadow_workspace()` succeeded normally with no classifier block reproducing for either
backend-developer or the orchestrator — the single earlier apparent block (during initial
orchestrator probing, pre-T314) is confirmed a one-off, not a standing restriction, consistent
with the coordinating session's own 3x direct test.

### Disposition
Fix implemented with defensive fallback; 59/59 unit tests pass (55 pre-existing + 4 new); live
round-trip proven with real UUIDs, no orphaned workspace; live stack undisturbed throughout.
Scope: `implementation/runtime/cwso/mcp_client.py` + `tests/unit/test_cwso_mcp_client_envelope.py`
only — no `client.py` changes needed.

Commit on branch `bugfix/t314-mcp-envelope-unwrap`:
- `dd76891` — `fix(t314): unwrap MCP tool-result envelope in CwsoMcpClient.call_tool`

**Status: done. Completed: 2026-08-02.**
