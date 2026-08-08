# Task T343 — Fix BUG-H: import hygiene in ast_conflict_check.py

**ID:** T343
**Owner:** backend-developer
**Status:** done
**Completed:** 2026-08-08
**Priority:** P2
**Depends on:** —
**Created:** 2026-08-08
**Based on:** `docs/tasks/task-T316.md` BUG-H, `docs/plans/plan-023-t316-pattern-a-cleanup.md` § 3.5

## Objective
Fix `implementation/runtime/cwso/ast_conflict_check.py`'s absolute import
(`from implementation.runtime.cwso.client import (...)`) to match the relative-import style used
by every other module in the same package (`from .client import ...`), eliminating the dual-class-
identity hazard confirmed via `id()`/`isinstance()` in T316's BUG-H narrative.

## Context
- Phase: Implementation (mechanical fix, no design decision)
- `implementation/runtime/cwso/concurrent_merge.py:13-14` already uses the correct relative style
  (`from .client import CwsoClient, MergeHeuristic, MergeInput, MergeLanguage`,
  `from .ast_conflict_check import AstConflictChecker, PreCheckResult`) — match that exactly.

## Inputs
- `implementation/runtime/cwso/ast_conflict_check.py` (line ~13, the import block)
- `implementation/runtime/cwso/concurrent_merge.py` (reference style)

## Constraints
- Single-line-block change. Do not touch any other logic in this file.
- Token budget: ≤ 20k (trivial fix).
- Land via a branch + MR to `develop` (branch: `bugfix/343-ast-checker-relative-import`) — no
  direct commit to `develop`, per `git-workflow.md` § "Protected Branches — No Direct Commits,
  Ever".

## Expected Outputs
- `implementation/runtime/cwso/ast_conflict_check.py` importing via
  `from .client import CwsoClient, QueryType, MergeHeuristic, MergeLanguage`.
- A regression check proving the dual-identity hazard is gone: import both
  `implementation.runtime.cwso.ast_conflict_check` and `implementation.runtime.cwso.concurrent_merge`
  in the same process and confirm `ast_conflict_check.CwsoClient is concurrent_merge.CwsoClient`
  (was `False` before the fix, per BUG-H's own evidence) — add this as a small regression test if
  none already exists, or cite the manual verification in Execution notes if a dedicated test is
  disproportionate for this fix's size.
- Task brief updated with an `## Outcome` section on completion.

## Acceptance Criteria
- [x] Import changed to relative style, matching `concurrent_merge.py`'s pattern exactly
- [x] `ast_conflict_check.CwsoClient is concurrent_merge.CwsoClient` confirmed `True` after the fix
      (cite the exact command/output) — see Outcome
- [x] Full local test suite still green
- [x] No other file changed
- [x] Landed via `bugfix/343-ast-checker-relative-import → develop` MR — opened, not self-merged

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalating.

## Outcome

**Architecture referenced:** none (mechanical packaging-hygiene fix, no design decision — per
Context).

**Files changed:**
- `implementation/runtime/cwso/ast_conflict_check.py` — single import block replaced:
  `from implementation.runtime.cwso.client import (CwsoClient, QueryType, MergeHeuristic,
  MergeLanguage,)` → `from .client import CwsoClient, QueryType, MergeHeuristic, MergeLanguage`,
  matching `concurrent_merge.py:13`'s exact style. No other line in the file touched (confirmed via
  `git diff --stat`: 1 file changed, 1 insertion(+), 6 deletions(-)).

**Regression evidence (dual-identity hazard):**

Reproduced BUG-H's hazard first, to confirm the fix actually addresses it (not just a cosmetic
`git diff --stat 1 file changed` claim). The hazard only manifests when `ast_conflict_check.py`
and a relative-import sibling (`concurrent_merge.py`) are reached via the *same* logical namespace
but the module itself is hardcoded to a specific absolute root — i.e. when only `implementation/`
is on `sys.path` (not repo root explicitly), both modules importable as `runtime.cwso.X`:

