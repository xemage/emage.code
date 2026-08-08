# Task T341 — Add post-merge squash/ancestry verification step to `release/* → main` runbook

**ID:** T341
**Owner:** devops-engineer
**Status:** done
**Completed:** 2026-08-07
**Priority:** P2
**Depends on:** —
**Created:** 2026-08-07
**Based on:** `docs/tasks/task-T340.md` (root-cause investigation and recommendation), `docs/tasks/task-T331.md`,
`docs/tasks/task-T339.md` (both prior incidents this task aims to shorten the detection loop for)

## Objective
Add a small, scripted verification step to the `release/vX.Y.Z → main` merge procedure that
immediately checks whether GitLab silently squashed the merge despite an explicit `squash: false`
override — the confirmed root cause (T340) of the phantom-ancestry incidents in T331 and T339 — and
gives the operator a documented recovery path the moment it happens, instead of discovering it a
full release cycle later (T339's actual experience).

## Context
- Phase: Implementation (small, contained)
- Based on: T340's independently-verified finding that `6b2d680` (MR !103) and `25fa98e` (MR !109)
  are GitLab's own `squash_commit_sha` for those merges — squashing occurred both times despite
  `squash: false` being explicitly passed via `glab api -X PUT .../merge`, on a project with
  `squash_option: default_on`. T340 could not conclusively determine whether the override failing
  to take effect is a GitLab server-side quirk or a client-serialization issue — this task does not
  need to resolve that; it only needs to detect the symptom reliably, which it can do regardless of
  cause.
- T340 explicitly recommended this as the *cheapest, first* remediation option — not the heavier
  options (bypass `/merge` via direct push to `main`, which weakens the `push=[No one]` protection;
  or disable `squash_option` project-wide, which would remove squash-and-merge for every other MR
  type too). Those heavier options are explicitly deferred pending evidence that this cheap option
  is insufficient, and are out of scope for this task.
- plan-019's `main-develop-drift-gate` (already shipped, `scripts/check-main-develop-drift.py`)
  remains the correct, unaffected mitigation for the *user-visible* symptom (content drift). This
  task does not touch that mechanism — it targets the underlying ancestry corruption at its source,
  one layer earlier.

## Inputs
- `docs/tasks/task-T340.md` § Findings — full mechanism, evidence, and citations
- `docs/tasks/task-T331.md`, `docs/tasks/task-T339.md` — the two incidents this shortens detection
  for
- `CONTRIBUTING.md` § Releasing — existing release procedure documentation (already has a "Drift
  detection" subsection from T335; this task adds a sibling subsection, does not replace it)
- GitLab merge-request API: `GET projects/:id/merge_requests/:iid` (fields to check:
  `squash`, `squash_commit_sha`, `merge_commit_sha`, `sha`)

## Constraints
- Scope is deliberately small: a verification step + a documented manual recovery procedure. **Do
  not** build a new CI gate, a branch-protection change, or anything that bypasses the `/merge` API
  — those are explicitly deferred per T340's recommendation.
- No change to `scripts/check-main-develop-drift.py` or its CI jobs (plan-019) — this is a
  different, earlier failure point (ancestry corruption at merge time, not content drift detected
  later).
- Token budget: ≤ 60k (this repo's Implementation tier is ≤120k, but this task's scope is small —
  budget conservatively per its actual size).
- Follow `.claude/rules/git-workflow.md`: branch from `develop` as `bugfix/341-post-merge-squash-verification`
  (this is a process/tooling fix, not a new capability — `bugfix/*` naming applies), open an MR to
  `develop`, do not touch `main` directly.

## Expected Outputs
- A small script or documented shell snippet (e.g. `scripts/verify-main-sync-merge.sh` or
  equivalent — implementer's choice, but it must be runnable non-interactively and take the MR IID
  as an argument) that: calls `GET projects/:id/merge_requests/:iid`, asserts `squash == false` and
  `squash_commit_sha == null`, and exits non-zero with a clear message if the assertion fails.
- A new subsection in `CONTRIBUTING.md` § Releasing (sibling to the existing "Drift detection"
  subsection) documenting: (a) when to run the verification (immediately after every
  `release/vX.Y.Z → main` merge, before considering the sync complete), (b) what a failure means
  (GitLab squashed despite the override — cite T340 for why this can happen), (c) the recovery
  procedure (open a small "ancestry restore" follow-up MR so the next sync's `merge-base` is
  correct — the exact mechanics T340 §4 option 1 sketched: a no-op commit on `main` with the true
  source tip as an explicit second parent).
- Task brief updated with an `## Outcome` section on completion, per this repo's standing pattern.

## Acceptance Criteria
- [x] Verification step runnable against a real MR IID and correctly distinguishes a genuine
      non-squashed merge (`squash: false`, no `squash_commit_sha`) from a squashed one, tested
      against the historical MR !103 and MR !109 records (both should FAIL the check, reproducing
      T340's finding) as a regression fixture — not just asserted to work
- [x] `CONTRIBUTING.md` subsection added, consistent in tone/format with the existing "Drift
      detection" subsection (T335's precedent)
- [x] No changes to `scripts/check-main-develop-drift.py`, its CI jobs, or any file outside this
      task's stated scope
- [x] Full local test suite still green after the change (functional suite; see Outcome for the
      one pre-existing, unrelated performance-suite failure and why it is out of this task's scope)
- [x] MR opened `bugfix/341-post-merge-squash-verification → develop`, not touching `main`

## Blocker Protocol
Report blockers per `AGENTS.md`: type (`technical` | `dependency` | `unclear_requirements` |
`external`) + severity (`critical` | `major` | `minor`). Max 2 retries before escalating to the
orchestrator. If the GitLab API's field names or semantics differ from what T340 documented (e.g.
API version drift), report as a `technical`/`minor` blocker rather than guessing at a fix.

## Outcome (2026-08-07)

### Artifacts produced
- `scripts/verify-main-sync-merge.py` — CLI script, takes an MR IID, calls
  `GET projects/:id/merge_requests/:iid` via `glab api`, asserts `squash == false` and
  `squash_commit_sha == null`. Exit codes: `0` verified-clean, `1` GitLab squashed despite the
  override, `2` tooling/lookup error (bad IID, `glab` missing, malformed response).
- `tests/functional/test_verify_main_sync_merge.py` — regression fixture using the exact MR !103
  / !109 API field values from `docs/tasks/task-T340.md` § Findings §2, plus a genuine-non-squash
  positive case, two edge cases (squash flag and squash_commit_sha disagreeing), and coverage for
  a `glab api`-quirk bug found during manual live testing (see below).
- `CONTRIBUTING.md` — new "Post-merge squash verification" subsection under § Releasing, sibling
  to "Drift detection", before "Hotfixes".

### Setup note (worktree state)
This task's assigned worktree (`.claude/worktrees/agent-a8e4f8825b4bcba2d`) was, at task start,
checked out on a branch (`worktree-agent-a8e4f8825b4bcba2d`) built from an old, unrelated point in
`main`'s history (tip `c14bf79`) rather than from the `develop` tip that contains this task's own
brief, T340's findings, and `CONTRIBUTING.md`'s current "Drift detection" section — none of those
files existed on that branch. The repo's local `develop` branch (checked out in the primary
worktree at `/home/emage/Code/emage/emage.code`, tip `f20c86b`, containing this file) had
everything needed. Resolved by creating `bugfix/341-post-merge-squash-verification` directly from
local `develop` tip (`git checkout -b bugfix/341-post-merge-squash-verification develop`) inside
this worktree, per `.claude/rules/git-workflow.md`'s "branch from develop" requirement — this does
not check out `develop` itself in two worktrees at once (which git disallows), only a new branch
from its tip. Not treated as a blocker since it was self-resolvable without ambiguity or guessing
at file content.

### Acceptance criteria verification (exact commands + output)

**1. Regression fixture against MR !103 / !109 (fixture-based, matches this repo's mocking
convention in `tests/functional/test_check_main_develop_drift.py`):**
```
$ python3 tests/run.py --suite functional
...
test_mr_103_fails_check (tests.functional.test_verify_main_sync_merge.TestEvaluateRegressionMR103.test_mr_103_fails_check) ... ok
test_mr_109_fails_check (tests.functional.test_verify_main_sync_merge.TestEvaluateRegressionMR109.test_mr_109_fails_check) ... ok
...
Ran 275 tests in 7.740s
OK (skipped=17)
```
Also independently verified live against the real GitLab API (beyond the acceptance criterion's
minimum bar, not fixture-only):
```
$ python3 scripts/verify-main-sync-merge.py 103
verify-main-sync-merge: MR !103 FAIL — GitLab squashed this merge despite the override (squash=True, squash_commit_sha=6b2d680c5499d0e12f1e4c9f910bcfc2984728d6)
...
EXIT=1

$ python3 scripts/verify-main-sync-merge.py 109
verify-main-sync-merge: MR !109 FAIL — GitLab squashed this merge despite the override (squash=True, squash_commit_sha=25fa98efe5c8c9aea9a72d40b9de651d085a1e7b)
...
EXIT=1
```
Both exactly reproduce T340's finding, live, not just against the fixture.

While doing this live verification, found and fixed a real bug: `glab api` exits `0` even on HTTP
errors (a bad IID returns `{"message":"404 Not found"}` on stdout with exit code `0`). Without a
fix, `fetch_mr` would have misread that error body as a valid MR record and falsely reported
"squashed" for a merely-nonexistent IID. Fixed by detecting the error-body shape explicitly
(`"iid" not in data`) and returning an `ERROR`/exit-2 lookup failure instead:
```
$ python3 scripts/verify-main-sync-merge.py 999999
ERROR: unexpected merge request response for IID 999999 (not a valid MR record): {"message":"404 Not found"}
EXIT=2
```
Covered by `TestFetchMrErrorShapes` in the new test file.

**2. `CONTRIBUTING.md` subsection:** added as a sibling to "Drift detection", before "Hotfixes",
matching its structure (when to run / what a failure means / recovery procedure), citing
`docs/tasks/task-T340.md` § Findings §2–4 and `docs/tasks/task-T339.md`.

**3. No changes outside scope:**
```
$ git diff --stat develop...bugfix/341-post-merge-squash-verification
 CONTRIBUTING.md                                 |  44 +++++++
 scripts/verify-main-sync-merge.py               | 140 ++++++++++++++++++++++
 tests/functional/test_verify_main_sync_merge.py | 148 ++++++++++++++++++++++++
 3 files changed, 332 insertions(+)
```
`scripts/check-main-develop-drift.py` and `.gitlab-ci.yml`: untouched (confirmed via the diff
above — neither file appears).

**4. Full local test suite:**
```
$ python3 tests/run.py --suite functional
Ran 275 tests in 7.740s
OK (skipped=17)

$ python3 tests/run.py            # functional + performance combined
Ran 293 tests in 14.364s
FAILED (failures=1, skipped=17)
FAIL: test_every_active_task_has_a_plan (tests.performance.test_team_health.TestPlanCoverage.test_every_active_task_has_a_plan)
AssertionError: ['T341'] is not false : Active tasks not referenced by any plan in docs/plans/ ...
```
This single failure is **pre-existing and out of this task's scope**: independently reproduced on
clean `develop` tip (`f20c86b`) via `git stash -u` (removing this task's new/untracked files) then
re-running `python3 tests/run.py --suite performance` — same failure, same message, before any of
this task's changes existed. It flags that `docs/tasks/task-T341.md` (this task itself) isn't yet
referenced by any file under `docs/plans/` — filing a plan document for T341 is not among this
task's Expected Outputs and is not something this task's brief asked for; it is the
orchestrator's/Plan-Approve-Execute process's responsibility, not this task's. Recommend the
orchestrator either add a plan reference for T341 or confirm this is acceptable for a P2-scoped
verification task before closing the ledger row.

**5. MR opened, `develop` target, `main` untouched:**
```
$ git push -u origin bugfix/341-post-merge-squash-verification
$ glab mr create --source-branch bugfix/341-post-merge-squash-verification --target-branch develop ...
https://gitlab.com/em-age/emage.code/-/merge_requests/111

$ glab api projects/:id/merge_requests/111
"state": "opened", "web_url": "https://gitlab.com/em-age/emage.code/-/merge_requests/111",
"source_branch": "bugfix/341-post-merge-squash-verification", "target_branch": "develop"
```
MR **not** merged (per this task's acceptance criteria, which stop at "MR opened") — awaiting
review/approval per `.claude/rules/git-workflow.md`. `main` was never checked out, committed to,
or pushed to during this task.

### Concerns / follow-up for the orchestrator
1. The pre-existing `test_every_active_task_has_a_plan` failure (see §4 above) — a plan-doc
   reference decision, not a code fix, needed before the ledger can show a fully green combined
   suite.
2. The worktree setup note above (stale worktree branch) — flagging in case other in-flight agent
   worktrees have the same stale-branch condition and would hit the same issue.
3. Per delegation: `active-tasks.md` and `completed-tasks.md` intentionally left untouched — for
   the orchestrator to transition after independently reviewing MR !111 and this Outcome section's
   evidence.

### Orchestrator closeout (2026-08-07)
- Independently re-verified the agent's work: read `scripts/verify-main-sync-merge.py` in full,
  ran it live against the real API myself (`python3 scripts/verify-main-sync-merge.py 103` and
  `109` both correctly FAIL, matching T340's finding; a bad IID correctly exits 2), and read the
  new `CONTRIBUTING.md` subsection in full.
- Filed `docs/plans/plan-021-post-merge-squash-verification.md` to resolve concern #1 above
  (`test_every_active_task_has_a_plan` requires every active task ID to appear in some
  `docs/plans/*.md` file) — pushed directly to `bugfix/341-post-merge-squash-verification`, which
  fixed the `unit-tests` job on the MR pipeline.
- CI infrastructure incident: the MR pipeline hit a genuine stuck-runner condition unrelated to
  this task's diff — every job lacking a per-job `image:` override (inheriting
  `.gitlab-ci.yml`'s `default: image: node:20-alpine`) hung indefinitely (`verify-knowledge-drift`
  ran 16+ min with zero trace output before a `markdown-links` retry finally failed with GitLab's
  own `no_updates_running` reason), while jobs with an explicit `image: python:3.12-alpine`
  succeeded in single-digit seconds throughout — a clean split pointing at the runner's Docker
  daemon being wedged specifically on `node:20-alpine`, not at anything in this MR. Cancel
  requests did not take effect for over 30 minutes (consistent with a genuinely unresponsive
  runner agent, not just a slow job). User confirmed the GitLab runners were fixed
  (infra-side, outside this repo); a fresh MR pipeline
  (`https://gitlab.com/em-age/emage.code/-/pipelines/2742737626`) then ran clean end-to-end
  (`sync-no-diff` 8.1s, `validation-super-gate` 12.7s, `verify-knowledge-drift` 6.3s, `unit-tests`
  39.1s, `markdown-links` 5.7s — all normal durations, all `success`).
- MR !111 merged (squash, source branch removed):
  `merge_commit_sha: 9452c0756eac637e3f859032fb457ffb172ace04`, target `develop`, `main` untouched
  throughout.
- Local `develop` synchronized: the branch's history contains a squash commit, so local `develop`
  (which had 2 of the same-content commits from earlier local work, never pushed since `develop`
  is protected against direct push) was reset to `origin/develop` after confirming via
  `git diff origin/develop develop` that local held nothing origin didn't already have.
- Worktree and branches cleaned up: `.claude/worktrees/agent-a8e4f8825b4bcba2d` removed, local and
  remote `bugfix/341-post-merge-squash-verification` deleted.
- Concern #2 (worktree branched from a stale point instead of `develop`) has now recurred across
  at least two consecutive agent dispatches (T340 and T341) — worth a dedicated look at how this
  session's worktree-creation step picks its base ref, though not urgent since it has been
  self-resolvable by the dispatched agent each time.
