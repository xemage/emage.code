# Artifact: release-rehearsal-t706-v1.md

> Immutable once produced; revisions bump `<N>`.

**Based on:** `docs/tasks/task-T706.md`; `docs/plans/plan-124-release-v9.md` (T706); `docs/artifacts/release-rehearsal-t647-v1.md` (the v8.0.0 rehearsal, the model followed); `docs/artifacts/release-v9-audit-v1.md` §5; `.gitlab-ci.yml` (`release`, `main-develop-drift-gate`, read); `scripts/publish-release.py`, `scripts/check-release-tag-tree.py`, `scripts/check-main-develop-drift.py` (read, then run); `docs/releases/v9.0.0.md`. All inputs as of `release/v9.0.0` at `ca11bb6e`.

**Author / mode:** DevOps Engineer, T706. Only this file was added to the repository. Nothing was pushed, no tag or release was created on any GitLab project, no API call was made with any token (real or dummy), and no real token was used or read. The tag `v9.0.0` existed only inside a scratch container and was destroyed with it. `tests/golden/held-out/` was not checked out (sparse checkout) and not opened. The scratch container was removed at the end; the pulled image stays in the remote daemon's cache.

**Basis marker:** **(V)** = run or read in this task. **(unverified)** = not checked.

## 1. Result

**PASS for the rehearsal's question.** I ran the job's own `before_script` line verbatim in the real, digest-pinned job image, then the job's `script` line verbatim plus `--skip-api`, with a scratch-only annotated tag `v9.0.0` on `release/v9.0.0` (`ca11bb6e`). Both exit 0. The git commands the script uses (`fetch`, `rev-parse --is-shallow-repository`, `tag --sort=-v:refname`, `merge-base --end-of-options`, `rev-list --count --end-of-options`, `log --no-merges --end-of-options <rev> --`) all work in the image's git 2.54.0. The release description that `main()` would hand to the API equals `docs/releases/v9.0.0.md` **byte for byte** (49815 bytes, sha256 `017260f1db18dfdb6c368c34657d503dc511c0eb34074edf830a8b6e101427fd`). The generated `CHANGELOG.md` entry lists exactly the 49 non-merge subjects of `v8.0.0..v9.0.0` and no merge commit. No git or apk child process received any variable whose value held the (dummy) job token. The T686 tag-tree check fails against today's `origin/main`, as it must before the merge, and passes against a simulated merge of the release into `main`.

## 2. Environment (V)

| Item | Value |
|---|---|
| Job image (`release`, `.gitlab-ci.yml:218`) | `python:3.12-alpine@sha256:92abd2ba1bdfb48b1e2ac224b582dd1558d0d4bb11c903b126b5bf9c448fd656` (image created 2026-10-21), pulled by digest |
| In that image after the `before_script` | **git 2.54.0** (`git~=2.54` resolved to `2.54.0-r0`), Python 3.12.15, Alpine 3.24.3, uid 0 |
| Host git (independent cross-check only) | 2.43.0 |
| Docker | client 29.1.3, server 29.9.2, remote daemon (`DOCKER_HOST` over ssh); no bind mounts were used. A git bundle of `origin/release/v9.0.0`, `origin/main`, `origin/develop` and all tags (7.98 MB) and the helper scripts went in with `docker cp` |
| Network | connected only for the `before_script` (`apk add`, Alpine mirror); then `docker network disconnect bridge` before any repository step, so no later step could reach any host |
| Dummy CI variables (names; values were the marker `DUMMY-T706-TOKEN`, never a real token) | `CI_JOB_TOKEN`, `CI_REGISTRY_PASSWORD` (same value), `CI_REPOSITORY_URL` (`https://gitlab-ci-token:<marker>@gitlab.invalid/...`), `WIKI_TOKEN` (`<marker>-WIKI`); plus `CI=true`, `GITLAB_CI=true`, `CI_COMMIT_TAG=v9.0.0`, `CI_SERVER_HOST=gitlab.invalid`, `CI_API_V4_URL=https://gitlab.invalid/api/v4`, `CI_PROJECT_ID=1`, `LC_ALL=C.UTF-8` |
| Env probes | `/wrap/git` and `/wrap/apk` placed first on `PATH`. Each logs the variable names it receives and the count of variables holding the marker, then `exec`s the real binary (`/usr/bin/git`, `/sbin/apk`) |

