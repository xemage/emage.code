# Task T297 — Prepare release `v6.4.0` (branch + final checks; human executes tag/merge/push)

**ID:** T297
**Owner:** release-manager
**Status:** done
**Priority:** P0
**Depends on:** T296
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T297;
`CONTRIBUTING.md` § "Cutting a release".

## Why this task exists
This is the final task in Plan 015. It prepares the `release/v6.4.0` branch
and re-confirms every gate is green, then **stops** before any action that
pushes to the shared GitLab remote or changes `main` — tagging, merge-requesting,
merging, and pushing a release tag are irreversible/shared-state actions that
require a human maintainer's explicit go-ahead, per this repository's own
`CONTRIBUTING.md` release process (branch → MR → review → merge → tag → push
→ back-merge). A cheap/dumb agent must not perform those steps unattended.

## STOP-RULES (read before touching anything)
- Confirm T296 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T297 (missing dependency)`.
- **R6** Do NOT run `git push` under any circumstance in this task, including
  pushing the new branch.
- **Do NOT** create a git tag, open a merge request, or merge to `main`. Those
  are explicitly human-executed steps in this task (see "Human steps" below).
- **R2** This task creates **at most one local git branch**
  (`release/v6.4.0`). It must not modify any tracked file — if `git status`
  shows any diff beyond the branch pointer after Step 2, STOP and report
  (that means an earlier task, T285–T296, left uncommitted work).

## Precondition (added after discovery — read before dispatching this task)

This brief's Step 2 branches `release/v6.4.0` from `develop`. That is only
correct **after** `feature/t285-add-claude-code-platform` (which holds every
commit from T285–T296) has already been merged into `develop` via an
approved, CI-green merge request. Merging a feature branch — pushing it,
opening the MR, waiting for pipeline + review, clicking merge — is itself a
shared-state action requiring the user's explicit go-ahead each time (per the
Orchestrator's own operating constraints), not something to perform
autonomously just because this plan was approved in advance. **Do not run
this task's Automated steps until the user has confirmed the feature branch
is merged to `develop`.** If it is not yet merged, STOP immediately and
report that back instead of proceeding — do not substitute the feature
branch for `develop` in Step 2 as a workaround.

## Automated steps (this task performs these, only once the precondition above is confirmed)

1. Confirm the working tree is clean before branching:
   ```bash
   git status --porcelain
   ```
   Expected: no output. If output appears, STOP and report — do not branch
   from a dirty tree.

2. Create the release branch locally from `develop` (do not push):
   ```bash
   git checkout develop
   git pull
   git checkout -b release/v6.4.0
   ```

3. Re-run the release docs gate on the release branch (final confirmation):
   ```bash
   python3 scripts/verify-release-docs.py --tag v6.4.0
   ```
   Expected: `release-docs-verify: all documentation checks passed`, exit `0`.

4. Re-run the full validation/test gate one more time on this branch (cheap
   insurance against branch-creation side effects):
   ```bash
   node implementation/scripts/verify.mjs --root implementation
   python3 tests/run.py
   ```
   Expected: both exit `0`.

5. STOP here. Do not proceed further automatically.

## Human steps (report these as the next actions; do NOT execute them)

Report to the user, verbatim, that the following steps remain and require
their explicit approval (per `CONTRIBUTING.md` § "Cutting a release"):

```
6. git push -u origin release/v6.4.0
7. Open MR: release/v6.4.0 → main  (use the "Release" MR template)
8. Wait for CI green + review approval, then merge
9. git checkout main && git pull
10. git tag -a v6.4.0 -m "Release v6.4.0"
11. git push origin v6.4.0
12. git checkout develop && git merge --no-ff main && git push   # back-merge
```
Step 11 (tag push) triggers the GitLab `release` CI job, which runs
`release-docs-gate`, regenerates `CHANGELOG.md`, and creates the GitLab
Release from `docs/releases/v6.4.0.md`.

## Expected outputs
- Local branch `release/v6.4.0`, not pushed.
- No file changes (all release content was already committed in T285–T296).

## Acceptance criteria
1. Verify command:
   ```bash
   git branch --show-current
   ```
   Expected output: `release/v6.4.0`
2. Verify command — branch has no uncommitted changes and no divergent
   content vs. `develop` (should be the exact same tree, just a new branch
   pointer):
   ```bash
   git diff develop release/v6.4.0 --stat
   ```
   Expected output: empty (no diff).
3. Steps 3 and 4 above both completed with exit code `0`.
4. This task's final report to the user includes the verbatim "Human steps"
   block above, clearly marked as pending human action.

## Revert rule
If any verify command fails:
```bash
git checkout develop
git branch -D release/v6.4.0
```
then STOP and report. (This is the one exception where deleting a
just-created local branch is safe — it was created by this same task, never
pushed, and contains no unique commits beyond `develop`.)

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.
Never treat "ready to push/tag/merge" as a blocker to route around — it is the
correct, intended stopping point for this task.

## Execution notes
<filled during execution>
</content>
