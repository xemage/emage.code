# Task T371 — Validation gate and merge item 1 to develop

**ID:** T371
**Owner:** tech-lead
**Status:** in_progress
**Priority:** P0
**Depends on:** T369, T370
**Created:** 2026-08-09
**Completed:** —
**Based on:** docs/plans/plan-031-install-mcp-json-merge-and-repo-update.md

## Objective
Implementation Gate for item 1 (the `install.sh` MCP JSON merge fix): review T368-T370's combined
diff against this plan, run the full verification bar, and — on PASS/CONDITIONAL_PASS — merge to
`develop` per `git-workflow.md`.

## Inputs
- T368, T369, T370 outputs (combined diff on `bugfix/T368-install-vscode-mcp-merge`)
- `docs/plans/plan-031-install-mcp-json-merge-and-repo-update.md`

## Expected outputs
- VERDICT (`PASS` / `CONDITIONAL_PASS` / `FAIL`) from tech-lead review
- Merged MR on `develop` (orchestrator executes merge after independent re-verification, per the
  established T354/T357/T360-series precedent of the orchestrator re-checking a delegate's diff
  before accepting)

## Acceptance criteria
1. Full verification bar green: `make verify`, `implementation/scripts/generate-registry.py
   --check`, `implementation/scripts/validate-tasks.py`, `python3 tests/run.py`,
   `implementation/scripts/sync.mjs --check`.
2. Orchestrator independently reviews the full diff (not just the delegate's report) before
   merging.
3. Branch named in the `bugfix/T368-install-vscode-mcp-merge` family, MR to `develop`, CI green.
4. `FAIL` verdict blocks progression — orchestrator creates fix tasks and re-routes; does not
   proceed to T372 until this gate passes.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled after gate runs and MR merges>