Before fix (`git stash` to isolate):
```
$ python3 -c "
import sys
sys.path.insert(0, 'implementation')
import runtime.cwso.ast_conflict_check as ast_conflict_check
import runtime.cwso.concurrent_merge as concurrent_merge
print('is same class:', ast_conflict_check.CwsoClient is concurrent_merge.CwsoClient)
print('ast_conflict_check.CwsoClient module:', ast_conflict_check.CwsoClient.__module__)
print('concurrent_merge.CwsoClient module:', concurrent_merge.CwsoClient.__module__)
"
is same class: False
ast_conflict_check.CwsoClient module: implementation.runtime.cwso.client
concurrent_merge.CwsoClient module: runtime.cwso.client
```
(`ast_conflict_check.py`'s hardcoded absolute import always pins to `implementation.runtime.cwso.client`
regardless of how the module itself was reached, while `concurrent_merge.py`'s relative import
resolves against whatever root actually got it there — `runtime.cwso.client` in this case. Two
distinct `sys.modules` entries, two distinct `CwsoClient` classes.)

After fix, identical scenario:
```
$ python3 -c "
import sys
sys.path.insert(0, 'implementation')
import runtime.cwso.ast_conflict_check as ast_conflict_check
import runtime.cwso.concurrent_merge as concurrent_merge
print('is same class:', ast_conflict_check.CwsoClient is concurrent_merge.CwsoClient)
"
is same class: True
```

Also confirmed the standard single-root case (repo root on `sys.path`, the normal/CI import
convention) is unaffected and stays `True` before and after:
```
$ python3 -c "
from implementation.runtime.cwso import ast_conflict_check
from implementation.runtime.cwso import concurrent_merge
print(ast_conflict_check.CwsoClient is concurrent_merge.CwsoClient)
"
True
```

No dedicated regression test file was added: the task's own acceptance criteria require "No other
file changed", so per the brief's explicit fallback ("or cite the manual verification in Execution
notes if a dedicated test is disproportionate for this fix's size") the manual verification above
is cited in lieu of a new test file.

**Full local test suite:**
```
$ python3 tests/run.py
Ran 293 tests in 20.290s
16 skipped (live-server tests requiring CWSO_LIVE_CONTRACT_TEST, unaffected/expected)
(no FAILED/ERROR — clean run)
```
Also ran the pytest-collected unit+functional suites directly:
```
$ python3 -m pytest tests/unit tests/functional -q --ignore=tests/functional/test_cwso_client_live.py
375 passed, 7 skipped in 29.11s
```
Note: one earlier run of `tests/run.py` under system load transiently failed
`test_scaling_and_throughput_envelope` (a wall-clock p95-latency assertion unrelated to
`ast_conflict_check.py`/CWSO). Confirmed pre-existing and unrelated to this change: it fails
identically on the unmodified baseline under the same load (`git stash` + rerun reproduced the
same flake), and passes in isolation both before and after the fix. Not attributable to this task.

**Branch / MR:**
- Branch: `bugfix/343-ast-checker-relative-import` (created fresh from `origin/develop` tip
  `bdbda9e`, since this worktree's original checkout was stale/unrelated — see note below).
- Commit: `91c75c0` — `fix(cwso): use relative import in ast_conflict_check.py to match package style`
- Pushed to `origin/bugfix/343-ast-checker-relative-import`.
- MR: https://gitlab.com/em-age/emage.code/-/merge_requests/117 (`bugfix/343-ast-checker-relative-import → develop`),
  opened via `glab mr create`, state `open`. Not self-merged — awaiting orchestrator review/merge.

**Note on worktree state:** this worktree's pre-existing checkout (`HEAD` at task start) was on an
unrelated branch/lineage (`c14bf79`, a `main`-side release-merge commit, not an ancestor of
`origin/develop`) and did not contain `docs/tasks/task-T343.md` at all. Per the task dispatch
instructions, fetched `origin` and created `bugfix/343-ast-checker-relative-import` fresh from
`origin/develop`'s actual tip (`bdbda9e`) rather than working from the stale base.

**Blocker status:** None.

### Orchestrator closeout (2026-08-08)
Independently re-verified before merging: reviewed the actual diff (1 file, absolute→relative
import matching `concurrent_merge.py`'s style exactly), independently re-ran the identity check
(`ast_conflict_check.CwsoClient is concurrent_merge.CwsoClient` → `True`) and the full suite
(293 tests, OK) on the MR branch myself. MR !117 merged (squash, source branch removed):
`merge_commit_sha: b18b5528ff03093e69348bfbd18bd353cd48426e`, target `develop`.
