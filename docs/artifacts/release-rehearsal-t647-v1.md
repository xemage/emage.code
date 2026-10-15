# Artifact: release-rehearsal-t647-v1.md

> Immutable once produced; revisions bump `<N>`.

**Based on:** `release-v8-audit-v2.md` (decision D-5, the user chose "Image run, no publish"; concern C-3 item 1); `docs/tasks/task-T647.md`; `docs/plans/plan-122-release-v8-wave-3.md` (T647); `.gitlab-ci.yml` (`release`, `release-docs-gate`, `main-develop-drift-gate`, read); `scripts/publish-release.py`, `scripts/check-main-develop-drift.py`, `scripts/verify-release-docs.py` (read, then run).

**Author / mode:** DevOps Engineer, T647. Only this file was added to the repository. Nothing was pushed, no tag or release was created on any GitLab project, no network call to gitlab.com was made, `WIKI_TOKEN` was not used, the primary checkout under `/home/emage/Code/emage/emage.code` was not mounted or copied.

**Basis marker:** **(V)** = run or read in this task. **(unverified)** = not checked.

## 1. Result

**PASS for the rehearsal's question (D-5):** in the real job image `python:3.12-alpine`, after the job's own `before_script` line, `scripts/publish-release.py --tag <fake-tag> --skip-api` runs to exit 0 on a GitFlow-shaped scratch repository with merge commits, an annotated and a lightweight prior tag and an annotated fake release tag. `git log --no-merges --pretty=%s --end-of-options <rev> --` works in that image's git, merge commits are absent from `CHANGELOG.md`, and the description equals the release document byte for byte. The drift gate script passes in the same image. `verify-release-docs.py` runs in the `alpine:3.20` gate image; its result on a snapshot of the real tree is in section 6 (the version-consistency stale list is real work for release preparation, not a rehearsal defect).

## 2. Environment (V)

| Item | Value |
|---|---|
| Job image (release, drift gate) | `python:3.12-alpine`, digest `sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4` (image created 2026-10-01) |
| In that image after `apk add --no-cache git` | **git 2.54.0**, Python 3.12.15, Alpine 3.24.2, user uid 0 |
| Gate image (release-docs-gate) | `alpine:3.20` digest `sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc`, Alpine 3.20.10, Python 3.12.13 after `apk add --no-cache python3`; **no git** (as in CI) |
| Host git used only to build the scratch repo | 2.43.0 (not the subject of the test) |
| Docker | client 29.1.3, server 29.9.1. `DOCKER_HOST` is `ssh://root@...` (a remote daemon), so local bind mounts are impossible; the scratch origin and the scripts were streamed into `docker run -i` over stdin as a tar. Nothing of the real repository except the three scripts under test (copied into the scratch repo) and, for section 6, a tracked-file snapshot (without `tests/golden/held-out/`, `.env*`, keys, credentials) was sent. |
| apk | unpinned, as in the job; the git version is whatever the floating `python:3.12-alpine` ships on the day. 2.54.0 is today's, not a promise for the tag day. |

## 3. Scratch repository (V)

Built outside the repository by a throwaway script (synthetic identity `scratch@example.invalid`): bare local origin plus a working repo. Content: `scripts/publish-release.py`, `scripts/check-main-develop-drift.py` (copies), `docs/releases/_template.md` (copy), `docs/releases/v1.0.0.md` (the template with `vX.Y.Z` replaced by `v1.0.0`), `README.md` with a `Latest release:` marker. History: `v0.9.0` (annotated) on the first commit; a `feature/` branch merged `--no-ff` with a GitLab-style subject; `release/v0.9.1` tagged lightweight `v0.9.1`, merged to `main`, back-merged to `develop`; a second feature and a bugfix merged `--no-ff`; seven further direct commits (perf, refactor, docs, test, ci, chore, one without a Conventional prefix); `release/v1.0.0` with the document, annotated fake tag `v1.0.0` on its tip, merged `--no-ff` to `main` and `develop`. 22 commits, 7 merge commits (20 of them are reachable from the tags).

