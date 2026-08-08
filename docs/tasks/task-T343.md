# Task T343 — Fix BUG-H: import hygiene in ast_conflict_check.py

**ID:** T343
**Owner:** backend-developer
**Status:** pending
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
- [ ] Import changed to relative style, matching `concurrent_merge.py`'s pattern exactly
- [ ] `ast_conflict_check.CwsoClient is concurrent_merge.CwsoClient` confirmed `True` after the fix
      (cite the exact command/output)
- [ ] Full local test suite still green
- [ ] No other file changed
- [ ] Landed via `bugfix/343-ast-checker-relative-import → develop` MR — opened, not self-merged

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalating.
