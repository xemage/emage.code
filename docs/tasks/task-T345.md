# Task T345 — Fix BUG-E: best-effort blob_oid extraction from write_shadow_file's prose response

**ID:** T345
**Owner:** backend-developer
**Status:** pending
**Priority:** P2
**Depends on:** —
**Created:** 2026-08-08
**Based on:** `docs/tasks/task-T316.md` BUG-E, `docs/plans/plan-023-t316-pattern-a-cleanup.md`
§ 3.3 (design decision — already made, this task is implementation)

## Objective
`CwsoClient.write_shadow_file()`'s docstring claims the response has a `blob_oid` key, but the
real server returns non-JSON prose (e.g. `"wrote 32 bytes (blob 77a8c908...)"`) for this specific
call, so `_unwrap_tool_result`'s JSON-unwrap correctly leaves it enveloped and `blob_oid` is never
actually present. Add a best-effort regex extraction so the documented key becomes real without
waiting on a CWSO-side response-shape change.

## Context
- Phase: Implementation
- Design already decided in plan-023 § 3.3 — implement it, don't re-derive it: apply
  `re.search(r"blob\s+([0-9a-f]+)", text)` (or equivalent) only when the response is still prose
  after the normal unwrap (i.e., exactly BUG-E's observed case). If it matches, add `blob_oid` to
  the returned dict. If it doesn't match, return the dict unmodified — **never raise** for this;
  it's a best-effort convenience, not a validation gate.
- Nothing downstream in `concurrent_merge.py` currently reads `blob_oid` from this specific call
  (confirmed in plan-023 § 2) — this fix has no other call sites to update, it's contained to
  `client.py`.

## Inputs
- `implementation/runtime/cwso/client.py:459-470` (`write_shadow_file` method + docstring)
- `implementation/runtime/cwso/mcp_client.py:186-214` (`_unwrap_tool_result` — read-only
  reference, do not edit; this task adds extraction logic in `client.py`, not here)
- `docs/tasks/task-T316.md` BUG-E — the exact real prose response example
  (`"wrote 32 bytes (blob 77a8c908...)"`)

## Constraints
- Scope is `write_shadow_file` only — do not touch `_unwrap_tool_result` itself or any other
  client method.
- Never raise on extraction failure — fail open (return the dict unmodified), matching this
  file's existing defensive-fallback philosophy.
- Token budget: ≤ 30k.
- Land via a branch + MR to `develop` (branch: `bugfix/345-blob-oid-extraction`) — no direct
  commit to `develop`.

## Expected Outputs
- `write_shadow_file` (or a small private helper it calls) extracting `blob_oid` from prose
  responses on a best-effort basis.
- Regression tests covering: (a) a prose response matching the real observed format → `blob_oid`
  populated correctly; (b) a prose response that doesn't match the expected pattern →
  `blob_oid` absent, no raise, dict otherwise unchanged; (c) a response that's already valid JSON
  (future server version) → unaffected, existing unwrap behavior unchanged.
- Task brief updated with an `## Outcome` section.

## Acceptance Criteria
- [x] `blob_oid` correctly extracted from the exact real example format cited in T316's BUG-E
- [x] Non-matching prose does not raise, returns dict unmodified
- [x] Already-JSON responses unaffected (no regression to existing unwrap behavior)
- [x] Full local test suite green
- [x] No other file changed
- [x] Landed via `bugfix/345-blob-oid-extraction → develop` MR — opened, not self-merged

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalating.

## Outcome

**Architecture/design version referenced:** `docs/plans/plan-023-t316-pattern-a-cleanup.md` § 3.3
(design decision consumed as-is, not re-derived).

### Files changed
- `implementation/runtime/cwso/client.py` — added `_BLOB_OID_PATTERN` module constant, a
  `CwsoClient._extract_blob_oid` static helper, and wired it into `write_shadow_file` (docstring
  updated to describe the best-effort behavior instead of unconditionally promising `blob_oid`).
- `tests/unit/test_cwso_client.py` — 3 new regression tests added to `TestCwsoClientTypedWrappers`:
  `test_write_shadow_file_extracts_blob_oid_from_real_prose_format`,
  `test_write_shadow_file_non_matching_prose_does_not_raise`,
  `test_write_shadow_file_already_json_unaffected`.

No other file touched (confirmed via `git diff --stat`).

### Extraction logic (exact)
```python
_BLOB_OID_PATTERN = re.compile(r"blob\s+([0-9a-f]+)")

@staticmethod
def _extract_blob_oid(response: dict[str, Any]) -> dict[str, Any]:
    content = response.get("content")
    if not isinstance(content, list) or not content:
        return response

    first_item = content[0]
    if not isinstance(first_item, dict):
        return response

    text = first_item.get("text")
    if not isinstance(text, str):
        return response

    match = _BLOB_OID_PATTERN.search(text)
    if not match:
        return response

    return {**response, "blob_oid": match.group(1)}
```
Called from `write_shadow_file` on the result of `self.call_tool(...)`. Only triggers on the
still-enveloped shape (`{"content": [{"type": "text", "text": ...}]}`) that `_unwrap_tool_result`
leaves untouched when `text` isn't valid JSON — i.e. exactly BUG-E's case. Never raises; any
unexpected shape or non-matching prose returns `response` unmodified.

### Test results
- `python3 -m pytest tests/unit/test_cwso_client.py -v` — 37 passed (34 pre-existing + 3 new).
- `python3 -m pytest tests/unit -q` — 118 passed.
- `python3 tests/run.py` (the CI `unit-tests` job's actual command; functional + performance
  suites, 16 live/network tests self-skip as expected) — first run: 293 tests, 1 failure
  (`test_scaling_and_throughput_envelope`, a timing/coefficient-of-variation performance
  assertion unrelated to this change — confirmed pre-existing/environmental by rerunning it in
  isolation, `python3 -m pytest tests/performance/test_scaling_and_throughput.py -q` → 1 passed).
  Second full `tests/run.py` rerun: `Ran 293 tests in 73.169s / OK (skipped=16)` — clean.
- `git status --short` / `git diff --stat` confirm only `implementation/runtime/cwso/client.py`
  and `tests/unit/test_cwso_client.py` changed.

### Branch / MR
- Branch: `bugfix/345-blob-oid-extraction`, pushed to `origin`.
- MR opened to `develop`, not self-merged — awaiting orchestrator review per task constraint.

### Assumptions / decisions
- Followed plan-023 § 3.3's exact regex verbatim (`re.search(r"blob\s+([0-9a-f]+)", text)`,
  compiled as a module-level constant for reuse/testability rather than inlined).
- Placed the extraction as a private static helper on `CwsoClient` rather than in `mcp_client.py`,
  per the task's explicit scope constraint (`_unwrap_tool_result` itself untouched).
- Merged the extracted `blob_oid` into a **new** dict (`{**response, "blob_oid": ...}`) rather than
  mutating `response` in place, to avoid any risk of aliasing surprises for callers that might hold
  a reference to the original envelope dict.

### Blocker status
None.
