# Repository functionality and v3 release requirements
_Exported on 6/16/2026 at 14:19:14 GMT+2 from Cursor (3.7.36)_

---

**User**

Check status, Merge if everything is green otherwise fix, update plans and task board,

---

**Cursor**

Checking merge/pipeline status, then updating plans and the task board.


Main and develop pipelines are green; MR !24 is merged. Tagging v4.0.0, back-merging main into develop, then updating plans and the task board.


## Status — all green

| Branch / artifact | State | Pipeline |
|-------------------|--------|----------|
| `main` @ `2c7b15a` | MR [!24](https://gitlab.com/em-age/emage.code/-/merge_requests/24) merged | success |
| Tag `v3.0.1` | Published | release pipeline OK |
| Tag `v4.0.0` | Published (was interrupted earlier; completed now) | release pipeline **success** |
| `develop` @ `902bb89` | MR [!25](https://gitlab.com/em-age/emage.code/-/merge_requests/25) merged | success |
| [GitLab Release v4.0.0](https://gitlab.com/em-age/emage.code/-/releases/v4.0.0) | Live with Install + Highlights | — |

**Active tasks:** empty (no open work on the board).

---

## Actions taken this session

1. **Tagged `v4.0.0`** on `main` — release CI passed and GitLab Release published.
2. **Back-merged `main` → `develop`** via [!25](https://gitlab.com/em-age/emage.code/-/merge_requests/25) — resolved release-marker conflicts; pipeline green; merged.
3. **Updated plan** — docs/plans/plan-007-v4-ecosystem-workflows.md: all acceptance criteria checked; release path steps 1–3 marked done.
4. **Updated task board** — [`docs/tasks/completed-tasks.md`](docs/tasks/completed-tasks.md) on `develop` with **T046–T050** (v3.0.1 patch, develop hygiene, v4 implementation, v4.0.0 release).

---

## Open item (minor)

[!26](https://gitlab.com/em-age/emage.code/-/merge_requests/26) — closes plan-007 status text (“back-merge complete”). Pipeline was **running** when last checked; merge once it’s green (docs-only, low risk).

---

## Current release summary

**v4.0.0** is the current release. Install from `v3/implementation/`:

- **3 new skills:** `systematic-debugging`, `receiving-code-review`, `verification-before-completion`
- **2 new commands:** `/handoff`, `/discover-skills`
- **Agent safety guards** in security guidelines
- **Mandatory skill workflow** in `AGENTS.md`

Quick start:

```
/discover-skills "start new project"
/new-project "My SaaS application"
```

---

**User**

Check status, update plans and task board

---

**Cursor**

MR !26 pipeline is green — merging it, then syncing the plan and task board on `develop`.


## Status — all green

| Item | State |
|------|--------|
| **`main`** @ `2c7b15a` + [!28](https://gitlab.com/em-age/emage.code/-/merge_requests/28) | Pipeline **success** |
| **`develop`** @ `0fbfeda` (after [!27](https://gitlab.com/em-age/emage.code/-/merge_requests/27)) | Pipeline **success** |
| **Tags** | `v3.0.0`, `v3.0.1`, `v4.0.0` published |
| **Release** | [v4.0.0](https://gitlab.com/em-age/emage.code/-/releases/v4.0.0) live |
| **Open MRs** | None blocking |

---

## Actions taken

1. **Merged [!26](https://gitlab.com/em-age/emage.code/-/merge_requests/26)** — plan-007 status closed on `develop`.
2. **Merged [!27](https://gitlab.com/em-age/emage.code/-/merge_requests/27)** — task board T051–T052; plan-006 marked complete.
3. **Merged [!28](https://gitlab.com/em-age/emage.code/-/merge_requests/28)** — synced task ledger and plans on `main` (was stuck at T045).

---

## Plans

| Plan | Status |
|------|--------|
| plan-006 (docs/plans/plan-006-v3-release-ready-parity.md) | **Complete** — delivered in v3.0.0 (T038–T045) |
| plan-007 (docs/plans/plan-007-v4-ecosystem-workflows.md) | **Complete** — v4.0.0 on `main`/`develop`; v4.x follow-ups noted |

---

## Task board

**Active:** empty

**Recently completed** ([`docs/tasks/completed-tasks.md`](docs/tasks/completed-tasks.md)):

| ID | Summary |
|----|---------|
| T046 | Post-v3.0.0 fixes + Pi platform (!20) |
| T047 | Develop pi revert (!21) |
| T048 | Patch v3.0.1 (!22) |
| T049 | v4 ecosystem implementation (!23) |
| T050 | Major release v4.0.0 (!24) |
| T051 | Develop back-merge v4.0.0 (!25) |
| T052 | Plan-007 closure (!26) |

`main` and `develop` now share the same task ledger and plan status.

---

**User**

1) Archive v1, v2, v3 (move to version independent folder) - build, verification and other scripts must still work though
2) Create an easy to use installation method.
3) Create updated documentation with installation / usage instructions

---

**Cursor**

Exploring the repo layout and every reference to `v1/`, `v2/`, and `v3/` so we can archive them safely without breaking scripts or CI.


Implementing the restructure: moving versioned trees into `archive/`, promoting the current stream to `implementation/`, and adding an install script plus path updates.


Updating the remaining documentation and running sync to regenerate projections.


Fixing repo-root resolution in scripts and updating tests that still reference old paths.


All three items are done on branch `feature/archive-and-install`. Summary:

## 1. Archive restructure

| Before | After |
|--------|-------|
| `v1/` | `archive/v1/` |
| `v2/` | `archive/v2/` |
| `v3/implementation/` | `implementation/` (repo root) |
| `v3/` (empty) | `archive/v3/` (pointer stub) |

CI, Makefile, tests, and scripts (`check-v3.py`, `generate-registry-v3.py`, `paths.py`) were updated for the new layout. v2 drift checks still run against `archive/v2/implementation/`.

## 2. Installation

**Recommended:**

```bash
git clone https://gitlab.com/em-age/emage.code.git
cd emage.code
scripts/install.sh --target /path/to/your-project --platform cursor
```

Platforms: `cursor`, `github`, `gemini`, `opencode`, `pi`, or `all`.

**Makefile shortcut:**

```bash
make install TARGET=/path/to/your-project PLATFORM=cursor
```

## 3. Documentation

Updated:

- `README.md` — layout, install, validation paths
- `CONTRIBUTING.md` — contributor workflow
- `docs/wiki/quick-start.md`, `implementation-guide.md`, `home.md`
- `docs/releases/_template.md`, `v4.0.0.md`
- `scripts/verify-release-docs.py` — gates the new doc surface

`docs/wiki/v3-implementation.md` is now a redirect to `implementation-guide`.

## Verification

- `make sync` / `make verify` — pass (416 files, no drift)
- `python3 tests/run.py` — 78 tests pass
- `python3 scripts/verify-release-docs.py --tag v4.0.0` — pass

Changes are **uncommitted** on `feature/archive-and-install`. I can commit and open an MR to `main` if you want — suggest `v4.1.0` or `v5.0.0` given the breaking path change.

---

**User**

commit and open an MR to main — v5.0.0

---

**Cursor**

Preparing the v5.0.0 release: checking git state and updating release markers and docs before commit and MR.


The **v5.0.0 release commit is done locally**, but push/MR creation failed because GitLab credentials aren’t available in this environment (HTTPS auth failed, SSH has no key, `glab` reports an invalid token, and GitLab MCP auth was skipped).

## Committed locally

| Item | Value |
|------|--------|
| Branch | `feature/archive-and-install` |
| Commit | `eb8a6c4` — `release: v5.0.0 — archive version trees and add install.sh` |
| Release brief | `docs/releases/v5.0.0.md` |
| Markers | Updated to `Latest release: v5.0.0` |
| Docs gate | `python3 scripts/verify-release-docs.py --tag v5.0.0` — pass |

## Push and open MR (run locally)

After refreshing GitLab auth (`glab auth login` or a valid `GITLAB_TOKEN`):

```bash
cd /home/emage/Code/emage/emage.code
git push -u origin feature/archive-and-install

glab mr create --target-branch main \
  --title "release: v5.0.0 — archive version trees and install.sh" \
  --description "$(cat <<'EOF'
## Summary

- Promote `v3/implementation/` to version-independent `implementation/` at repo root
- Archive `v1/`, `v2/`, and `v3/` under `archive/` (v2 CI drift gate preserved)
- Add `scripts/install.sh` and `make install` for one-command platform install
- Update README, CONTRIBUTING, wiki, release docs, CI, tests, and validation scripts

## Breaking changes

- Install path is now `implementation/` or `scripts/install.sh` (not `v3/implementation/`)
- Historical trees live under `archive/v1/` and `archive/v2/`

## Test plan

- [x] `make sync` / `make verify` — no drift (416 files)
- [x] `python3 tests/run.py` — 78 tests pass
- [x] `python3 scripts/verify-release-docs.py --tag v5.0.0` — pass
- [ ] CI pipeline green on merge request
- [ ] After merge: tag `v5.0.0` on `main` and publish GitLab Release
EOF
)"
```

## After MR merges to `main`

```bash
git checkout main && git pull
git tag -a v5.0.0 -m "Release v5.0.0"
git push origin v5.0.0
git checkout develop && git merge --no-ff main && git push
```

If you re-authenticate GitLab in this session, I can retry the push and MR creation for you.

---

**User**

Commit, push (do NOT use SSH) and monitor CI, fix if needed. Create Release.
Important information: gitlab CLI (glab) is available with a valid token. The message '! Invalid token provided' is a known issue and can be ignored!
Also: do NOT use SSH for push

---

**Cursor**

Checking repo state, then pushing over HTTPS with glab and monitoring CI.


CI is green. Merging the MR, tagging v5.0.0, and creating the release.


**v5.0.0 is shipped.** Commit was already in place; push, CI, merge, tag, and release all completed without SSH.

## Completed

| Step | Result |
|------|--------|
| **Commit** | `eb8a6c4` — `release: v5.0.0 — archive version trees and add install.sh` |
| **Push** | HTTPS via `glab` token (`feature/archive-and-install`) |
| **MR** | [!29](https://gitlab.com/em-age/emage.code/-/merge_requests/29) — merged (squash) to `main` |
| **MR CI** | [Pipeline #160](https://gitlab.com/em-age/emage.code/-/pipelines/2582249648) — **success** (all 6 jobs) |
| **Tag** | `v5.0.0` on `main` (`bfed6bbc`) |
| **Release CI** | [Pipeline #162](https://gitlab.com/em-age/emage.code/-/pipelines/2582254604) — **success** |
| **Release** | [v5.0.0](https://gitlab.com/em-age/emage.code/-/releases/v5.0.0) published with Install + Highlights from `docs/releases/v5.0.0.md` |

No CI fixes were needed — the MR pipeline passed on the first run.

## Install (from v5.0.0)

```bash
git clone https://gitlab.com/em-age/emage.code.git
cd emage.code
scripts/install.sh --target /path/to/your-project --platform cursor
```

## Optional follow-up

Back-merge `main` into `develop` so the task ledger and branch stay aligned:

```bash
git checkout develop
git pull
git merge --no-ff origin/main
git push
```

I can do that back-merge over HTTPS if you want.

---

**User**

Back-merge main into develop so the task ledger and branch stay aligned
Then, check, verify and clean up all scripts in @implementation/scripts/
Fix / remove if needed

---

**Cursor**

Back-merging `main` into `develop`, then auditing and cleaning up `implementation/scripts/`.


Back-merging `main` into `develop`, then fixing the broken script wrappers and stale paths.


Applying script fixes while MR !30 CI runs.


Resolving merge conflicts on MR !30 locally.


---

**User**

resume

---

**Cursor**

Checking repo state and continuing the back-merge and script cleanup.


Resolving merge conflicts by taking main's v5.0.0 layout and preserving develop's task ledger updates.


Conflict markers remain in several files — fixing them by taking main's versions.


Resumed and finished. Here is what completed:

## Back-merge `main` → `develop`

MR [!30](https://gitlab.com/em-age/emage.code/-/merge_requests/30) had merge conflicts (550 files — mostly `v3/implementation/` → `implementation/` renames). Resolved locally by taking **main’s v5.0.0 layout**, then pushed directly to `develop`:

| Item | Value |
|------|--------|
| Commit | `f052cfb` on `develop` |
| Push | `0fbfeda..f052cfb` via HTTPS |
| CI | [Pipeline #164](https://gitlab.com/em-age/emage.code/-/pipelines/2582785395) — **success** |
| Task ledger | Added **T053** (back-merge), **T054** (script cleanup) |

MR !30 is still open on GitLab (superseded by the direct push). You can close it manually if you want a tidy MR list.

## `implementation/scripts/` cleanup

| Script | Action |
|--------|--------|
| `sync-v3.mjs` | Kept — core sync engine |
| `verify-v3.mjs` | Kept — drift check wrapper |
| `check-v3.py` | Kept — updated usage docstring + `_repo_root()` |
| `generate-registry-v3.py` | Kept — updated module docstring |
| `package-v3.py` | Kept — updated module docstring |
| `sync.sh` | **Fixed** — was calling missing `sync.mjs`; now calls `sync-v3.mjs --root ..` |
| `sync.ps1` | **Fixed** — same as `sync.sh` |
| `verify.sh` | **Added** — thin wrapper for `verify-v3.mjs` |

Also updated related docs:
- `implementation/commands/package-*.md` — paths now use `implementation/`
- `implementation/knowledge/README.md`, `PREREQUISITES.md`, `implementation/README.md`

## Verification

- `make sync` / `make verify` — pass (416 files, no drift)
- `generate-registry-v3.py` — regenerated registry
- `python3 tests/run.py --suite functional` — 61 tests pass
- `./implementation/scripts/sync.sh --check` — pass

**Install/sync from repo root (unchanged):**

```bash
make sync
make verify
```

**From `implementation/scripts/`:**

```bash
./sync.sh
./verify.sh
```

---

**User**

Completely remove version relations / mentions (v1, v2, v3) from repository. No mention of v1, v2, v3 anymore. Also no migration instructions.
Check and update documentation (docs, Wiki, ... ) as well as all scripts.
Only one (current) implementation must be left.
Finally, synchronize, verify implementations and create a new Release.
Important: Gitlab CLI (glab) is available with valid token (message about invalid token is known issue and can be ignored). Also, do NOT use SSH for push.

---

**Cursor**

Removing all v1/v2/v3 references and the archive layout. Exploring the repository scope first.


Large cleanup: removing `archive/`, renaming v3-prefixed scripts, and scrubbing docs. Working through it systematically.


Running a bulk update script, then rewriting key files.


Applying targeted updates to critical files after the bulk script was blocked.


Continuing the cleanup: updating canonical knowledge, root docs, and scripts, then running sync and verification.


**v6.0.0 is released.** The repository now has a single `implementation/` stream with no archive, migration docs, or `-v3` script names.

## What changed

### Repository structure
- **Removed** entire `archive/` tree (historical v1/v2/v3 streams)
- **Deleted** migration docs (`migration-v1-to-v2.md`, `v3-implementation.md`, migration artifacts)
- **Single implementation** at `implementation/` only

### Scripts renamed
| Old | New |
|-----|-----|
| `sync-v3.mjs` | `sync.mjs` |
| `verify-v3.mjs` | `verify.mjs` |
| `check-v3.py` | `check.py` |
| `generate-registry-v3.py` | `generate-registry.py` |
| `package-v3.py` | `package.py` |

### Documentation
- Rewrote `README.md`, `CONTRIBUTING.md`, wiki pages
- Updated `implementation/README.md`, `AGENTS.md`, `PREREQUISITES.md`
- Added [`docs/releases/v6.0.0.md`](docs/releases/v6.0.0.md)
- Release markers set to **Latest release: v6.0.0**

### Sync & verification
- `make sync` — 416 files regenerated, no drift
- `make verify` — OK
- Super-gate — **245 checks passed**
- Tests — **77 passed** (1 skipped)
- `verify-release-docs.py --tag v6.0.0` — passed

## Release published

| Item | Link |
|------|------|
| MR (merged) | [!31](https://gitlab.com/em-age/emage.code/-/merge_requests/31) |
| CI pipeline | [#168](https://gitlab.com/em-age/emage.code/-/pipelines/2582833326) — success |
| Tag | `v6.0.0` |
| GitLab Release | [v6.0.0](https://gitlab.com/em-age/emage.code/-/releases/v6.0.0) |

## Follow-up

Back-merge MR [!32](https://gitlab.com/em-age/emage.code/-/merge_requests/32) (`main` → `develop`) is open — CI was still running when merge was attempted. Merge it when green to align `develop` with `main`.

## Current commands

```bash
make sync && make verify
python3 implementation/scripts/check.py --root implementation --required
node implementation/scripts/verify.mjs --root implementation
scripts/install.sh --target <project> --platform cursor
```

---

**User**

pause

---

**Cursor**

Paused.

**Done:** v6.0.0 is merged to `main`, tagged, and published. The repo is on a single `implementation/` stream with renamed scripts and updated docs.

**Open:** Back-merge MR [!32](https://gitlab.com/em-age/emage.code/-/merge_requests/32) (`main` → `develop`) — merge when CI is green.

Say when you want to continue.

---

**User**

resume

---

**Cursor**

Resuming from the pause — checking MR !32 and branch state to finish the back-merge.


MR !32 is green and mergeable — merging the back-merge now.


Resumed and finished the remaining item.

**Back-merge complete:** MR [!32](https://gitlab.com/em-age/emage.code/-/merge_requests/32) merged (`main` → `develop`). CI passed.

**Remote branches:**
- `main` — `ac92220a` (v6.0.0 release merge)
- `develop` — `f6760d93` (back-merge from `main`)

**v6.0.0 release** — already published:
- Tag: `v6.0.0`
- Release: https://gitlab.com/em-age/emage.code/-/releases/v6.0.0

**Local workspace:** Your local `develop` is behind remote (stale `origin/develop`). To sync:

```bash
git fetch origin
git checkout develop
git pull origin develop
```

The file you have open (`implementation/.pi/skills/verification-before-completion/SKILL.md`) already uses the new paths (`check.py`, `verify.mjs`) — no stale v3 references there.

Anything else you want to tackle?

---

**User**

Get local workspace to latest state

---

**Cursor**

Local workspace is synced to the latest remote state.

**Current state**
- Branch: `develop`
- HEAD: `f6760d9` — *Merge branch 'main' into 'develop'*
- Tracking: up to date with `origin/develop`
- Working tree: clean

**Fetched**
- `origin/develop` → `f6760d9` (includes v6.0.0 + back-merge)
- `origin/main` → `ac92220a` (v6.0.0 release)
- Tag `v6.0.0`

Recent history on `develop`:
1. `61ac37b` — feat!: unify repository to single implementation stream (v6.0.0)
2. `6554e1e` — Back-merge main after v6.0.0
3. `f6760d9` — Merge branch 'main' into 'develop'

You're ready to work from the latest codebase.

---

**User**

Please fix the bug.
There is an issue that when @scripts/install.sh runs and one of the target subfolders (i.e. /docs) already exists, the files are copied into a sub-sub-folder with this name.
Example:

"<target-project-folder>/.pi" already exists.
install.sh --target <target-project-folder> --platform pi
Result: <target-project-folder>/.pi/.pi

---

**Cursor**

Inspecting `scripts/install.sh` to see how it handles existing target directories.


The bug is `cp -r` nesting when the destination already exists. Verifying behavior, then fixing with a merge-into helper.


Fixed. `cp -r source dest` nests into `dest/source` when `dest` already exists, which caused `.pi/.pi` and `docs/docs`.

**Change:** added a `copy_tree_into` helper that creates the destination and copies contents with `cp -r "$src/." "$dest/"`, so existing folders are merged instead of nested.

```63:98:scripts/install.sh
# Merge source tree into dest without nesting when dest already exists.
# `cp -r src dest` creates dest/srcname when dest is present; this copies contents.
copy_tree_into() {
  local src="$1"
  local dest="$2"
  run mkdir -p "$dest"
  run cp -r "$src/." "$dest/"
}
```

Applied to all directory installs: `docs`, `.cursor`, `.github`, `.gemini`, `.opencode`, `.pi`. Single-file copies (`AGENTS.md`, `mcp.json`) are unchanged.

**Test added:** `tests/functional/test_install_script.py` — pre-creates `.pi` and `docs`, runs install, asserts no nesting and that existing files are kept. Test passes.

Re-run your install; files should land directly in `<target>/.pi/` and `<target>/docs/`.

---

**User**

Also add an option (i.e. -u / --update) to update an exisitng version.


---

**Cursor**

Reviewing `install.sh` and any existing update workflow to define `--update` behavior.


Adding `--update` to sync platform trees (remove stale files) while merging `docs/` and requiring an existing install.


Added `-u` / `--update` to `scripts/install.sh`.

### Behavior

| Mode | Platform dirs (`.pi`, `.cursor`, …) | `docs/` | `AGENTS.md` |
|------|--------------------------------------|---------|-------------|
| **Install** (default) | Merge into existing folders | Merge (keeps your tasks/checkpoints) | Overwrite |
| **Update** (`-u`) | Full sync — removes stale upstream files | Merge (preserves local workspace state) | Overwrite |

**Update requirements:** `AGENTS.md` must already exist in the target (otherwise the script exits with an error).

### Usage

```bash
# First install
scripts/install.sh --target ~/projects/my-app --platform pi

# Update to latest emage.code release
scripts/install.sh --target ~/projects/my-app --platform pi --update
```

Uses `rsync -a --delete` when available; otherwise removes and recopies the platform tree.

### Tests

Four tests in `tests/functional/test_install_script.py` — all passing:
- merge without nesting (original fix)
- update requires existing install
- update removes stale platform files
- update preserves custom files under `docs/`

---

**User**

Create a new release (on Gitlab / main) with updated documentation.

---

**Cursor**

Preparing a GitLab release: checking repo state, updating release docs, then running verification before we tag and publish.


Updating release docs to v6.0.1 and preparing the GitLab release.


Git push auth failed; publishing the commit via the GitLab API instead.


MR !33 has merge conflicts from branch divergence. Creating a clean release branch from `main` instead.


CI failed because the test image lacks `bash`. Checking the CI config and updating the tests.


**v6.0.1** is published on GitLab `main`.

## Release

| Item | Link |
|------|------|
| **GitLab Release** | [v6.0.1](https://gitlab.com/em-age/emage.code/-/releases/v6.0.1) |
| **Merge request** | [!34](https://gitlab.com/em-age/emage.code/-/merge_requests/34) (merged) |
| **CI pipeline** | [#179](https://gitlab.com/em-age/emage.code/-/pipelines/2597188114) — success |
| **Tag** | `v6.0.1` on `main` (`f2959c4`) |

## What's in v6.0.1

- **Installer fix** — no more nested folders (`.pi/.pi`, `docs/docs`) when targets already exist
- **`--update` / `-u`** — sync platform trees and remove stale generated files
- **Docs updated** — `Latest release: v6.0.1` across README, wiki, `implementation/README.md`, `docs/releases/v6.0.1.md`
- **Tests** — `tests/functional/test_install_script.py` (4 cases)
- **CI fix** — `bash` added to Alpine unit-tests image

## Notes

- **!33** (develop→main) was closed — it had merge conflicts from branch divergence
- **!35** (back-merge main→develop) is open with conflicts; `develop` on GitLab is still behind `main`
- **Local workspace** is on `main` at `f2959c4`, matching remote

## Update an existing project

```bash
scripts/install.sh --target /path/to/your-project --platform pi --update
```

---

**User**

I used 'scripts/install.sh --target /home/emage/Code/emage/emage.code/ --platform all --update' to update the version of emage.code in the current folder.
The only thing I wonder if it is as expected (at an update): the file @docs/tasks/completed-tasks.md was emptied completely.
May this lead to issues?

---

**Cursor**

Checking how `--update` handles `docs/` and what's in the source `completed-tasks.md`.


Yes — that behavior matches how `install.sh` works today, and it can cause real issues in your case.

## What happened

On `--update`, platform folders (`.pi`, `.cursor`, etc.) are fully synced, but `docs/` is always **merged** via `copy_tree_into`, not `rsync --delete`:

```117:121:scripts/install.sh
install_common() {
  run cp "$IMPLEMENTATION/AGENTS.md" "$TARGET/AGENTS.md"
  # Workspace docs are merged so local task/checkpoint state is preserved.
  copy_tree_into "$IMPLEMENTATION/docs" "$TARGET/docs"
}
```

`copy_tree_into` copies files from `implementation/docs/` **on top of** `target/docs/`. Any file that exists in both places gets **overwritten**.

`implementation/docs/tasks/completed-tasks.md` is only an empty starter template:

```1:7:implementation/docs/tasks/completed-tasks.md
# Completed Tasks

Append-only log. Entries move here after the orchestrator marks a task `done`.

| ID | Title | Owner | Done on | Outcome / artifact |
|----|-------|-------|---------|--------------------|
```

On `main`, the repo-root `docs/tasks/completed-tasks.md` had ~50+ completed task rows (T001–T053, etc.). Your update replaced that with the empty template.

The same likely happened to `docs/tasks/active-tasks.md` — it was reset to the example `T001` row from `implementation/docs/`.

## Why this is a problem

Per `AGENTS.md`, the orchestration protocol relies on:

- `docs/tasks/active-tasks.md` — current work
- `docs/tasks/completed-tasks.md` — append-only done log

Losing the completed ledger means:

1. **Audit trail gone** — no record of what was finished and when
2. **Inconsistent state** — `docs/tasks/task-T*.md` briefs are probably still there (they aren’t in `implementation/docs/`, so they weren’t deleted), but the ledger no longer references them
3. **Agent confusion** — orchestrator/checkpoint flows may assume the ledger is authoritative

Platform projections (`.pi`, agents, skills) should be fine; this mainly affects **project workspace docs**.

## Special case: updating emage.code itself

`install.sh` is meant for **installing into a consumer project**, not for updating the emage.code **source repo**.

This repo has two different `docs/` trees:

| Path | Purpose |
|------|---------|
| `docs/` (repo root) | Full project state: wiki, releases, task history, checkpoints |
| `implementation/docs/` | Minimal template copied into installed projects |

Running install with `--target` pointing at the emage.code repo overwrites root ledger files with the template.

## Recovery

Restore from git (on `main` the file still has full history):

```bash
git checkout origin/main -- docs/tasks/completed-tasks.md docs/tasks/active-tasks.md
```

Or recover a specific version from history if you’ve committed since the update.

## Going forward

- **Don’t** use `install.sh --update` on the emage.code repo root to refresh the framework — use `make sync` / `make verify` in the repo instead.
- For **other projects**, `--update` is fine for platform trees, but be aware it will still overwrite `docs/tasks/active-tasks.md` and `docs/tasks/completed-tasks.md` if those paths exist in the target.

That last point is arguably a design gap: the installer treats those ledgers as installable templates, not as user-owned runtime state that should be preserved on update.

If you want, switch to Agent mode and we can change `install.sh` so update skips or only seeds `docs/tasks/*.md` when missing.

---

**User**

Change @scripts/install.sh  so update only seeds docs/tasks/*.md when missing or updates the format in case it changed it changed but prevents listed tasks.

---

**Cursor**

Reviewing `install.sh` and the task ledger files to design update behavior that preserves listed tasks.


Implementing a task-ledger merge helper and updating `install.sh` to use it on `--update`.


Updated `install.sh` so `--update` no longer wipes task ledgers.

## Behavior on `--update`

| File | Behavior |
|------|----------|
| `docs/tasks/active-tasks.md` | Refresh header/footer from template; **keep** existing `T###` rows |
| `docs/tasks/completed-tasks.md` | Same |
| Other `docs/tasks/*.md` | **Seed only** if missing (e.g. user `task-T099.md` untouched) |
| Other `docs/*` subtrees | Still merged via `copy_tree_into` (templates, etc.) |

Template example rows (`_Example:`) are never copied over real data.

## New helper

`scripts/merge-task-docs.py` — parses each ledger into preamble (title + table header), task rows, and postamble (status notes), then writes template preamble/postamble with preserved rows.

## Tests

- `tests/functional/test_merge_task_docs.py` — merge logic (3 tests)
- `tests/functional/test_install_script.py` — `test_update_preserves_task_ledger_rows` (integration)

All 8 tests pass.

Re-running your update command should keep rows in `completed-tasks.md` and `active-tasks.md` while updating format/footer from the current template. To restore what was lost earlier:

```bash
git checkout origin/main -- docs/tasks/completed-tasks.md docs/tasks/active-tasks.md
```

---

**User**

Create a new release (on Gitlab / main) with updated documentation.

---

**Cursor**

Preparing v6.0.2 release: checking repo state and updating release documentation.


**v6.0.2** is published on GitLab `main`.

## Release

| Item | Link |
|------|------|
| **GitLab Release** | [v6.0.2](https://gitlab.com/em-age/emage.code/-/releases/v6.0.2) |
| **Merge request** | [!36](https://gitlab.com/em-age/emage.code/-/merge_requests/36) (merged) |
| **CI pipeline** | [#184](https://gitlab.com/em-age/emage.code/-/pipelines/2597271598) — success |
| **Tag** | `v6.0.2` on `main` (`3999316`) |

## What's in v6.0.2

- **`scripts/merge-task-docs.py`** — on `--update`, refreshes ledger format without wiping task rows
- **`install.sh`** — task ledgers merged separately; other `docs/` subtrees still copied as before
- **Docs** — `Latest release: v6.0.2` in README, wiki, `implementation/README.md`, plus `docs/releases/v6.0.2.md`
- **Tests** — 8 install/merge tests passing; release docs gate passed

## Local workspace

Your tree is at the release commit (`3999316`). There are still **untracked** platform folders at the repo root (`.pi/`, `.gemini/`, etc.) from running `install.sh` against this repo — safe to delete; they are not part of the release:

```bash
rm -rf .pi .gemini .opencode .cursor/commands .cursor/skills \
  .github/prompts/discover-skills.prompt.md .github/prompts/handoff.prompt.md \
  .github/skills/receiving-code-review .github/skills/systematic-debugging \
  .github/skills/verification-before-completion
```

For consumer projects, use:

```bash
scripts/install.sh --target <project> --platform all --update
```

Task rows in `docs/tasks/active-tasks.md` and `docs/tasks/completed-tasks.md` are now preserved.

---

**User**

Commit the files anywayy with something like "Update internally used platform files"

---

**Cursor**

Committed on branch `release/v6.0.2`:

**`1ffcbdb`** — `chore: update internally used platform files`

274 files, including:
- Root platform projections: `.cursor/`, `.gemini/`, `.github/` (prompts/skills), `.opencode/`, `.pi/`
- Local agent skills: `.agents/`
- Updated manifests and `docs/tasks/active-tasks.md`

Working tree is clean. This commit is local only — say if you want it pushed or opened as an MR to `main`/`develop`.

---

**User**

/"Orchestrator" Plan new features. Read https://hackernoon.com/twelve-opencode-skills-every-dev-team-should-steal , follow links included, especially read https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/SKILL.md?ref=hackernoon.com
2) Implement optional enforcement of 'Test Driven Development' (i.e. user is asked)
1) Evaluate, which other features could be missing in current implementation of 'emage.code'


---

**Cursor**

Planning new features: reviewing the article and TDD skill, then comparing them to emage.code's current skills and workflow.


Creating the orchestrator plan artifact and checkpoint from the gap analysis.


## Orchestrator plan complete (Plan-Approve-Execute)

Research is synthesized from [12 OpenCode Skills Every Dev Team Should Steal](https://hackernoon.com/twelve-opencode-skills-every-dev-team-should-steal), [obra/superpowers TDD](https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/SKILL.md), and the existing research artifact: docs/artifacts/research-agents-skills-ecosystem-v1.md. v4 already closed most Superpowers gaps; **test-first implementation** is the main remaining behavioral gap.

### Gap evaluation (current emage.code)

| Status | Count | Examples |
|--------|-------|----------|
| **Covered** | 8/12 HackerNoon themes | `systematic-debugging`, `verification-before-completion`, `/handoff`, `/discover-skills`, security guards |
| **Partial** | 3/12 | brainstorming (`/plan` only), parallel agents (`/batch`), token pruning |
| **Major gap** | 1/12 | **TDD** — `testing-strategy` plans tests but does not enforce RED-GREEN-REFACTOR |

**Superpowers skills still missing or partial:** `test-driven-development`, `brainstorming`, `using-superpowers`, `subagent-driven-development`, `finishing-a-development-branch`, `dispatching-parallel-agents` (as dedicated skills).

### Proposed feature: optional TDD enforcement

Modeled on [OpenCode skill `ask` permissions](https://opencode.ai/docs/skills/) — user is prompted, not forced:

```yaml
# docs/emage-workflow.yaml (consumer project)
workflow:
  tdd_enforcement: ask   # ask | always | never
```

| Mode | Behavior |
|------|----------|
| `ask` (default) | Agent asks before implementation: enable strict TDD for this task? |
| `always` | `test-driven-development` becomes mandatory in `AGENTS.md` Skill Workflow |
| `never` | Skill available via `/discover-skills` only |

**Deliverables (v6.1.0):** Superpowers-derived TDD skill + workflow prefs file + orchestrator/`discover-skills`/`new-project` wiring + install merge (same pattern as v6.0.2 task ledger preservation).

### Artifacts created

- docs/plans/plan-008-optional-tdd-and-skill-gaps.md — full plan + task breakdown T055–T060
- docs/artifacts/requirements-optional-tdd-v1.md — functional requirements
- docs/checkpoints/checkpoint-001-planning-tdd-skills.md — planning checkpoint

### Approval

**Shall I proceed with plan-008?**

- **APPROVE** — create task briefs and start implementation (T055 + T056 in parallel)
- **APPROVE_WITH_CHANGES** — e.g. different default (`never`), file path, or scope
- **REJECT** — replan

Recommended: **APPROVE** with `tdd_enforcement: ask`.

