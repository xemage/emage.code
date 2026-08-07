# Task T319 — Author the missing Pattern A usage guide

**ID:** T319
**Owner:** technical-writer (structure) + backend-developer (technical accuracy)
**Status:** done
**Priority:** P0
**Depends on:** T317
**Created:** 2026-08-02
**Completed:** 2026-08-03
**Based on:** docs/plans/plan-017-deployment-docs-and-registry-hardening.md, docs/tasks/task-T214.md,
docs/tasks/task-T314.md, docs/tasks/task-T315.md

## Objective
Write `implementation/runtime/cwso/README.md` — required as a deliverable by T214's original brief
and never produced. Document the ACTUAL, CURRENT, post-fix behavior of the Pattern A runtime
modules, not aspirational or pre-fix behavior.

## Inputs
- `implementation/runtime/cwso/client.py`, `mcp_client.py`, `ast_conflict_check.py`,
  `concurrent_merge.py`
- `tests/functional/test_pattern_a_integration_live.py` (the proven, working usage pattern)
- `docs/tasks/task-T214.md` (BUG-A role-split finding), `task-T314.md` (envelope-unwrap fix),
  `task-T315.md` (response-shape fix)
- `implementation/scripts/test-jwt-registration.py`, `.claude/rules/security-guidelines.md`

## Expected outputs
- `implementation/runtime/cwso/README.md` (new file)

## Acceptance criteria
1. Documents the role-split requirement found as BUG-A: a single-role `CwsoClient` cannot run the
   full flow — `worker` may create/write/commit/query_ast/drop but not
   `merge_concurrent_results`; `orchestrator` may create/merge/drop but not
   `write_shadow_file`/`commit_shadow`. Two role-scoped client instances from one shared JWT
   secret are required.
2. Contains a minimal worked example based directly on
   `test_pattern_a_integration_live.py`'s Scenario 1, using the POST-T314 response shape (e.g.
   `create_shadow_workspace()` returns `{"workspace_uuid": ..., "base_tree_oid": ...}`, not the
   raw MCP envelope).
3. Explains how to obtain a JWT for local testing via `generate_jwt_token()` and
   `CwsoClient.from_env()`, and explicitly notes the `.env.jwt.dev`/`.env.*` read guard from
   `security-guidelines.md` — a reader (human or agent) generates a fresh secret, never reads the
   existing dev secret file directly.
4. Links to `docs/tasks/task-T214.md` and `task-T315.md` as the canonical evidence record.
5. If a live CWSO stack is reachable, the worked example's commands are actually run and the
   README's shown output matches real output. If no live stack is reachable, this limitation is
   stated explicitly in Execution notes rather than silently skipped.
6. `grep -c "role-split\|role_split" implementation/runtime/cwso/README.md` → 1 or more.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed: 2026-08-03

Created `implementation/runtime/cwso/README.md` covering:
1. What Pattern A is (one paragraph)
2. Role-split requirement (BUG-A) with permission table and code example
3. Minimal worked example based directly on test_pattern_a_integration_live.py Scenario 1
4. BUG-E note on write_shadow_file plain-text response shape
5. JWT / from_env() guide with env var table, link to test-jwt-registration.py
6. Live verification status (stack was down at authoring time; instructions to re-verify)
7. Links to task-T214.md and task-T315.md as canonical evidence

### Verify output
```
grep -c "role-split\|role_split" implementation/runtime/cwso/README.md
1
```
```
test -f implementation/runtime/cwso/README.md && echo FILE EXISTS
FILE EXISTS
```

**Result: PASS**

**Limitation:** no live stack was running at authoring time. Worked example is based on confirmed
passing Scenario 1 from T214/T314/T315 runs. Run `CWSO_LIVE_CONTRACT_TEST=1` against a live
stack to re-verify the example commands.
