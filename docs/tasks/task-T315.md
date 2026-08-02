# Task T315 — Fix AstConflictChecker/ConcurrentMergeOrchestrator live response-shape bugs (blocks T214)

**ID:** T315
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** — (blocks T214)
**Created:** 2026-08-02
**Completed:** 2026-08-02
**Based on:** `docs/tasks/task-T214.md` Execution notes (qa-engineer's first real, live run of
T214's 4 scenarios, 2026-08-02, branch `test/t214-pattern-a-live-integration`), findings
BUG-B/BUG-C/BUG-D.

## Objective

qa-engineer's first real run of T214's 4 Pattern A scenarios against the live CWSO stack (see
`docs/tasks/task-T214.md` Execution notes for full evidence) found 1 of 4 scenarios (Scenario 1)
fully passing, and 3 of 4 (Scenarios 2/3/4) failing exactly one assertion each: the AST pre-check
(`AstConflictChecker`, T213) reports `ConflictSeverity.LOW` for every file, every time, regardless
of real content — even for files with a genuine simultaneous same-symbol addition (should be
MEDIUM) or genuinely diverging function signatures (should be HIGH). Root cause, confirmed live
and pasted verbatim in task-T214.md:

- `AstConflictChecker._query_exports()` (`implementation/runtime/cwso/ast_conflict_check.py`
  ~line 120) looks for a top-level `"exports"` key. The real server's `query_ast(...,
  LIST_EXPORTS)` response is `{"hits": [{"kind": "function_definition", "name": "foo"}, ...],
  "language": ..., "query_type": ..., "target_symbol": ...}` — there is no `"exports"` key; the
  symbol names are nested inside `hits[i]["name"]`. This makes `_query_exports()` always return
  an empty set against the real server.
- `AstConflictChecker._query_signatures()` (~line 150) looks for a top-level `"signature"` key.
  The real server's `query_ast(..., EXTRACT_SIGNATURE, target_symbol=...)` response is
  `{"hits": [{"kind": "function_definition", "signature": "def foo():", "start_row": 0}],
  ...}` — the signature is nested inside `hits[i]["signature"]`, not top-level. This makes
  `_query_signatures()` always return an empty dict against the real server.
- Net effect: every `FileConflictAnalysis` has empty symbol sets and empty signature maps, so
  `_detect_conflicts()` can never detect a simultaneous add or a diverging signature — severity is
  always LOW, heuristic always `AST_SEMANTIC_ONLY`, independent of actual file content.
- Separately, `ConcurrentMergeOrchestrator._extract_conflicts()`
  (`implementation/runtime/cwso/concurrent_merge.py`) does
  `merge_response.get("unresolved_conflicts", [])`. The real server's `merge_concurrent_results`
  response has no such key; it returns `{"outcome": "conflict"|"success", "results": [{"path":...,
  "status": "merged"|"conflict", "reason_code":..., "message":...}], "conflict_count":..., ...}`.
  Any caller relying on `ConcurrentMergeResult.unresolved_conflicts` always sees an empty list even
  when the merge genuinely reports conflicts in `results`.

This blocks T214: 3 of its 4 required scenarios cannot show the documented "Pre-check severity:
MEDIUM/HIGH" acceptance criterion until this is fixed. This is exactly the "integration reveals a
bug unit tests didn't catch" risk plan-016's own risk table anticipated for T213/T212 — the
existing mocked unit tests (`tests/unit/test_ast_conflict_check.py`,
`tests/unit/test_cwso_concurrent_merge.py`) never exercise the real server's actual `query_ast`/
`merge_concurrent_results` response shapes, so they still pass (55+ green) while being blind to
this defect.

## Inputs

- `implementation/runtime/cwso/ast_conflict_check.py` (`_query_exports`, `_query_signatures`)
- `implementation/runtime/cwso/concurrent_merge.py` (`_extract_conflicts`)
- `docs/tasks/task-T214.md` Execution notes — real, pasted `query_ast` and
  `merge_concurrent_results` response shapes captured live for all 4 scenarios (use these as your
  ground truth for the real shape; do not guess)
- `tests/unit/test_ast_conflict_check.py`, `tests/unit/test_cwso_concurrent_merge.py` (existing
  mocked unit tests — must keep passing; update their mocks to reflect the real response shape if
  needed so they actually exercise the fixed code path, same pattern as T314)

## Expected outputs

- Fixed `AstConflictChecker._query_exports()`: parse the real `{"hits": [{"kind":..., "name":...},
  ...]}` shape — return the set of `hit["name"]` values for hits that represent a symbol
  definition (defensive: skip hits missing a `"name"` key; keep a fallback to the old `"exports"`
  key check in case a future/different server response ever uses that shape instead — do not
  regress the mocked-unit-test contract).
- Fixed `AstConflictChecker._query_signatures()`: parse the real `{"hits": [{"kind":...,
  "signature":..., ...}]}` shape — return `{symbol: hit["signature"]}` for the queried symbol
  (defensive: keep a fallback to the old top-level `"signature"` key check).
- Fixed `ConcurrentMergeOrchestrator._extract_conflicts()`: parse the real `{"outcome":...,
  "results": [{"path":..., "status": "conflict"|"merged", "reason_code":..., "message":...}],
  ...}` shape — build `MergeConflict(path=..., reason=...)` entries for every `results[i]` where
  `status == "conflict"`, using `message` (fall back to `reason_code` if `message` is absent) as
  `reason` (defensive: keep the old `"unresolved_conflicts"` top-level-key fallback too, in case a
  future/different server response uses that shape).
- Updated/added unit tests in `tests/unit/test_ast_conflict_check.py` and
  `tests/unit/test_cwso_concurrent_merge.py` that mock the REAL `hits`-list / `results`-list
  response shapes (not the old assumed shapes) and assert MEDIUM/HIGH severity is now correctly
  detected for a simultaneous-add case and a diverging-signature case, and that
  `_extract_conflicts()` correctly extracts conflicts from the real `results`-list shape. Keep (or
  adapt) any existing tests that exercised the old assumed shape only if they still make sense as
  defensive-fallback tests; do not delete real coverage without a reason.
- Real, live re-verification: re-run (or write an equivalent minimal live check for)
  `AstConflictChecker.run()` against the live stack for a case shaped like T214's Scenario 2
  (simultaneous same-symbol add) and confirm it now reports `ConflictSeverity.MEDIUM`
  (`FAIL_RAPIDLY_ON_CONFLICT`), and for a case shaped like Scenario 3 (diverging signatures)
  confirm it now reports `ConflictSeverity.HIGH`. Use `CwsoClient.from_env()` (role="worker" for
  workspace/AST calls, per T214's confirmed role matrix — do NOT read any `.env*` file,
  `CWSO_JWT_SECRET` is already set in the environment). Drop every workspace you create. Paste the
  real, live `PreCheckResult` (severity, summary) as evidence.

## Acceptance criteria

1. `python3 -m pytest tests/unit/test_ast_conflict_check.py tests/unit/test_cwso_concurrent_merge.py tests/unit/test_cwso_client.py -q` → all passing, paste literal output (should be ≥55, plus your new/updated tests).
2. Live re-verification: real `AstConflictChecker.run()` call against the live stack for a
   simultaneous-same-symbol-add file reports `overall_severity=medium`; for a diverging-signature
   file reports `overall_severity=high`. Paste the real, live `PreCheckResult` output for both.
3. `docker ps --filter "name=cwso-"` unchanged before/after your live verification (paste both).
4. No workspace left orphaned by your verification (paste `drop_shadow_workspace` confirmations).
5. Changes scoped to `implementation/runtime/cwso/ast_conflict_check.py`,
   `implementation/runtime/cwso/concurrent_merge.py`, and the two unit test files — nothing else.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Merge ownership (binding for this task)

Do NOT run `git push`, do NOT open a merge request, do NOT run any `glab mr merge`/merge command.
Work on the current branch (`bugfix/t315-ast-precheck-live-response-shape`, already checked out),
commit locally, and stop. The orchestrator pushes, opens the MR, polls CI, and merges personally.

## Execution notes

Executed 2026-08-02 by backend-developer subagent (delegated by orchestrator); fix and evidence
independently re-verified by the orchestrator directly against the live CWSO stack before ledger
completion. Branch: `bugfix/t315-ast-precheck-live-response-shape`.

### Fixes applied
1. `AstConflictChecker._query_exports()` — now parses the real `{"hits": [{"kind":...,
   "name":...}, ...]}` shape (returns `{hit["name"] for hit in hits if "name" in hit}`), with a
   defensive fallback to the old top-level `"exports"` key.
2. `AstConflictChecker._query_signatures()` — new `_extract_signature()` helper parses the real
   `{"hits": [{"kind":..., "signature":...}]}` shape, with a defensive fallback to the old
   top-level `"signature"` key.
3. `ConcurrentMergeOrchestrator._extract_conflicts()` — now parses the real `{"outcome":...,
   "results": [{"path":..., "status": "conflict"|"merged", "reason_code":..., "message":...}],
   ...}` shape via new `_extract_conflicts_from_results()`, with a defensive fallback to the old
   `"unresolved_conflicts"` shape via `_extract_conflicts_legacy()`.

### Unit test verification
Backend-developer's run:
```
$ python3 -m pytest tests/unit/test_ast_conflict_check.py tests/unit/test_cwso_concurrent_merge.py tests/unit/test_cwso_client.py -q
.................................................................        [100%]
65 passed in 0.24s
```
Orchestrator's independent re-run (includes T314's envelope tests too):
```
$ python3 -m pytest tests/unit/test_ast_conflict_check.py tests/unit/test_cwso_concurrent_merge.py tests/unit/test_cwso_client.py tests/unit/test_cwso_mcp_client_envelope.py -q
.....................................................................    [100%]
69 passed in 0.23s
```

### Live re-verification (orchestrator's own independent run, 2026-08-02)
```
$ docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"   # before
NAMES               STATUS
cwso-rollout        Up 13 hours (healthy)
cwso-orchestrator   Up 13 hours (healthy)
cwso-git-shadow     Up 13 hours
cwso-merge-engine   Up 13 hours
cwso-sia-executor   Up 13 hours

