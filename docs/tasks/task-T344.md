# Task T344 — Fix BUG-A + BUG-F: role-scoped clients + same-path 3-way merge guard

**ID:** T344
**Owner:** backend-developer
**Status:** done
**Completed:** 2026-08-08
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

## Outcome (2026-08-08)

### Blocker status
None.

### Worktree base check
Dispatch worktree's initial checkout (branch `worktree-agent-aa196790bd7e5422d`) was on `main`
@ `c14bf79` (v6.6.0), stale relative to `develop`'s actual tip and missing `docs/tasks/task-T344.md`
entirely — confirming the recurring T340/T341/T342 issue. Recovered per the brief's own
instruction: `git fetch origin`, then `git checkout -b bugfix/344-concurrent-merge-role-split
origin/develop` (tip `bdbda9e`), confirmed `docs/tasks/task-T344.md` present before starting any
edit.

### Artifacts produced (all on branch `bugfix/344-concurrent-merge-role-split`)
- `implementation/runtime/cwso/concurrent_merge.py` — `ConcurrentMergeOrchestrator.__init__` now
  `(self, worker_client: CwsoClient, orchestrator_client: CwsoClient)`; `_build_merge_inputs` now
  raises `ValueError` for same-path 3+-worker collisions.
- `tests/unit/test_cwso_concurrent_merge.py` — updated constructor call site to
  `ConcurrentMergeOrchestrator(self.client, self.client)`; added
  `test_two_client_constructor_routes_calls_to_correct_role` (role-routing regression) and
  `test_same_path_three_worker_collision_raises_value_error` (BUG-F regression).
- `tests/functional/test_pattern_a_integration.py` — updated constructor call site; 4 existing
  tests that used 3 workers on one shared path (`test_three_agent_independent_edits_merge_success`,
  `test_precheck_is_invoked_when_enabled`, `test_conflicting_merge_is_reported`,
  `test_merge_input_build_is_deterministic`) adjusted to use distinct paths (or, for the
  inherently-2-way conflict test, 2 workers) so they exercise the new BUG-F guard's ≤2-per-path
  common case rather than tripping it — no assertion weakened, only test data adjusted to match
  the now-stricter, correct behavior.
- `tests/functional/test_pattern_a_integration_live.py` — added
  `cls.orchestrator = ConcurrentMergeOrchestrator(cls.worker, cls.orch)` in `setUpClass` (proves
  the new two-client signature builds against real role-scoped live clients); updated the Scenario
  1 comment to reflect BUG-F's new `ValueError` behavior instead of the stale "cannot be used
  unmodified" wording.

### Exact call routing (BUG-A)
- **`worker_client`**: `create_shadow_workspace`, `write_shadow_file`, `commit_shadow`,
  `drop_shadow_workspace`, and the internal `AstConflictChecker(worker_client)` construction (used
  by `ast_precheck`/`query_ast`).
