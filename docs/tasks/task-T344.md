# Task T344 — Fix BUG-A + BUG-F: role-scoped clients + same-path 3-way merge guard

**ID:** T344
**Owner:** backend-developer
**Status:** pending
**Priority:** P2
**Depends on:** —
**Created:** 2026-08-08
**Based on:** `docs/tasks/task-T316.md` BUG-A, BUG-F; `docs/plans/plan-023-t316-pattern-a-cleanup.md`
§ 3.1, § 3.2 (design decisions — read these before starting, the decisions are already made, this
task is implementation)

## Objective
`ConcurrentMergeOrchestrator.run()` cannot execute end-to-end against the live CWSO server today
because its single-client constructor can't hold both the `worker` role (needed for
`create_shadow_workspace`/`write_shadow_file`/`commit_shadow`/`drop_shadow_workspace`/AST
pre-check) and the `orchestrator` role (needed for `merge_concurrent_results`) at once — the live
permission matrix denies each role the other's operations. Separately, `_build_merge_inputs`
silently drops a worker's edits when 3+ workers touch the same file path. Fix both in the same
task since they're both in `concurrent_merge.py` and touch the same call sites.

## Context
- Phase: Implementation
- Design already decided in `docs/plans/plan-023-t316-pattern-a-cleanup.md` § 3.1/§3.2 — do not
  re-derive or second-guess it, implement it:
  - **BUG-A:** `ConcurrentMergeOrchestrator.__init__` changes from `(self, client: CwsoClient)` to
    `(self, worker_client: CwsoClient, orchestrator_client: CwsoClient)`. Route
    `create_shadow_workspace`/`write_shadow_file`/`commit_shadow`/`drop_shadow_workspace` and the
    internal `AstConflictChecker(...)` construction to `worker_client`; route
    `merge_concurrent_results` to `orchestrator_client`. This exactly mirrors
    `tests/functional/test_pattern_a_integration_live.py:100-181`'s already-proven-live pattern
    (`cls.worker` / `cls.orch`) — use that file as your ground truth for which calls go to which
    role, don't guess.
  - **BUG-F:** `_build_merge_inputs` (or `run()`, implementer's judgment on exact placement) raises
    `ValueError` with a message identifying the path and the ≥3 contributing worker roles when 3 or
    more workers edit the same path. Paths touched by ≤2 workers must continue to work exactly as
    today (do not change behavior for the common case).
- **Call sites needing the new two-client constructor** (confirmed via `grep -rl
  "ConcurrentMergeOrchestrator("`, do not skip any):
  `tests/unit/test_cwso_concurrent_merge.py`, `tests/functional/test_pattern_a_integration.py`,
  `tests/functional/test_pattern_a_integration_live.py`. In the two mocked test files, it's fine
  to pass the same mock object for both `worker_client` and `orchestrator_client` (the mock
  doesn't enforce role restrictions) unless the test specifically needs to distinguish which role
  a call went to. In `test_pattern_a_integration_live.py`, replace whatever manual workaround
  exists there with a direct `ConcurrentMergeOrchestrator(cls.worker, cls.orch)` construction now
  that the class itself supports it — check whether this simplifies that test file meaningfully,
  but do not remove real assertion coverage in the process.
- **Worktree base check:** this session has hit a recurring issue (T340, T341, T342) where a
  dispatched agent's isolated worktree was checked out on a stale/wrong base instead of current
  `develop`. Before starting, run `git log -1 develop` (or `git log -1 origin/develop` after
  `git fetch origin`) and confirm `docs/tasks/task-T344.md` (this file) is present in your
  worktree — if it isn't, your worktree is on a stale base; branch fresh from `develop`'s actual
  current tip instead of guessing at content.

## Inputs
- `implementation/runtime/cwso/concurrent_merge.py` — file to edit
- `implementation/runtime/cwso/client.py` — `CwsoClient` role model (read-only reference, do not
  edit as part of this task)
- `tests/functional/test_pattern_a_integration_live.py:90-235` — proven-live reference pattern for
  BUG-A; also has a comment near line 230 explicitly noting the current 3-way limitation this
  task's BUG-F fix addresses
- `docs/tasks/task-T214.md` Execution notes — original live evidence for both bugs

## Constraints
- Do not implement genuine N-way sequential-pairwise merge composition (explicitly rejected for
  this wave in plan-023 § 3.2) — a raised, clear error for same-path 3+-worker collisions is the
  full scope of the BUG-F fix.
- Do not change `client.py`'s role/JWT model — `CwsoClient` itself is out of scope for this task
  (BUG-E, a separate task T345, touches `client.py`).
- Token budget: ≤ 60k.
- Land via a branch + MR to `develop` (branch: `bugfix/344-concurrent-merge-role-split`) — no
  direct commit to `develop`.

## Expected Outputs
- `ConcurrentMergeOrchestrator.__init__(self, worker_client: CwsoClient, orchestrator_client:
  CwsoClient)` with correct call routing per role.
- `_build_merge_inputs` (or equivalent) raising a clear `ValueError` for same-path 3+-worker
  collisions, with a regression test proving it (construct a `WorkerEditSet` list where 3 workers
  edit the same path, assert the raise and its message content).
- A regression test proving the two-client role routing is correct (e.g., using two distinct mock
  objects and asserting `create_shadow_workspace`/etc. were called on the worker mock and
  `merge_concurrent_results` was called on the orchestrator mock, not the reverse).
- All 3+ existing call sites updated and passing.
- If a live CWSO stack is reachable in your environment (check via whatever this repo's existing
  live-test skip logic already does, e.g. an env var or connectivity check —
  `test_pattern_a_integration_live.py` likely already has this pattern), run it and report the
  result; if not reachable, say so plainly rather than fabricating a live-run claim — the mocked
  test suite passing is still your primary acceptance bar.
- Task brief updated with an `## Outcome` section citing exact commands/output.

## Acceptance Criteria
- [ ] `ConcurrentMergeOrchestrator.__init__` accepts two clients, routes calls correctly per role
      (cite the routing explicitly: which methods go to which client)
- [ ] New regression test proves role routing is correct
- [ ] New regression test proves same-path 3+-worker collision raises `ValueError` with an
      actionable message (names the path and the contributing roles)
- [ ] Existing ≤2-worker-per-path behavior unchanged (existing tests for that path still pass
      without modification to their assertions, only to their constructor calls)
- [ ] All 3 identified call sites updated
- [ ] Full local test suite green
- [ ] Live integration test run and reported if reachable; honestly reported as unreachable if not
- [ ] Landed via `bugfix/344-concurrent-merge-role-split → develop` MR — opened, not self-merged

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalating. If the live
integration test's connectivity check itself is unclear or missing, that's a valid
`technical`/`minor` blocker to report — don't guess at how to reach a live server.
