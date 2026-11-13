# plan-159 — Dedicated runner tag for the tag-pipeline jobs (A-20, SEC-T741-17)

**Created:** 2026-11-13
**Based on:** `docs/artifacts/security-review-t741-gate-pin-v1.md` (§ 4, SEC-T741-17); `docs/plans/plan-143-batch-s-rest.md` (§ Goal); `docs/artifacts/tracked-debt-register-v16.md` (batch S, user action A-20); `.gitlab-ci.yml`; `tests/functional/test_ci_hash_pins.py`; `docs/wiki/mcp-pin-bump-checklist.md`.
**Scopes:** `T810`, `T811`.

## User decision (2026-11-13, verbatim)

The orchestrator proposed plan-159 in the session (T810 DevOps change and pins, T811 Security Engineer review, the orchestrator's verification and merge) and asked "Shall I start plan-159?". The user answered:

> start plan-159

Nothing here is a release, a tag, a probe tag or a root refresh. A probe tag needs the user's separate approval.

## Goal

SEC-T741-17 (LOW, batch S) is open in part: the two release gates already use `GIT_STRATEGY: clone` (T744), but no job carries a dedicated runner tag, because no dedicated runner existed (A-20). The user has now provided one. The three tag-pipeline jobs `release-docs-gate`, `main-develop-drift-gate` and `release` move to it, and the tag is pinned, so no branch job shares that runner's build directory or host.

## Runner facts (the orchestrator's record of what the user reported in the session, 2026-11-13)

This section is the source for these facts. None was read from GitLab or from the runner host by the orchestrator: the GitLab API returned 401 to the session's token, so every point is **(the user's report)**.

- **Host:** a new unprivileged LXC container `gitlab-runner-16028` on the user's Proxmox host, created with the script the orchestrator wrote in the session (features `nesting=1,keyctl=1`, no root password, no SSH). Docker Engine and GitLab Runner run inside it. The earlier entry for this runner on `gitlab-runner-16027` (the host whose `dind` runner binds the Docker socket) was removed and that runner restarted, per the user.
- **Runner:** project runner #59129270, description `emage-release-gate`, tag `release-gate`, online, shown locked to the project (screenshot).
- **Runner config, as the script writes and checks it:** Docker executor, `limit = 1`, `privileged = false`, `disable_cache = true`, `volumes = []`, `allowed_images = ["python:3.12-alpine@sha256:e064671ca452259bab50e8e2c7bd896e39e9a343bb06ca25234adf6fe18d0fc7"]`, no Docker socket, no shared cache. Whether the script ran to the end on the host **(unverified)**; the runner being online suggests registration ran.
- **Protected tags:** a `v*` rule, 42 matching tags, "Allowed to create: Maintainers" (screenshot).
- **Open, asked of the user:** the runner list shows "2" managers and an IP "(+1)"; whether the second is a leftover of the 16027 registration. Whether "Protected" is ticked and "Run untagged jobs" is off. Neither is visible in the screenshot.

## Task Decomposition

1. **T810** (devops-engineer): add `tags: [release-gate]` to the three tag-pipeline jobs, update their SEC-T741-17 comments, pin the tag exactly in `tests/functional/test_ci_hash_pins.py`, add a test that no other job names `release-gate`, and add to `docs/wiki/mcp-pin-bump-checklist.md` that a bump of the gate image digest must also update the runner's `allowed_images`. Brief: `docs/tasks/task-T810.md`.
2. **T811** (security-engineer), after T810: review the change and the runner setup in § Runner facts; grade findings; state whether SEC-T741-17 closes when this merges. Brief: `docs/tasks/task-T811.md`.
3. **The orchestrator:** gates, the full suite in a clean worktree, MR, merge pinned and squashed on a green pipeline.

## Constraints

- No tag, probe tag, release or project setting change; no change on any runner or host.
- No `docker` command in any brief.
- Only a tag pipeline proves the routing. If the runner is offline when a tag is pushed, the three jobs stay pending and nothing is published (fail closed).

## Outcome

**Done on 2026-11-13.** The three tag-pipeline jobs carry the dedicated runner tag, pinned; user action A-20 is closed.

- **T810** (devops-engineer), commits `ab8d02db` and `1c19caab`: `tags: ["release-gate"]` on `release-docs-gate`, `main-develop-drift-gate` and `release`, with the SEC-T741-17 comments updated; in `tests/functional/test_ci_hash_pins.py`, the tag is pinned exactly on the three jobs, and the new check `runner_tag_problems` refuses `release-gate` anywhere else in the file, a `$` in any other job's `tags`, and an `extends` of a tag job. There are 6 new tests in `TestCiReleaseGateRunnerTag`. A paragraph in `docs/wiki/mcp-pin-bump-checklist.md` § 3 says the runner's `allowed_images` must change with the tag jobs' image digest. The DevOps Engineer's mutation runs: without the tag pin, 24 subtests fail; without the new check, 13 fail.
- **T811** (security-engineer): `docs/artifacts/security-review-t811-release-gate-runner-v1.md`, **CONDITIONAL_PASS**, with one MEDIUM and four LOW findings. Its § 6 item 1 says that if the user confirms before merge that the second manager is stale and deleted and the token reset, SEC-T811-01 is resolved and the verdict becomes PASS (LOWs tracked).
- **The user's answers of 2026-11-13** (question dialog, verbatim):
  - SEC-T811-01 (delete every manager except `gitlab-runner-16028`, reset the token, re-register, confirm one manager): "Already done".
  - SEC-T811-02 ("Protected" ticked and "Run untagged jobs" off): "Yes, both".

  Both are the user's report; nobody in the session read GitLab (API 401).

**Status of findings, for register v17:**
- **SEC-T741-17:** fixed. The repository half is fixed by T810; the runner half is met by the user's report (T811 § 3). The first `v*` tag pipeline confirms it; if any of the three jobs runs on another runner or manager there, it reopens.
- **SEC-T811-01:** MEDIUM, resolved by the user's action, as reported.
- **SEC-T811-02:** LOW, resolved by the user's confirmation.
- **SEC-T811-04:** LOW, fixed by the orchestrator in `a4902de2`. That rewording of the checklist paragraph follows T811's proposed fix and was not re-reviewed: the orchestrator's ruling.
- **SEC-T811-03 and SEC-T811-05:** LOW, tracked. -03 is the routes the pin does not cover (`trigger:`, `inherit:`, `tags: []`); -05 is runner hardening leftovers.

**The orchestrator's own verification:** in the branch's YAML, `tags` appears only on `default` (`["docker"]`), `unit-tests` (`["dind"]`) and the three tag jobs (`["release-gate"]`). Test discovery finds the 6 new tests and no other difference (2741 to 2747). The gates (validate-tasks, link integrity, team health, scorecard, sync `--check`, registry `--check`), `test_ci_hash_pins` and `test_pin_bump_checklist` all exit 0. Root drift is `[]`. GitLab CI lint did not run locally (403); the merge request pipeline parses the whole file. The full suite and the pipeline are recorded in the merge request.

**Not proven until a tag pipeline:** that the jobs are picked by runner #59129270 through `gitlab-runner-16028`; the `allowed_images` match; the jobs' installs and fetches on that runner (T811 § 4). A probe tag needs the user's separate approval.

**Budgets:** T810 about 98k tokens against 60k; T811 about 96k against 60k (both counting loaded context).

**No root drift:** nothing under `implementation/knowledge/` changed.