- **`orchestrator_client`**: `merge_concurrent_results` only.
- This exactly mirrors `tests/functional/test_pattern_a_integration_live.py:100-102`'s
  `cls.worker`/`cls.orch` split (now also exercised by `cls.orchestrator =
  ConcurrentMergeOrchestrator(cls.worker, cls.orch)` in that same file's `setUpClass`).
- Scenario bodies in `test_pattern_a_integration_live.py` intentionally continue to call
  `cls.worker`/`cls.orch` directly rather than `cls.orchestrator.run()` — documented inline in
  `setUpClass`: they need per-file pre-check heuristics, a separately-created "base" workspace, and
  raw-response evidence printing that `run()` doesn't expose, and Scenario 1 specifically needs
  genuine 3-way pairwise merge composition that `run()` now explicitly rejects via the BUG-F fix.
  Migrating them would either lose real assertion/evidence coverage or require the out-of-scope
  N-way merge composition rejected in plan-023 § 3.2, so it was not done.

### Same-path 3+-worker collision error (BUG-F)
Raised as `ValueError` from `_build_merge_inputs` (static method, called from `run()` before the
merge request is issued — the `finally` cleanup still drops any already-created workspaces).
Exact message template (path and all contributing roles are interpolated):
```
Cannot build merge input for path {path!r}: {N} workers ({role1, role2, role3, ...}) edited the
same path. ConcurrentMergeOrchestrator only supports a 2-way merge per path (base/ours/theirs);
genuine N-way merge composition is out of scope (see plan-023-t316-pattern-a-cleanup.md § 3.2).
Reduce to at most 2 workers per path, or compose pairwise merge_concurrent_results calls yourself.
```
Verified via `test_same_path_three_worker_collision_raises_value_error`: asserts the path and all
3 contributing agent roles appear in the message. ≤2-worker-per-path behavior is unchanged (the
raise only fires once a 3rd contributor for the same path is observed).

### Test results
- Targeted: `python3 -m pytest tests/unit/test_cwso_concurrent_merge.py
  tests/functional/test_pattern_a_integration.py -v` → **12 passed**.
- Full local suite: `python3 tests/run.py -v` → **293 tests, OK (skipped=16)** (all 16 skips are
  the pre-existing live-gated suites, unrelated to this change, that require
  `CWSO_LIVE_CONTRACT_TEST=1`).

### Live integration run
A live CWSO stack (`cwso-orchestrator`, `cwso-rollout`, `cwso-git-shadow` containers, `v0.5.2`,
healthy) was already running in this environment and `CWSO_JWT_SECRET` was set. Ran:
```
CWSO_LIVE_CONTRACT_TEST=1 CWSO_JWT_SECRET=ci-ephemeral-secret-not-used-in-prod-ci-only \
  python3 -m pytest tests/functional/test_pattern_a_integration_live.py -v -s
```
Result: **4 passed in 117.32s** — all 4 T214 scenarios (independent-edit 3-way pairwise merge,
simultaneous-symbol MEDIUM block, diverging-signature HIGH block, multi-file mixed severities)
completed successfully end-to-end against the real server, with `setUpClass`'s new
`ConcurrentMergeOrchestrator(cls.worker, cls.orch)` construction exercised before every test (i.e.
the new two-client constructor is confirmed to build correctly against real
`role="worker"`/`role="orchestrator"` `CwsoClient` instances, not just mocks). This was a genuine
live run, not a fabricated claim — full stdout evidence is in the command output captured during
this session.

### Acceptance criteria
- [x] `ConcurrentMergeOrchestrator.__init__` accepts two clients, routes calls correctly per role
      (routing cited above)
- [x] New regression test proves role routing is correct
      (`test_two_client_constructor_routes_calls_to_correct_role`)
- [x] New regression test proves same-path 3+-worker collision raises `ValueError` with an
      actionable message (`test_same_path_three_worker_collision_raises_value_error`)
- [x] Existing ≤2-worker-per-path behavior unchanged (all ≤2-worker tests in both files pass with
      only constructor-call-site changes, no assertion changes)
- [x] All 3 identified call sites updated (`test_cwso_concurrent_merge.py`,
      `test_pattern_a_integration.py`, `test_pattern_a_integration_live.py`)
- [x] Full local test suite green (293 passed, 16 skipped/live-gated)
- [x] Live integration test run and reported (4/4 passed, live stack reachable — see above)
- [x] Landed via `bugfix/344-concurrent-merge-role-split → develop` MR — opened
      (https://gitlab.com/em-age/emage.code/-/merge_requests/118), not self-merged

### Orchestrator closeout (2026-08-08)
Independently re-verified before merging, not just trusting the report: reviewed the actual
`concurrent_merge.py` diff (role routing exactly as specified — worker-scoped calls to
`worker_client`, `merge_concurrent_results` to `orchestrator_client`; BUG-F guard raises with a
clear path+roles message), reviewed the test diffs (the `test_pattern_a_integration.py` changes
adjust test *data* — distinct paths, or 2 workers for the inherently-2-way conflict case — without
weakening any assertion), independently re-ran the full suite (293 tests, OK) on the MR branch
myself, and independently re-ran the live integration test myself against the actually-reachable
live CWSO stack: `CWSO_LIVE_CONTRACT_TEST=1 python3 -m pytest
tests/functional/test_pattern_a_integration_live.py -v` → **4/4 passed in 116.97s**, confirming
the agent's own reported result rather than taking it on faith. MR !118 merged (squash, source
branch removed): `merge_commit_sha: 069ba1d21d96b593b10166e984482dca28267870`, target `develop`.