## 4. Commands and output: the release job (V)

Job `before_script` run verbatim: `python3 -c "import shutil, subprocess; apk=shutil.which('apk'); subprocess.check_call([apk, 'add', '--no-cache', 'git']) if apk else None"`. Then a full clone of the scratch origin (`GIT_DEPTH=0`) detached at `v1.0.0`:

```
git tag --sort=-v:refname          ->  v1.0.0 / v0.9.1 / v0.9.0
git merge-base --end-of-options v0.9.1 v1.0.0        -> 86db2bd...  (the v0.9.1 commit)
git rev-list --count --end-of-options <base>..v1.0.0  -> 15
git rev-list --count --end-of-options v0.9.1..v1.0.0  -> 15   (equal, so the range is <base>..v1.0.0)
git log --no-merges --pretty=%s --end-of-options <base>..v1.0.0 --   -> 11 subjects
```

Without `--no-merges` the same range lists 15 subjects; the four extra are `Merge branch 'bugfix/3-null' into 'develop'`, `Merge branch 'feature/2-api' into 'develop'`, `Merge branch 'main' into 'develop'`, `Merge branch 'release/v0.9.1' into 'main'`. All four are absent with the flag.

Script call (the job's, plus `--skip-api` and dummy API arguments, which the CLI requires even with `--skip-api`; `.invalid` host, no call is made):

```
python3 scripts/publish-release.py --tag v1.0.0 --api-v4-url https://gitlab.invalid/api/v4 --project-id 1 --token DUMMY-NOT-A-TOKEN --skip-api
release-publish: regenerated CHANGELOG.md for v1.0.0
release-publish: skipped GitLab API publish by request          (exit 0)
```

Generated `CHANGELOG.md` (the only file written; `git status --short` shows only `?? CHANGELOG.md`; a second run is idempotent):

```
# Changelog

## [v1.0.0] - 2026-10-15

_Commits since v0.9.1._

### Features
- drop legacy flag
- add endpoint

### Bug Fixes
- null check

### Performance
- add index

### Refactor
- split module

### Documentation
- add release document v1.0.0
- update guide

### Tests
- add cases

### CI
- pin image

### Chores
- bump

### Other
- Update readme wording (no conventional prefix)
```

No `Merge branch` line appears. A root `release-notes.md` does not exist. The description the script would send (`render_release_description(load_release_brief("v1.0.0"))`) equals `docs/releases/v1.0.0.md` byte for byte (2967 bytes) and the document file is unchanged by the run.

Further cases (V, same image):

- **Shallow start** (`git clone --depth 1 --branch v1.0.0`): `rev-parse --is-shallow-repository` is `true` with 1 commit before; the script's `fetch --unshallow --tags origin` makes it `false` (20 commits, the history reachable from the tags), exit 0, same section. Git prints `warning: refs/tags/v1.0.0 ... is not a commit!` at the shallow clone of an annotated tag (clone-time, harmless here).
- **Fail-closed**: unknown tag, missing document, newline in the tag, non-https URL each exit 1 with a one-line message.
- **No previous tag**: `resolve_previous_tag` returns `None`, the range is the tag alone, 15 subjects, no merges.
- **Pre-release tag ordering**: with a local `v1.0.0-rc.1`, `git tag --sort=-v:refname` lists `v1.0.0-rc.1` above `v1.0.0` (git sorts a suffix after the plain version unless `versionsort.suffix` is set). For a final tag the previous tag is still right; a run on an `-rc` tag cut after the final tag of the same version would pick the final tag as its "previous". Not relevant for v8.0.0 as long as no `v8.0.0-rc.*` exists; note it if one is ever cut.

## 5. Commands and output: the drift gate job (V)

The `main-develop-drift-gate` runs with `GIT_DEPTH=1`. With a runner-style checkout (init, `remote add origin` with the default `+refs/heads/*:refs/remotes/origin/*`, depth-1 fetch of the tag, detach), the job's three script lines ran verbatim:

```
git fetch origin main develop --depth=1                      exit 0   (creates origin/main, origin/develop)
git fetch --force origin 'refs/tags/*:refs/tags/*'          exit 0   (v0.9.0, v0.9.1)
python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop
drift-check: main=v1.0.0 develop=v1.0.0 releases_behind=0
drift-check: PASS - main is within the allowed 1-release grace window      (exit 0)
```

Caveat found while rehearsing: after `git clone --depth 1 --branch <tag>` the remote refspec is single-branch (`+refs/tags/v1.0.0:refs/tags/v1.0.0`), and the same `git fetch origin main develop --depth=1` then writes only `FETCH_HEAD`, no `origin/main`, so the drift script dies with a `CalledProcessError` traceback (exit 1). That is a property of my clone method, not of the job; it depends on how the GitLab runner configures the remote, which I did not observe (**unverified**). Earlier tag runs of this job are the real evidence.

## 6. `release-docs-gate` script (V for what ran, with limits)

`alpine:3.20` plus `apk add --no-cache python3`, on a snapshot of the tracked files of this worktree at its base commit (held-out directory excluded):

- `verify-release-docs.py --tag v7.0.1`: exit 1, `missing required content in docs/releases/v7.0.1.md: ## RELEASE VERDICT` (history, as audit C-2 says).
- Markers bumped in the three marker files and a template-shaped document `docs/releases/<tag>.md`: with `v1.0.0` exit 0 (not meaningful: the stale-version check only flags versions older than the marker); with `v8.0.0` exit 1, only `version-consistency` findings: 9 lines at 6 locations (`README.md:201`, `docs/wiki/implementation-guide.md:5` and `:41`, `implementation/README.md:4`, `:6`, `:56`, all `v7.0.1`). The snapshot omits `tests/golden/held-out/`, so any hits in that protected path are not in this count; audit C-1 recorded 18 findings at 14 locations on `origin/develop` `ac63dbe`, and the difference (snapshot differences, base commit, excluded path) was not reconciled (**unverified**). Stale-claim fixing is release-preparation work (audit C-1, D-1).
- The script ran with the image's python3 and needs no git (the gate image has none).

## 7. Limits

- **The GitLab API half is not exercised**: `create_or_update_release` (GET/PUT/POST of the Release) was skipped by `--skip-api`; it is covered by the offline dry run (`scripts/dry-run-publish-release.py`) and `tests/functional/test_publish_release.py`, not by this rehearsal. GitLab's description size limit and the rendering of the document as a Release are **(unverified)**.
- Not the real project: the scratch history is 22 commits, not the v7.0.1..v8.0.0 range; real-range size, the real `CHANGELOG.md` (the rehearsal started with none, so the insertion under an existing `# Changelog` and the known intro-paragraph placement defect, audit C-3, were not exercised) and the real `docs/releases/v8.0.0.md` (not yet written) are not covered.
- Runner behaviour not reproduced: `GIT_DEPTH=0` is imitated with a full clone; the runner's own fetch refspecs, `CI_*` variables, `needs:` ordering, the tag-protection and `WIKI_TOKEN` (Protected+Masked) settings (D-4) and artifact upload are **(unverified)**.
- Floating image and unpinned `apk add git`: the git version on the tag day can differ from 2.54.0; the rehearsal is a point-in-time result. The job image is not pinned by digest in `.gitlab-ci.yml` (observation, no change made).
- Remote docker daemon (see section 2); the rehearsal ran there, not on this machine's engine.
- Not run: `release-docs-gate` in the exact `CI_COMMIT_TAG` context on the real tag, `check-version-consistency.py` against the held-out directory.

## 8. Reproduction

Scratch build and runner scripts were throwaway files in the session scratchpad (not committed). To repeat: create a bare origin and a GitFlow-shaped history as in section 3, stream both into `docker run -i python:3.12-alpine` (tar over stdin when `DOCKER_HOST` is remote), run the `before_script` line from section 4, clone, detach at the fake tag, and run the commands listed above.
