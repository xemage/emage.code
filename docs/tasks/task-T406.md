# Task T406 — Validation gate + merge Phase 0 (T400–T405) to `develop`

**ID:** T406
**Owner:** qa-engineer (validation), tech-lead (implementation gate review), orchestrator (merge)
**Status:** done
**Priority:** P0
**Depends on:** T400, T401, T402, T403, T404, T405 (all must be committed on the shared branch)
**Created:** 2026-08-12
**Completed:** —
**Based on:** docs/plans/plan-035-roadmap-v7-ground-up.md (Phase 0, §2.4)

This brief is self-contained.

## Objective
Independently verify the full Phase 0 batch (T400–T405, all stacked as commits on
`feature/T400-phase0-ground-truth-v6.11.0`) against the plan's Phase 0 acceptance criteria, open a
merge request to `develop`, confirm CI is green, and merge — closing Gate G0. This mirrors the
established `plan-033`/T381 and `plan-034` validation-gate pattern: full verification bar,
independent diff review, branch → MR → CI green → merge, never a direct push to `develop`.

## Inputs
- `feature/T400-phase0-ground-truth-v6.11.0` — the shared branch carrying T400–T405's commits.
- Phase 0's acceptance criteria, copied here verbatim from `docs/plans/plan-035-roadmap-v7-ground-
  up.md` §2.4 for convenience (the plan file is the authoritative source if these ever drift):
  - [ ] `python3 scripts/check-version-consistency.py` exits 0 on a clean tree
  - [ ] Deliberately reverting `implementation/README.md:4` to `v6.0.1` makes it exit non-zero
  - [ ] `docs/deployment/` contains no deployment instructions for any target
  - [ ] `pytest tests/performance/test_team_health.py` passes, including
        `test_every_active_task_has_a_plan`
  - [ ] Creating a task row without a plan reference fails CI

## Expected outputs
- QA engineer: a validation report (can be inline in the completion message, no separate artifact
  file required for this task) confirming each Phase 0 acceptance criterion above, plus the full
  verification bar:
  1. `make verify` (== `node implementation/scripts/sync.mjs --root implementation --check`) — 0
     drift
  2. `implementation/scripts/generate-registry.py --check` — passes
  3. `docs/tasks/validate-tasks.py` (or `implementation/docs/tasks/validate-tasks.py` — confirm
     the actual sanctioned path at execution time) — passes
  4. `python3 tests/run.py` — full suite green, no regressions vs. the pre-Phase-0 baseline
  5. `python3 scripts/check-version-consistency.py` — exits 0
  6. `python3 scripts/verify-release-docs.py --tag <current README marker>` — passes (proves
     T404's wiring works end-to-end)
- Tech lead: independent read-only review of the full `develop...feature/T400-phase0-ground-truth-
  v6.11.0` diff (per `.claude/rules/security-guidelines.md`, Tech Lead is read-only during review
  — annotate/approve/request-changes only, no edits). Produce a VERDICT: `PASS` /
  `CONDITIONAL_PASS` / `FAIL` per `AGENTS.md`'s Validation Gates protocol.
- Orchestrator: on `PASS` or `CONDITIONAL_PASS` (with conditions tracked), push the branch, open
  an MR to `develop` referencing T400–T406, watch CI to green, merge (squash-and-merge per
  `git-workflow.md`'s feature-branch convention — note the actual branch prefix used is `feature/`
  even though the underlying work spans multiple Conventional Commit types (`feat`/`fix`/`docs`/
  `refactor`), consistent with the `plan-033`/T377-T381 precedent of one branch per logical batch
  regardless of individual commit types).

## Acceptance criteria
1. All five Phase 0 acceptance-criteria checkboxes above are independently confirmed true, not
   merely asserted by the implementing agents.
2. Full verification bar (6 items above) green.
3. Tech lead's diff review is genuinely independent — read the diff, don't rubber-stamp a
   implementer's self-report.
4. `FAIL` verdict blocks progression — do not merge; instead return to the orchestrator with the
   specific failing criteria so fix tasks can be created and re-delegated (do not silently patch
   the failure yourself; per `AGENTS.md`, review agents must not modify code during review).
5. MR title/description references T400–T406 and links `docs/plans/plan-035-roadmap-v7-ground-
   up.md`.
6. Branch is up to date with `develop` before merge (rebase/merge `develop` in if it has moved
   since the branch was cut).
7. Post-merge: `git worktree remove`/branch cleanup per `git-workflow.md`'s Worktree Lifecycle, if
   a dedicated worktree was used for this batch (confirm whether the batch was worked in the
   orchestrator's primary checkout via a plain branch switch, or a dedicated worktree, and clean up
   accordingly).
8. Gate G0 is explicitly declared closed in the orchestrator's next checkpoint
   (`docs/checkpoints/checkpoint-016-phase0-kickoff.md` or its successor) once this task completes.

## Blocker protocol
- Any verification-bar item failing → do not merge. Report which item, exact command, exact
  output. `type: technical`, `severity: major` if it looks like an implementation defect in
  T400–T405; `type: dependency`, `severity: minor` if it looks like environment drift unrelated to
  this batch.
- CI failing on GitLab after MR is opened, for a reason not reproducible locally → `type:
  technical`, `severity: major` — do not force-merge past a red pipeline (`git-workflow.md`: "All
  CI checks must pass").
- Max 2 retries on any single failing check before escalating to the user with full context.

## Git workflow
1. Confirm all of T400–T405's commits are present on `feature/T400-phase0-ground-truth-v6.11.0`.
2. Run the full verification bar (above).
3. Tech lead reviews the diff, produces a VERDICT.
4. On `PASS`/`CONDITIONAL_PASS`: `git push -u origin feature/T400-phase0-ground-truth-v6.11.0`,
   open MR to `develop` (via `mcp__gitlab` or `glab`/`gh` equivalent — this repo's remote is
   GitLab, use the GitLab tooling), wait for CI green, merge (squash-and-merge), delete the source
   branch on merge per `git-workflow.md`'s MR rules.
5. On `FAIL`: do not push/open an MR. Report back to the orchestrator with the failing criteria.

## Constraints
- Token budget: ≤15k tokens (this is a review/merge gate, not implementation — should be cheap).
- No code changes by qa-engineer or tech-lead during this task — verification and review only.
