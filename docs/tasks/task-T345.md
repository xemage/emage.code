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
- [ ] `blob_oid` correctly extracted from the exact real example format cited in T316's BUG-E
- [ ] Non-matching prose does not raise, returns dict unmodified
- [ ] Already-JSON responses unaffected (no regression to existing unwrap behavior)
- [ ] Full local test suite green
- [ ] No other file changed
- [ ] Landed via `bugfix/345-blob-oid-extraction → develop` MR — opened, not self-merged

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalating.
