# Artifact: security-review-t811-release-gate-runner-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T811 (plan-159). **Gate**: security. **Date**: 2026-11-13.
- **Reviewer**: security-engineer agent, read-only, no shell. The orchestrator recorded this artifact from the agent's report.
- **Target**: T810, branch `agent/devops-engineer/T810`. The change is commits `ab8d02db` and `1c19caab` on `b1915b90`, read as the diff file `t811-diff.patch` that the orchestrator supplied. Files: `.gitlab-ci.yml`, `tests/functional/test_ci_hash_pins.py`, `docs/wiki/mcp-pin-bump-checklist.md`.
- **Based on**:
  - `docs/tasks/task-T811.md`
  - `docs/plans/plan-159-release-gate-runner-tag.md` (§ Runner facts; every runner fact there is the user's report)
  - `docs/artifacts/security-review-t741-gate-pin-v1.md` § 2 and § 4 (SEC-T741-12, -16, -17)
  - `.gitlab-ci.yml` in full on the branch
  - `tests/functional/test_ci_hash_pins.py` on the branch, lines 360-409 and the diff
- **User's word for the plan (verbatim)**: "start plan-159".
- **Tools**: Read only. `grep_content` refuses a worktree path, so one search ran on `develop`'s copy of `test_ci_hash_pins.py` (for `inherit`, `trigger`, `services`, `DEFAULT_TAGS`) and was checked against the branch file with Read. No dependency changed, so no audit ran.
- **Orchestrator's checks** (reported by the orchestrator; the reviewer did not run them):
  - Parsed with PyYAML, the branch file has `tags` in exactly five places: `default` (`["docker"]`), `unit-tests` (`["dind"]`), and each of the three tag jobs (`["release-gate"]`).
  - These all exit 0: validate-tasks, link integrity, team health, scorecard, sync `--check`, registry `--check`, `tests.functional.test_ci_hash_pins` and `test_pin_bump_checklist`.
  - Root drift is `[]`.
  - GitLab CI lint did not run: it returned 403 to the DevOps Engineer, and the branch is not pushed yet.
  - The DevOps Engineer reports mutation runs: removing the tag pin fails 24 subtests, and removing `runner_tag_problems` fails 13.

## Verdict: CONDITIONAL_PASS

- **Counts**: 0 CRITICAL, 0 HIGH, 1 MEDIUM (SEC-T811-01, a condition with a remediation plan below), 4 LOW.
- **No breach**: no Immutable Security Constraint is broken, and no required control is removed or weakened. The change adds a control.
- **No regression**: before this change, the tag jobs ran on any runner tagged `docker`. Nothing below is worse than that.
- **Why not PASS**: the runner's isolation rests on settings that nobody in the session could read, and on one runner token that was present for a while on the host whose `dind` runner binds the Docker socket.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 | 0 | 1 (SEC-T811-01, condition) |
| LOW | 4 | 0 | 4 (track as debt) |

## 1. Rulings on the change

- **The three tag jobs.** Each carries `tags: ["release-gate"]`, and `tags` is now in `GATE_KEYS`. Each job's value is pinned exactly to `RELEASE_GATE_TAGS`. A job-level `tags` replaces `default.tags`, and `default.tags` stays pinned to `["docker"]` (`file_level_problems`). So a tag job can only be offered to runners that hold the tag `release-gate`. Correct.
- **`runner_tag_problems`.** It walks the parsed values of every top-level key except the three pinned jobs, so it also covers `default`, the file-level `variables`, `stages` and hidden jobs. Checked route by route:
  - **The name in a job's `tags`**: caught, including through a YAML alias, because aliases resolve into the parsed value.
  - **The name anywhere else**, such as a variable value or a `parallel:matrix` value: caught by the substring check. False positives are harmless.
  - **A `$` in another job's `tags`**, as a list item or a plain string: caught. This blocks expansion from job, file, project, group and pipeline variables and from `parallel:matrix`.
  - **`extends`** of a tag job, at any depth: caught, because each hidden link in the chain is walked too.
  - **`!reference`**: already refused anywhere in the file as an explicit YAML tag (SEC-T741-09).
  - **`include:`**: already refused at the top level (SEC-T741-03).
  - **Route not covered:** the gaps are in SEC-T811-03.
- **Comments and checklist.** They are accurate, except for one overclaim (SEC-T811-04).
- **A limit of the pin, not new.** The pin tests the file in the pipeline that GitLab runs. It cannot stop a job in the branch pipeline that carries the edit: that job runs before `unit-tests` reports. Only the runner's "Protected" setting keeps unmerged CI files off this runner (SEC-T811-02).

## 2. Findings

| Id | Grade | Location | Description | Proposed fix |
|---|---|---|---|---|
| SEC-T811-01 | MEDIUM (A05/A08) | Runner #59129270 (user side); plan-159 § Runner facts | **Second manager.** The runner list shows 2 managers ("(+1)"), and the runner's authentication token was first registered on `gitlab-runner-16027`. On that host, branch jobs (`unit-tests`, tag `dind`) bind the host Docker socket, which gives root on that host's daemon and files. **Risk if the second manager is live, or if the token was read there:** whoever holds the token can poll as `release-gate` and receive the `release` job, which includes its `CI_JOB_TOKEN`, the release content and the gate verdicts. A live manager on 16027 would also put the release job next to socket-binding branch jobs, which is exactly what SEC-T741-17 is meant to prevent. **Likelihood:** low. The user reports that the 16027 entry was removed, the "(+1)" is probably a stale record, and only project members can push branches **(unverified)**. | **Owner:** the user. **Before the next `v*` tag:** (1) check each manager's "last contact" and delete any manager other than `gitlab-runner-16028`; (2) **reset the runner authentication token** (GitLab UI, runner → reset token, or delete and re-create the runner), then re-register on 16028 only; (3) confirm one manager. **Deadline:** before the first tag push after merge. A remediation plan, not a merge block. |
| SEC-T811-02 | LOW (A05) | Runner settings (user side) | **"Protected" and "Run untagged jobs" are unconfirmed.** If "Protected" is off, any project member can push a branch whose `.gitlab-ci.yml` names `release-gate`, and that job runs on this runner. The pin fails only later, in that same pipeline. What a hostile job could still do there: no socket, no cache, no volumes, `limit = 1` and `allowed_images` leave only a container-escape attempt (SEC-T811-05) and blocking the runner. If "Run untagged jobs" is on, an untagged job can land there (see SEC-T811-03). | **Owner:** the user. Tick "Protected" and turn "Run untagged jobs" off. With "Protected" on, only `main`, `develop` and the protected `v*` tags reach the runner. Record the confirmation in the register. |
| SEC-T811-03 | LOW (A08) | `runner_tag_problems`, `tests/functional/test_ci_hash_pins.py` | **Three routes the pin does not cover** **(GitLab behaviour from memory, unverified)**: (a) **`trigger:`** child pipelines: a job-level `trigger: include:` names a local file, or an artifact a script generates at run time. Neither file is pinned, and a child pipeline on `develop` or `main` is on a protected ref. (b) **`inherit: default: false`**, or an `inherit:default` list without `tags`: the job drops `default.tags`. (c) **`tags: []`** on a job. (b) and (c) produce untagged jobs, and the real file has none of the three. These routes need a merged CI edit, which merge request review would see. (b) and (c) also need "Run untagged jobs" on. | Refuse the key `trigger` and the key `inherit` in every job, hidden ones included. Refuse a `tags` value outside the tag jobs that is not a non-empty list of literal strings. Add one mutation test for each. |
| SEC-T811-04 | LOW (wording) | `docs/wiki/mcp-pin-bump-checklist.md` (new paragraph) | "run only on the user's dedicated project runner" goes further than the pin proves. The pin proves only that the jobs need a runner tagged `release-gate`. That only this runner holds that tag, with one manager, is the user's report **(unverified)**: see SEC-T811-01, and group or instance runners available to the project. | Reword to "need a runner tagged `release-gate`; by the user's report only the dedicated project runner carries it". Optionally add "keep instance and group runners free of that tag". |
| SEC-T811-05 | LOW (A05) | Runner `config.toml` and LXC (user side) | **Runner hardening residuals:** (a) **Services:** `allowed_services` is not set, so any service image is allowed **(runner behaviour from memory, unverified)**. The tag jobs cannot add `services` (keys allowlist), so this matters only for a job that reaches the runner by another route. (b) **Escape surface:** a container escape via runc, kernel or Docker Engine gives uid-mapped root in the unprivileged LXC. From there, an attacker reads the runner token and every later release job's `CI_JOB_TOKEN`, though not root on the Proxmox host. `nesting=1,keyctl=1` widen the kernel surface a little. (c) **Fail-closed coupling:** `allowed_images` is maintained by hand at each image bump; this is documented, and a missed update stops a release (fail closed) rather than weakening anything. | Restrict services with `services_limit = 0` or with `allowed_services` set to the one digest **(option names from memory, verify against the installed runner version)**. Keep Docker Engine, GitLab Runner and the PVE kernel patched on the image-review cadence (`ci_images_reviewed_on`). Run nothing else in that LXC. |

**Grading notes.**
- **SEC-T811-01** is MEDIUM rather than LOW for two reasons: the impact is the job that publishes with the token, and the token sat on a host where branch jobs have socket-level root. If the user finds a live manager on any host that runs branch jobs, regrade it HIGH and do not push a `v*` tag until it is removed and the token is reset.
- **SEC-T811-02 and -05** are LOW, because the runner keeps no state between jobs: `disable_cache = true`, `volumes = []`, no socket, and the image is pinned by digest, so it is content-addressed.

## 3. Status of SEC-T741-17 after merge

- **What the merge completes:** the repository half. `GIT_STRATEGY: clone` is on all three tag jobs (T744, T750), a dedicated runner tag is on all three (T810), and both are pinned exactly.
- **What it does not complete:** the runner half, which depends on user-side facts that no one in the session read.
- **Proposed register status:** "fixed in the repository; open on runner confirmation". It closes when both hold:
  1. SEC-T811-01 is done: one manager (16028) and a reset token.
  2. The user confirms SEC-T811-02: "Protected" on and "Run untagged jobs" off.
- **Afterwards:** the first `v*` tag pipeline confirms the closure. If that pipeline shows any of the three jobs on another runner or manager, SEC-T741-17 reopens.

## 4. What only a tag pipeline proves

- **Routing:** each of the three jobs is picked by runner #59129270 through the `gitlab-runner-16028` manager. Read the job log header (runner description and short token) and the runner's job list.
- **Image allowlist:** `allowed_images` accepts the exact `python:3.12-alpine@sha256:e064671c…` string.
- **The jobs run in Docker inside the unprivileged LXC:**
  - `apk add` and the hash-locked `pip install` succeed, with egress to the Alpine mirrors and PyPI.
  - `rm -rf .git "${CI_PROJECT_DIR}.tmp"` still removes the clone credential (T750 relied on GitLab Runner 19.5.2 source; this runner's version is unknown).
  - The `main-develop-drift-gate` fetches authenticate with `CI_JOB_TOKEN`, under this runner's `FF_GIT_URLS_WITHOUT_TOKENS` default.
- **Publishing:** `release` publishes, and its `CHANGELOG.md` artifact uploads.
- **Ordering:** `limit = 1` serialises the two gates and `release`, and each stays inside its timeout (queue time does not count).
- **Not tag-only:** that GitLab accepts the YAML is shown by the merge request pipeline, which parses the whole file, tag jobs included. A probe tag needs the user's separate approval (plan-159 § User decision).

## 5. Not verified

- **Runner facts:** every fact in plan-159 § Runner facts is the user's report or a screenshot: the LXC features, the `config.toml` values, that the setup script ran to the end, the runner being locked, and the protected `v*` rule. In particular:
  - what the second manager is;
  - whether "Protected" is ticked and "Run untagged jobs" is off;
  - whether any group or instance runner available to the project carries `release-gate`;
  - the runner's version.
- **GitLab and runner behaviour, from memory:**
  - `tags: []` and `inherit: default` producing untagged jobs;
  - child pipelines from a protected ref counting as protected for runner selection;
  - `allowed_services` and `services_limit` semantics;
  - whether stale runner managers are cleaned up automatically.
- **CI lint:** not run (403). The orchestrator's PyYAML result for `tags` is the orchestrator's check.
- **Mutation runs:** the counts are the DevOps Engineer's report.
- **Project settings, still open from T741 § 5:** who can merge to `develop` and `main` and whether approvals are enforced; the configured CI file path; whether `WIKI_TOKEN` is flagged protected (if it is, it is injected into the tag jobs on this runner; this is unchanged by T810).

## 6. Needs the user's word

1. **SEC-T811-01:** the user should accept being its owner, then check the managers and reset the runner token before the next `v*` tag. If the user confirms before merge that the second manager is stale and has been deleted, and that the token was reset, SEC-T811-01 is resolved and this verdict becomes PASS (LOWs tracked).
2. **SEC-T811-02:** the user confirms the "Protected" and "Run untagged jobs" settings. This is the plan's open question.
3. **Probe tag:** any tag or probe tag to prove the routing needs the user's separate approval.
4. **No user decision needed:** SEC-T811-03 and -04 are repository follow-ups (owner devops-engineer, proposed; tracked as LOW debt), and the orchestrator can route them.

## 7. OWASP coverage

| Category | Reviewed | Findings |
|---|---|---|
| A01 Broken Access Control | Yes | 0 (the runner's protected and locked state is covered under A05) |
| A02 Cryptographic Failures | Yes | 0 |
| A03 Injection | Yes | 0 (variable expansion in `tags` refused) |
| A04 Insecure Design | Yes | 0 |
| A05 Security Misconfiguration | Yes | 3 (SEC-T811-01, -02, -05) |
| A06 Vulnerable Components | Yes | 0 (no dependency changed; no audit ran) |
| A07 Auth Failures | Yes | 0 (token reset is part of SEC-T811-01) |
| A08 Data Integrity Failures | Yes | 1 (SEC-T811-03) and SEC-T811-01 (release integrity) |
| A09 Logging & Monitoring | Yes | 0 |
| A10 SSRF | Yes | 0 |

SEC-T811-04 is a wording finding with no OWASP category.

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 | 0 | 1 |
| LOW | 4 | 0 | 4 |

### Justification
- **Positive:** the change is correct, it is pinned with mutation-tested checks, and it closes the repository half of SEC-T741-17.
- **Condition:** SEC-T811-01 (MEDIUM) has a remediation plan and is owned on the user side.
- **LOWs:** SEC-T811-02 and -05 are runner settings. SEC-T811-03 and -04 are repository follow-ups.

### Conditions
- **SEC-T811-01:** owner=@user (owner the user still has to accept); remediation=delete every manager except `gitlab-runner-16028`, reset the runner authentication token, confirm one manager; deadline=before the first `v*` tag push after merge.
- **SEC-T811-02:** owner=@user; remediation=confirm "Protected" on and "Run untagged jobs" off; deadline=before the first `v*` tag push after merge (LOW, tracked).
- **SEC-T811-03 and -04:** owner=@devops-engineer (proposed); remediation=as in the table; deadline=next register batch (LOW, tracked as debt).
- **SEC-T811-05:** owner=@user; remediation=as in the table; deadline=next runner maintenance (LOW, tracked as debt).

### Blockers
None.
