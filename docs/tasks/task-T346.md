# Task T346 — GATE: verify T343/T344/T345, record BUG-G disposition, close T316

**ID:** T346
**Owner:** qa-engineer
**Status:** done
**Completed:** 2026-08-08
**Priority:** P2
**Depends on:** T343, T344, T345
**Created:** 2026-08-08
**Based on:** `docs/plans/plan-023-t316-pattern-a-cleanup.md`, `docs/tasks/task-T316.md`

## Objective
Independently verify T343 (BUG-H), T344 (BUG-A + BUG-F), and T345 (BUG-E) are all correctly
merged to `develop` and the combined result is sound (no interaction bugs between the three
independent changes), record BUG-G's deferral disposition, and produce the evidence needed for the
orchestrator to close T316 itself.

## Context
- Phase: Validation Gate (review only — MUST NOT modify code, per `.claude/rules/security-guidelines.md`
  § "Read-Only Agents" / `AGENTS.md` § "Validation Gates": review agents do not modify code during
  review)
- This task only starts once T343/T344/T345 have all been merged to `develop` — do not begin
  before confirming all three MRs are merged (check `git log develop` for the three merge commits,
  or ask the orchestrator to confirm before you start if it's unclear).
- BUG-G's disposition (deferred, not routed to CWSO) was already decided and reasoned in
  `docs/plans/plan-023-t316-pattern-a-cleanup.md` § 3.4 — this task records that decision in
  `docs/tasks/task-T316.md`'s own Execution notes, it does not re-litigate it.

## Inputs
- `docs/plans/plan-023-t316-pattern-a-cleanup.md` — full design rationale
- `docs/tasks/task-T343.md`, `task-T344.md`, `task-T345.md` — Outcome sections with per-task
  evidence
- `docs/tasks/task-T316.md` — the original task, to be updated with final disposition

## Constraints
- Read-only for application code — this is a verification gate, not an implementation task.
- May write to `docs/tasks/task-T316.md` only (recording the verification result and BUG-G's
  disposition) — do not touch `active-tasks.md`/`completed-tasks.md` (orchestrator-only archival)
  and do not touch this task's own `**Status:**` header beyond what's needed to report your result
  to the orchestrator.
- Token budget: ≤ 40k.

## Expected Outputs
- A VERDICT (`PASS` | `CONDITIONAL_PASS` | `FAIL`) per `.claude/rules/*` validation-gate
  convention, covering:
  1. Full local test suite green on current `develop` tip (after all three merges)
  2. `implementation.runtime.cwso.ast_conflict_check.CwsoClient is
     implementation.runtime.cwso.concurrent_merge.CwsoClient` → `True` (BUG-H's fix, re-verified
     independently, not just trusting T343's own report)
  3. `ConcurrentMergeOrchestrator`'s new two-client constructor works as designed (re-run or
     independently inspect T344's regression tests)
  4. Same-path 3+-worker collision raises the expected error (re-run or independently inspect
     T344's regression test)
  5. `write_shadow_file`'s best-effort `blob_oid` extraction behaves as designed on the real
     example format from BUG-E (re-run or independently inspect T345's regression test)
- A written disposition for BUG-G appended to `docs/tasks/task-T316.md`'s Execution notes: quote
  plan-023 § 3.4's reasoning, confirm it as this task's own independent recommendation (not just a
  copy), and confirm no active caller of `ConcurrentMergeOrchestrator` outside tests has emerged
  that would change that reasoning.

## Acceptance Criteria
- [ ] Full test suite result cited with exact command/output
- [ ] All 5 checks above independently re-verified (not just re-stating what T343/T344/T345
      already claimed) — re-run the relevant tests/commands yourself
- [ ] BUG-G disposition recorded in `task-T316.md` Execution notes
- [ ] VERDICT stated explicitly
- [ ] No application code modified by this task

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. A `FAIL` verdict is not itself a blocker — it's
a valid, expected outcome; report it plainly with the specific failing check, and the orchestrator
will create a fix task and re-route (per `AGENTS.md` § "Validation Gates").

## Outcome (2026-08-08)

### Worktree base check
This worktree's initial checkout (branch `worktree-agent-a39ae596f3b5dcf2e`) was on `main` @
`c14bf79` (v6.6.0) and did not contain `docs/tasks/task-T346.md` — confirming the recurring
T340/T341/T342/T343/T344 stale-worktree issue. Recovered per the brief's instruction: `git fetch
origin`, then `git checkout -b agent/qa-engineer/T346 origin/develop` (tip `61c3465`), confirmed
`docs/tasks/task-T346.md` and the T343/T344/T345 merge commits (`b18b552`, `069ba1d`, `f23e480`,
plus closeout commits `decbe21`/`61c3465`) present before starting any verification.

### Check 1 — Full local test suite green
```
$ python3 tests/run.py
Ran 293 tests in 12.648s
OK (skipped=16)
```
```
$ python3 -m pytest tests/unit tests/functional -q --ignore=tests/functional/test_cwso_client_live.py
380 passed, 7 skipped in 9.06s
```
No FAILED/ERROR in either run. Independently executed by this task, not cited from T343/T344/T345.

### Check 2 — BUG-H identity fix
Re-ran from a fresh process (not trusting T343's own report):
```
$ python3 -c "
from implementation.runtime.cwso import ast_conflict_check
from implementation.runtime.cwso import concurrent_merge
print(ast_conflict_check.CwsoClient is concurrent_merge.CwsoClient)
"
True
```
Also reproduced the dual-root hazard scenario T343 used to demonstrate the bug (`sys.path.insert(0,
'implementation')`, import both modules as `runtime.cwso.X`) and confirmed it now also returns
`True` (was `False` pre-fix per T343's Outcome). Also confirmed
`implementation/runtime/cwso/ast_conflict_check.py`'s import block is
`from .client import CwsoClient, QueryType, MergeHeuristic, MergeLanguage` (relative style,
matching `concurrent_merge.py`).

### Check 3 — BUG-A two-client role routing
Inspected `implementation/runtime/cwso/concurrent_merge.py` directly: `__init__(self, worker_client:
CwsoClient, orchestrator_client: CwsoClient)`; `worker_client` routes
`create_shadow_workspace`/`write_shadow_file`/`commit_shadow`/`drop_shadow_workspace` and
`AstConflictChecker(worker_client)`; `orchestrator_client` routes `merge_concurrent_results` only —
matches T344's cited routing exactly. Independently re-ran the regression test:
```
$ python3 -m pytest tests/unit/test_cwso_concurrent_merge.py -v -k two_client_constructor
test_two_client_constructor_routes_calls_to_correct_role PASSED
```

### Check 4 — BUG-F same-path 3+-worker collision guard
Inspected `_build_merge_inputs`: raises `ValueError` once a 3rd contributor for the same path is
seen, message includes the path and all contributing roles. Independently re-ran:
```
$ python3 -m pytest tests/unit/test_cwso_concurrent_merge.py -v -k three_worker_collision
test_same_path_three_worker_collision_raises_value_error PASSED
```
Full file (8/8) and the related functional suite (`test_ast_conflict_check.py` +
`test_pattern_a_integration.py`, 29/29) also re-run clean.

### Check 5 — BUG-E blob_oid extraction
Inspected `write_shadow_file`/`_extract_blob_oid` in `implementation/runtime/cwso/client.py`:
regex `blob\s+([0-9a-f]+)` applied only to still-enveloped prose text, returns a new dict with
`blob_oid` on match, returns the response unmodified (no raise) otherwise. Independently re-ran all
4 related tests:
```
$ python3 -m pytest tests/unit/test_cwso_client.py -v -k write_shadow_file
test_write_shadow_file PASSED
test_write_shadow_file_already_json_unaffected PASSED
test_write_shadow_file_extracts_blob_oid_from_real_prose_format PASSED
test_write_shadow_file_non_matching_prose_does_not_raise PASSED
```

### Extra confidence — live contract test
A live CWSO stack was reachable (`curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/healthz`
→ `200`) and `CWSO_JWT_SECRET` was set. Independently re-ran (third independent run this session,
after the T344 agent's own and the orchestrator's T344-closeout run):
```
$ CWSO_LIVE_CONTRACT_TEST=1 python3 -m pytest tests/functional/test_pattern_a_integration_live.py -v
4 passed in 117.00s
```
All 4 scenarios (independent-edit merge, simultaneous-symbol MEDIUM block, diverging-signature HIGH
block, multi-file mixed severities) passed against the real server with the new two-client
constructor.

### BUG-G disposition
Recorded in `docs/tasks/task-T316.md` § Execution notes (2026-08-08 entry): quotes plan-023 § 3.4
verbatim, independently confirms it as this task's own recommendation (grounded in this task's own
re-run of the full/live suites observing the same generic conflict message, and a fresh
`grep -rn "ConcurrentMergeOrchestrator(" --include="*.py" .` survey confirming the only
construction call sites remain the 3 test files — no non-test caller has emerged since plan-023
§ 3.4 was written), and confirms the disposition (deferred, not routed to CWSO) stands.

### Acceptance criteria
- [x] Full test suite result cited with exact command/output
- [x] All 5 checks independently re-verified (test runs + direct code inspection, not just
      re-stating T343/T344/T345's claims)
- [x] BUG-G disposition recorded in `task-T316.md` Execution notes
- [x] VERDICT stated explicitly (below)
- [x] No application code modified by this task (`git status --short` on this worktree shows only
      `docs/tasks/task-T316.md` and `docs/tasks/task-T346.md` touched — see note below)

### Blocker status
None.

### Note on landing
Per explicit orchestrator instruction for this dispatch, this task's two doc-only changes
(`docs/tasks/task-T316.md`, `docs/tasks/task-T346.md`) are reported back directly rather than
landed via a branch + MR from this worktree, to avoid an extra round-trip for a review-only task
that writes no application code — the orchestrator will land them itself alongside T316's final
closure.

## VERDICT: PASS

### Justification
All 5 required checks were independently re-verified by this task (not merely re-stated from
T343/T344/T345's own Outcome sections): the full local test suite is green on `develop`'s current
tip (post all three merges) via two independent invocations (`tests/run.py`: 293 OK/16 skipped;
direct pytest: 380 passed/7 skipped); BUG-H's identity fix holds (`True` for both the standard
single-root import path and the dual-root hazard scenario that previously reproduced `False`);
BUG-A's two-client constructor routes calls exactly as designed (verified by direct code
inspection plus a passing regression test); BUG-F's same-path 3+-worker collision guard raises
`ValueError` with the path and contributing roles (verified by direct code inspection plus a
passing regression test); BUG-E's `blob_oid` extraction behaves as designed on the real observed
prose format, fails open on non-match, and leaves already-JSON responses untouched (verified by 4
passing regression tests). As extra confidence, the live CWSO contract test was independently
re-run a third time this session and passed 4/4. No interaction issues were found between the
three independent changes (disjoint files, full suite green together). No application code was
modified by this task. BUG-G's disposition has been recorded in `task-T316.md` per the brief's
exact instructions.
