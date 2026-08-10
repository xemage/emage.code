# Task T371 — Validation gate and merge item 1 to develop

**ID:** T371
**Owner:** tech-lead
**Status:** done
**Priority:** P0
**Depends on:** T369, T370
**Created:** 2026-08-09
**Completed:** 2026-08-09
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
VERDICT: PASS. Ran the full verification bar on `bugfix/T368-install-vscode-mcp-merge`: `make verify`
(0 drift, 550 files), `implementation/scripts/generate-registry.py --check` (up to date),
`docs/tasks/validate-tasks.py` (TASK LEDGER PASS), `python3 tests/run.py` (299 tests, OK, skipped=17),
`node implementation/scripts/sync.mjs --check` (0 drift). Independently reviewed the full diff (11
files, +857/-2 — `scripts/install.sh`, `scripts/merge-mcp-json.py`,
`tests/functional/test_install_script.py`, `README.md`, plan + task-brief docs) before proceeding.

Pushed branch, opened MR !158
(https://gitlab.com/em-age/emage.code/-/merge_requests/158). CI pipeline #2745395767 went green on
all 5 jobs (sync-no-diff, validation-super-gate, verify-knowledge-drift, unit-tests,
markdown-links). Merged via `glab mr merge 158 --squash=false --yes`; GitLab squashed the merge
anyway (commit `07b141a`, merge commit `2b11d20`) despite the explicit override — same
`squash_option: default_on` behavior CONTRIBUTING.md documents for this project; acceptable here
since squash-and-merge is this repo's own documented default for feature/bugfix branches. Re-ran
the entire verification bar a second time directly against `develop` post-merge — identical results,
no drift introduced by the squash. Local and remote feature branch cleaned up.