## 3. Scratch repository (V)

- Bare origin `/origin.git` in the container, filled from the bundle: `refs/heads/release/v9.0.0` = `ca11bb6`, `refs/heads/main` = `8f829a6` (the v8.0.0 main), `refs/heads/develop` = `61098c3`, all real tags (newest real tag `v8.0.0`, annotated).
- Fake tag: `git tag -a -m '... scratch only' v9.0.0 refs/heads/release/v9.0.0` in that origin, exit 0. The tag name has to be `v9.0.0` because the script loads `docs/releases/<tag>.md`. A name such as `v9.0.0-rehearsal` would only test the missing-document path (that path is case B in section 6).
- Runner-style `GIT_DEPTH: "0"` checkout: `git clone --no-checkout file:///origin.git /build`, sparse checkout `'/*' '!/tests/golden/held-out/'`, `git checkout --detach v9.0.0`, all exit 0; `HEAD` = `ca11bb6e…`, not shallow, clean status. The sparse pattern changes only the working files, not the history or the tree ids the scripts read.

## 4. Commands and exit codes (V)

### 4.1 `before_script` (verbatim; `diff` against `.gitlab-ci.yml:222` was empty)

| Command | Exit | Output |
|---|---|---|
| the `python3 -I -c "... apk add --no-cache git~=2.54 ..."` line | 0 | 12 packages, `git-init-template (2.54.0-r0)` among them |
| apk env probe | — | apk received `HOME LANG LC_ALL PATH` (+ `PWD SHLVL` from the probe's own shell); **0** variables holding the marker |

### 4.2 Git commands, run directly in `/build`

| Command | Exit | Result |
|---|---|---|
| `git tag --sort=-v:refname` | 0 | `v9.0.0`, `v8.0.0`, `v7.0.1`, … |
| `git merge-base --end-of-options v8.0.0 v9.0.0` | 0 | `6630dd0e…` (the v8.0.0 tag commit) |
| `git rev-list --count --end-of-options <base>..v9.0.0` / `v8.0.0..v9.0.0` | 0 / 0 | 90 / 90 (equal, so the script uses `<base>..v9.0.0`) |
| `git log --no-merges --pretty=%s --end-of-options <base>..v9.0.0 --` | 0 | 49 subjects |
| the same without `--no-merges` | 0 | 90 subjects (41 merge commits excluded by the flag) |

### 4.3 The job's `script` line plus `--skip-api`

```
python3 scripts/publish-release.py --tag "${CI_COMMIT_TAG}" --api-v4-url "${CI_API_V4_URL}" --expected-host "${CI_SERVER_HOST}" --project-id "${CI_PROJECT_ID}" --token-env CI_JOB_TOKEN --token-header JOB-TOKEN --skip-api
release-publish: regenerated CHANGELOG.md for v9.0.0
release-publish: skipped GitLab API publish by request                       (exit 0)
```

`git status --short` afterwards shows only ` M CHANGELOG.md`. A second run exits 0 and leaves `CHANGELOG.md` byte-identical (`cmp` exit 0), so the script is idempotent.

**Child environment (V).** Across both runs the script made 14 git calls (`fetch` 2, `rev-parse` 2, `tag` 2, `merge-base` 2, `rev-list` 4, `log` 2). Every call received only `HOME LANG LC_ALL PATH` (+ `PWD SHLVL` from the probe), with **0** variables holding the marker each time. `CI_JOB_TOKEN`, `CI_REGISTRY_PASSWORD`, `CI_REPOSITORY_URL`, `WIKI_TOKEN` and all other `CI_*` variables were absent. Control: one unfiltered `git status` from my own shell, through the same probe, saw all 21 variables and 4 marker hits. The probe therefore detects a leak when one is present.

### 4.4 Release body (the API half, API replaced by a capture)

`--skip-api` does not build the request, so I loaded the clone's own `scripts/publish-release.py` with `importlib` and replaced `create_or_update_release` by a function that records its keyword arguments. I also replaced `urllib.request.urlopen` by a function that aborts, and the container had no network. Then I called `main()` with the job's exact argv **without** `--skip-api` and `CI_JOB_TOKEN` set to the dummy marker.

| Check | Exit / result |
|---|---|
| `main()` | rc 0; printed `published GitLab release for v9.0.0` (the stub, no request) |
| arguments handed to the API function | `token_header='JOB-TOKEN'`, token = the dummy from `CI_JOB_TOKEN` (resolved by name, not from argv), `expected_host='gitlab.invalid'`, `tag='v9.0.0'`, `project_id='1'` |
| `WITHHELD_ENV_NAMES` after `main()` | `['CI_JOB_TOKEN', 'WIKI_TOKEN']` |
| `cmp <captured description> docs/releases/v9.0.0.md` | **0, byte-identical**; sha256 of both `017260f1db18dfdb6c368c34657d503dc511c0eb34074edf830a8b6e101427fd`, 49815 bytes; same sha256 as the host worktree's file |

There is no difference to explain. The verdict placeholders that `docs/releases/v9.0.0.md` still holds at `ca11bb6e` are in both copies. The body published on the tag day will be the document as it stands on the tagged commit, whatever T710 writes into it.

### 4.5 Generated `CHANGELOG.md` entry

- The heading is `## [v9.0.0] - 2026-11-01`, followed by `_Commits since v8.0.0._`, then the groups Features 6, Bug Fixes 10, Refactor 1, Documentation 19, Tests 5, CI 1, Chores 6, Other 1. That is 49 bullets with 0 `Merge branch` lines.
- The 49 subjects from the image's git equal the 49 from the host's git 2.43 (`git log --no-merges v8.0.0..origin/release/v9.0.0`, sorted `diff` empty). After the Conventional prefix is stripped, the bullets are the same multiset as the subjects (a script check returned `True`).
- `Other` holds `plan-124 wave 1: release audit, …` (commit `37ec27d0`, a subject without a Conventional type). Putting it there is correct classifier behaviour.
- Placement: the entry is inserted after the intro paragraphs and **above** `## [Unreleased]` (the first `## ` heading, rule K-12). Lines 1-12 and everything from `## [Unreleased]` onward are unchanged (`diff` against the committed file, with the 69 inserted lines removed, is empty).

### 4.6 Tag-tree check (T685/T686) and drift gate, with the drift job's fetch lines

| Command | Exit | Output |
|---|---|---|
| `git fetch origin main develop --depth=1` | 0 | |
| `git fetch --force origin 'refs/tags/*:refs/tags/*'` | 0 | |
| `check-release-tag-tree.py --tag v9.0.0 --main-ref origin/main` (main = v8.0.0 state) | **1** | `FAIL - the tree of v9.0.0 (aaf746364e45) differs from the tree of origin/main (654ad64e0665)`, with path list. Correct before the merge |
| the same with `--main-ref sim/main`, a scratch merge commit (`commit-tree -p origin/main -p v9.0.0 v9.0.0^{tree}`, the GitLab merge shape) | **0** | `PASS - v9.0.0 and sim/main have the same tree (aaf746364e45)` |
| `check-main-develop-drift.py --main-ref sim/main --develop-ref origin/develop` | 1 | `main marker (v9.0.0) is AHEAD of develop marker (v8.0.0)`. Expected: the scratch `develop` lacks the release merge |
| the same with `--develop-ref sim/develop` (scratch merge of the release into develop) | **0** | `main=v9.0.0 develop=v9.0.0 releases_behind=0`, `PASS` |

The `sim/*` refs are not the runner's `origin/*` refs. This shows only the scripts' logic on the release tree, not the gate on the real `main`.

## 5. Fail-closed cases (V)

| Case | Exit | Message |
|---|---|---|
| A. SEC-T686-06 shape: `GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=http.extraHeader`, `GIT_CONFIG_VALUE_0` holds the dummy token | 1 | `git fetch --tags --force failed: error: missing config value GIT_CONFIG_VALUE_0` / `fatal: unable to parse command-line config`. The value is not printed. The value filter drops `VALUE_0` but keeps `COUNT` and `KEY_0`, so git stops at the first fetch, before any API call. This is the availability failure the audit predicts if the runner delivers its credential this way |
| B. Tag without a document (`v9.0.1`, scratch, same commit) | 1 | `missing release brief: docs/releases/v9.0.1.md (...)` |
| C. `CI=true`, `CI_SERVER_HOST` unset, no `--expected-host` | 1 | `--expected-host is required in CI (pass "${CI_SERVER_HOST}")` |

## 6. Audit `release-v9-audit-v1.md` §5: what this rehearsal confirms

| §5 item | Status after T706 |
|---|---|
| 1. `release-docs-gate` passes | **Not confirmed.** Not run: the document still holds the verdict placeholders, which T710 fills; T707 runs `verify-release-docs.py` |
| 2. drift gate + tag-tree check pass | **Partly.** Both scripts and the job's two fetch lines run in the pinned image. Tag-tree is FAIL on today's `main` (correct) and PASS on a simulated merge with the release tree. The real pass needs the real `main` after the T711 merges (unverified) |
| 3. both fetches in `release` succeed with the filtered env (SEC-T686-06) | **Partly.** With the credential in `.git/config` or none (a local `file://` origin), the filtered env is enough and both fetches succeed. If the credential comes through the environment (case A), the job fails closed as predicted. **SEC-T686-06 itself, the runner's real clone method, cannot be confirmed here**: an agent cannot read the runner, and a scratch origin has no credential. The first real tag pipeline is the first test |
| 4. Releases API accepts `JOB-TOKEN`; pusher role; job-token settings | **Not confirmed.** No API call was made. Only shown: the script resolves the token by name and passes `JOB-TOKEN` as the header choice to the API function |
| 5. Release body equals the document; `CHANGELOG.md` lists the `v8.0.0..v9.0.0` non-merge subjects | **Confirmed for the script's output** (section 4.4, 4.5) on `ca11bb6e`. The final body is the document on the tagged commit after T710. GitLab's storage and rendering of the body (size limit, normalisation) are unverified |
| 6. No job-token value in the job logs (SEC-T686-03) | **Not confirmed.** The script printed no token value in any run here, and the dummy marker appears in no output line (no git or apk child received it, section 4.1, 4.3). **Whether GitLab masks `CI_JOB_TOKEN` in job logs cannot be confirmed here**; it is a property of the GitLab instance |
| 7. Job tokens in tag pipelines on protected tags | **Not confirmed** (GitLab-side) |
| Precondition: `apk add git~=2.54` resolves in the pinned image | **Confirmed on 2026-11-01** (`2.54.0-r0`). A later git minor version in Alpine 3.24 could still break the bootstrap on the tag day (unverified) |

## 7. Observations (no change made)

- **O-1 (changelog placement).** Rule K-12 puts the new entry above `## [Unreleased]`, whose line still reads "Bootstrap of the professional GitLab project surface — initial release pending." The committed `CHANGELOG.md` has no `v8.0.0` entry, because the job's output is only a job artifact (`.gitlab-ci.yml:228-231`), so the v9.0.0 artifact holds only the v9.0.0 entry. Keep a Changelog convention keeps `[Unreleased]` on top. This is the release manager's call; not a defect of the job.
- **O-2 (date).** The entry date comes from `date.today()` in the container (UTC on the runner), so the artifact will carry the tag day's date, not 2026-11-01.
- **O-3 (pre-release ordering, carried from T647).** It still holds: a `v9.0.0-rc.*` tag would sort above `v9.0.0`. No such tag exists.

## 8. Still unconfirmed until the real `v9.0.0` tag pipeline (T711)

SEC-T686-06 (the runner's clone method and whether the filtered fetches succeed with it); SEC-T686-03 (job-token masking in GitLab logs); acceptance of the `JOB-TOKEN` header by the Releases API with the real permission and allowlist settings; whether job tokens work in tag pipelines on protected `v*` tags; `release-docs-gate` and the tag-tree check on the real `main`; the runner's refspecs, `needs:` ordering and artifact upload; `apk add git~=2.54` on the tag day; GitLab's rendering of the 49815-byte body. All **(unverified)**.

## 9. Reproduction

The helper scripts were throwaway files in the session scratchpad and were not committed. The steps:

1. `git bundle create repo.bundle origin/release/v9.0.0 origin/main origin/develop --tags`.
2. `docker run -d` the digest-pinned image, then `docker cp` the bundle and two env-probe wrappers into it.
3. Run the `before_script` line with the dummy variables of section 2.
4. Run `docker network disconnect bridge <container>`.
5. Build the bare origin from the bundle, add the annotated scratch tag, and clone with the sparse checkout.
6. Run the commands of sections 4 and 5.
7. Remove the container with `docker rm -f`.