=== Scenario 2 shape: simultaneous same-symbol add (expect MEDIUM) ===
overall_severity: medium
summary: Analyzed 1 file(s); Overall severity: medium; Conflicts in: orch_verify/s2.py

=== Scenario 3 shape: diverging signature (expect HIGH) ===
overall_severity: high
summary: Analyzed 1 file(s); Overall severity: high; Conflicts in: orch_verify/s3.py

=== Cleanup === (6 workspaces: base2/A2/B2/base3/A3/B3)
{'dropped': True} x6

$ docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"   # after — identical
NAMES               STATUS
cwso-rollout        Up 13 hours (healthy)
cwso-orchestrator   Up 13 hours (healthy)
cwso-git-shadow     Up 13 hours
cwso-merge-engine   Up 13 hours
cwso-sia-executor   Up 13 hours
```
Backend-developer's own live verification (matching evidence, run separately beforehand) also
confirmed `overall_severity=medium`/`high` for the same two shapes with all workspaces dropped.

### Disposition
All 3 fixes implemented with defensive fallbacks to the old (never-actually-observed-live)
shapes. 69/69 unit tests pass (65 required combo + 4 T314 envelope tests, full `tests/unit/`
suite is 115 passed per backend-developer). MEDIUM and HIGH severity detection independently
confirmed live, twice. No orphaned workspaces. Live stack undisturbed throughout. Scope:
`implementation/runtime/cwso/ast_conflict_check.py`, `implementation/runtime/cwso/
concurrent_merge.py`, `tests/unit/test_ast_conflict_check.py`,
`tests/unit/test_cwso_concurrent_merge.py` only. Unblocks T214 — its 3 previously-failing
scenarios (2/3/4) can now be re-run with correct severity detection.

Commit on branch `bugfix/t315-ast-precheck-live-response-shape`:
- `16a6daf` — `fix(t315): parse real query_ast/merge_concurrent_results response shapes in AstConflictChecker/ConcurrentMergeOrchestrator`

**Status: done. Completed: 2026-08-02.**
