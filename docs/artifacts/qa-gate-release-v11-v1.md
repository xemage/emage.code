# Artifact: qa-gate-release-v11-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Executor**: qa-engineer, worktree `agent/qa-engineer/T818`. A detached clean worktree of the target for the suite, detached worktrees of `v10.0.0` and of the target for the installer runs, install targets and a virtual environment lived in the session scratch folder and were removed. Only this artifact was written to the repository.
- **Gate**: integration (T818). **Date**: 2026-11-13.
- **Target**: `release/v11.0.0` at `67222765` (`docs(plan-161): addendum 3 (probe tag), close T817, briefs for the gates (T818 to T820)`). QA did not re-run later commits. If the release files change after this gate, the gates are re-run on the final tree.
- **Based on**: `docs/tasks/task-T818.md`; `docs/plans/plan-161-release-v11.md` (§ Task Decomposition item 6, Addenda 1 to 3); `docs/releases/v11.0.0.md` at the target; `docs/artifacts/release-v11-audit-v1.md` (T813); ADR-013, ADR-014 (removal behaviour, D5 / D4); format model `docs/artifacts/qa-release-v10-v1.md` (the v10.0.0 QA gate; `qa-gate-release-v10-v1.md` does not exist).
- **Credentials**: every suite and installer run had `GITLAB_PERSONAL_ACCESS_TOKEN`, `GITLAB_TOKEN`, `GITLAB_PERSONAL_ACCESS_TOKEN_FILE`, `BRAVE_API_KEY`, `WIKI_TOKEN`, `GITHUB_PERSONAL_ACCESS_TOKEN` and `CWSO_JWT_SECRET` unset, under `ulimit -v 4000000` and `timeout`. No server was launched, no `docker` command was run, `tests/golden/held-out/` was not opened.

## Gate Verdict

- **Gate:** integration
- **Verdict:** CONDITIONAL_PASS

No critical or high finding, and every executable gate is green. **The removal behaviour holds:** `--platform pi` and `--platform gemini` are refused in every mode and letter case before any write, and a real v10.0.0 `--platform all` install keeps every byte under `.pi/` and `.gemini/` through `--update` and `--projections-only`, with the ADR-013 / ADR-014 notices. One medium finding is a cleanup procedure in M-1 and M-2 that fails as written (QA-T818-02). Three findings are low, one of them a reproduction of the ungraded TD-T774-01 on this release's own security fix (QA-T818-01), one a pre-tag condition about the probe tag (QA-T818-04). Conditions C1 to C3 below. This gate does not grade security findings: they are a T820 matter.

## Gates

| Check | Command | Result |
|---|---|---|
| Full suite, clean copy | `git worktree add --detach <scratch>/suite 67222765`; `npm ci --ignore-scripts --prefix ci/js` (exit 0); `CI=true timeout 1800 python3 tests/run.py` | exit 0, `Ran 2744 tests in 1037.188s`, `OK (skipped=24)`, no `FAIL:` or `ERROR:` line. The plan's baseline is 2744 OK (skipped=25). The one skip fewer is `tests.performance.test_team_health ... test_every_active_task_has_a_plan`, which skips only on an empty active queue and ran `ok` here, with 3 active tasks. The other 24 skip reasons were not enumerated **(unverified)**. The clean copy was left with no change (`git status` empty) |
| Golden contract tests | `python3 -m unittest` over the eleven `tests.functional.test_golden_harness_*`, `test_golden_held_out_isolation`, `test_golden_suite_format`, `test_scorecard_artifact_no_drift` modules | exit 0, `Ran 173 tests`, `OK` (they also run inside the full suite) |
| Held-out isolation | `python3 -m unittest tests.functional.test_golden_held_out_isolation` | OK |
| Scorecard | `python3 scripts/scorecard.py --check` | exit 0, `OK — committed content matches a fresh run (34 cases, 30 pass, 0 regressions). Wrote nothing.` |
| Knowledge drift | `node implementation/scripts/sync.mjs --root implementation --check` | exit 0, `OK - no drift across 314 files.` (494 at v10.0.0; the Pi and Gemini trees are gone) |
| Registry | `python3 implementation/scripts/generate-registry.py --check` | exit 0, `registry is up to date` |
| Maturity | `python3 implementation/scripts/check-maturity.py --root implementation` | exit 0, 0 failing in every class |
| Task ledger | `python3 docs/tasks/validate-tasks.py` | `TASK LEDGER: PASS (3 active, 617 completed)` |
| Root parity | `python3 -m tests.functional.test_root_install_parity --print-drift` | `[]` |
| Version consistency | `python3 scripts/check-version-consistency.py` | exit 0, `canonical version is v11.0.0; no older version references found outside the exclusion list`, `VERSION CONSISTENCY: PASS` |
| Release docs, locked parser | scratch venv, `pip install --require-hashes --only-binary=:all: -r ci/requirements-release.txt` (exit 0, `markdown-it-py` 4.2.0); `python scripts/verify-release-docs.py --tag v11.0.0` | exit 1 with 16 lines, every one `unfilled verdict ... value is still pending`: 5 under `## Gate Verdicts` (Architecture, Implementation, Integration, Security, Release) and 11 under `## RELEASE VERDICT` (Status to Independent check). **No other error.** As expected until T821. `scripts/verify-release-docs.py` and `ci/requirements-release.txt`: `git diff --stat v10.0.0 HEAD` empty, as M-8 says |
| Main/develop drift, as the CI job runs it | `git fetch origin main develop`; `git fetch origin 'refs/tags/*:refs/tags/*'`; `python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop` | exit 0, `main=v10.0.0 develop=v10.0.0 releases_behind=0`, `MAIN-DEVELOP DRIFT: PASS`. `origin/main` `623eea7c`, `origin/develop` `81520c31`: neither holds the release commits, so this PASS **says nothing about v11.0.0** (next section) |

## What the drift check says before the release merges

The script accepts only remote refs (`--develop-ref HEAD` and a local branch both fail with `refs/remotes/... does not exist`, by design since T730). The pure `evaluate()` was run in memory with the real tag list, which holds the probe tag `v11.0.0-gate.1` (`git ls-remote --tags origin`: 1 ref holds `gate`):

| main / develop markers | Tags | Result |
|---|---|---|
| v10 / v11 | as today (no `v11.0.0`) | FAIL, `develop marker version v11.0.0 is not a known git tag`. By design before the tag |
| v11 / v11 | `v11.0.0` added | PASS, `releases_behind=0` |
| v10 / v11 | `v11.0.0` added, probe tag present | **FAIL**, `releases_behind=2`, `missing releases on main: v11.0.0-gate.1, v11.0.0` |

At v10.0.0 the same v10/v11 state passed with the grace NOTE (`releases_behind=1`). The difference is the probe tag, which `semver_key` counts as a release (QA-T818-04). With the planned order (develop, then main, then the tag) the tag pipeline sees v11/v11 and passes. The develop-push job `main-develop-drift` (`allow_failure: true`) will show FAIL between the merge to develop and the merge to main while the probe tag exists. Expected and harmless, but not what the v10 gate recorded.

## Install and upgrade replay

All runs from detached worktrees of `v10.0.0` and of `67222765`, into a fresh `git init` target, credentials unset.

| Step | Result |
|---|---|
| v10.0.0 `scripts/install.sh --target <t> --platform all` | exit 0, 548 files, `.pi/` and `.gemini/` present with manifest and sidecar |
| Own files added and committed: `.pi/qa-own.txt`, `.gemini/qa-own.txt`, a synthetic `.gemini/.env`, an own server `qa-own` in `.pi/mcp.json` | 183 files under `.pi/` and `.gemini/`, sha256 list recorded |
| This branch `--platform all --update` | exit 0. Both notices printed in full, word for word as `scripts/install.sh:1324-1327` and `:1347-1351`; then the five `rsync --delete` warnings for `.github`, `.opencode`, `.claude`, `.cline`, `.clinerules`. sha256 list of `.pi/` and `.gemini/` **identical** (own files, own server, `.env` kept) |
| Files changed by that `--update` | 33 modified, 0 added, 0 deleted (git status). The document says 35. The two missing are the lock files of QA-T818-01 |
| Control, the same v10 state with every target mtime set to 2026-11-07 (as a real install made days earlier has), fresh checkout of the target | exit 0, **35 modified**, 0 added, 0 deleted; the tree then equals a fresh v11 install outside `.pi/` and `.gemini/` (`diff -rq` empty). This matches the document |
| `--platform all --projections-only` on the updated target | exit 0, both notices, nothing changed, `.pi/` and `.gemini/` identical |
| A second `--update` | exit 0, nothing changed (idempotent) |
| `.pi` and `.gemini` as symlinks to directories outside the target, `--update` | exit 0, no notice (as M-1 says: a symlinked `.pi` is not read), the link targets byte-identical |
| `--platform pi`, `PI`, `Pi`, `gemini`, `GEMINI`, `Gemini`, each plain, `--update`, `--projections-only`, `--dry-run`, on the existing target and on a non-existent target (24 x 2 runs) | every run exit 1 with the exact ADR-013 D5 / ADR-014 message (`error: platform 'pi' was removed in v11.0.0 (see docs/releases/v11.0.0.md). Existing .pi/ files in your project are not touched. Nothing was written.`, and the Gemini twin); the non-existent target was never created; the existing target unchanged (git status empty) |
| Rollback claim: the v10.0.0 installer `--update` on the updated target | exit 0; deletes `.pi/qa-own.txt`, `.gemini/qa-own.txt` and `.gemini/.env`, 34 modified. Matches M-1 / M-2 "Rollback" (and shows why "commit or back up first" matters) |
| Fresh install of this branch, `--platform all` | exit 0, 365 files; no `.pi/` or `.gemini/`; four sidecars (`.mcp.json`, `.vscode`, `.opencode`, `.cline`) |
| Per platform: `github`, `opencode`, `claude-code`, `cline` | each exit 0 (139, 138, 139, 92 files), only its own trees |
| `--update` diff of `.cline/mcp.json` and `.opencode/opencode.json` | `--platform-root .claude` became `.cline` and `.opencode`, as M-4 says |
| "What a target does not receive" | on the fresh target: no `scripts/`, `docs/releases/`, `.gitlab-ci.yml`, `CONTRIBUTING.md`, `implementation/PREREQUISITES.md` (and no `implementation/SECURITY.md`). Matches |

## Document commands run locally

| Command (section) | Result |
|---|---|
| `scripts/install.sh --target <t> --platform <name>` for each value of the Install table | exit 0 each (above) |
| `scripts/install.sh --help` (Install) | exit 0; lists `github | opencode | claude-code | cline | all` |
| `scripts/install.sh --target <t> --platform <name> --update` (Migration Guide step 2) | exit 0 (above), run from the release tip in place of `git checkout v11.0.0` |
| M-1 / M-2 cleanup, in the written order, on a copy | **fails** at the second step (QA-T818-02). In the corrected order: `.pi/` left with `mcp.json` (only `qa-own`) and `qa-own.txt`; `.gemini/` with `settings.json` (`{"hooks": {}, "mcpServers": {}}`), `.env` and `qa-own.txt` |
| M-5 build, `--project-id Acme/Widget` with remote `https://gitlab.com/Acme/Widget.git` | exit 2, `project id must be the lower-case <org>/<repo> id ...; got 'Acme/Widget'` |
| M-5 build, `--project-id acme/widget` | exit 0, `wrote 0 chunks, 0 rejections` |
| M-5 build, `--project-id acme/other` (lower case, not the remote's) | **exit 0**, index written (QA-T818-03) |
| M-8 local gate: `pip install --require-hashes --only-binary=:all: -r ci/requirements-release.txt` in a venv | exit 0 (needed PyPI) |
| M-6 `node --version` | runs; this host has v24.19.0, below the stated 24.22.3 minimum. A host fact, not a release finding; nothing warns, as M-6 says |

Not run (network, credentials, or a tag that does not exist yet): `git clone https://gitlab.com/...`; `git fetch --tags && git checkout v11.0.0`; M-5's `python3 -m venv .venv-mcp && ... pip install -r implementation/runtime/memory/requirements.txt` (the build above ran on the host's Python, which has the packages); M-6's two `pip install --require-hashes -r .../requirements-mcp-server.lock.txt` lines **(unverified)**; `/new-project`; any MCP server.

## Line citations spot-checked

`scripts/install.sh:187`, `:191-198`, `:1301`, `:1305`, `:1313-1327`, `:1336-1351`, `:1358`, `:1359`, `:1735-1741`; `.gitlab-ci.yml:104`, `:116`, `:160`, `:181`, `:255`, `:282`, `:306`; `implementation/scripts/sync.mjs:208`; `implementation/PREREQUISITES.md:4`; the `opentelemetry-api==1.45.2` pin at line 244 of both runtime lock files. Each holds what the document says.

## Findings

Severity scale: `Critical | High | Medium | Low`.

| ID | Severity | Where | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| QA-T818-01 | Low | `scripts/install.sh:925-934`, `:974-983` (`rsync -a`); `docs/releases/v11.0.0.md` M-6, Migration Guide count | **TD-T774-01 reproduced on a user `--update`, on this release's one security fix.** `rsync -a` skips a changed file of equal size whose mtime falls in the same second. The two runtime lock files change only `1.45.1` to `1.45.2` (same size, 55414 bytes), so a skipped copy leaves `opentelemetry-api==1.45.1` in the target, and M-6's action `pip install --require-hashes -r implementation/runtime/<dir>/requirements-mcp-server.lock.txt` then re-installs 1.45.1, silently. The trigger needs source and target mtimes in the same second: rare for a person, plausible for automation that clones and installs in one job. TD-T774-01 says "Not reproduced here" and has no grade | v10 target from a `v10.0.0` checkout made in the same second as the v11 checkout: `--update` exit 0, 33 modified, both locks still `1.45.1` (`stat`: equal size, mtimes `22:33:22.00` vs `22:33:22.28`). A target cloned in the same second as the source: 30 modified. Control with old mtimes: 35, both `1.45.2` | Release document: in M-6, a check after `--update`, `grep '^opentelemetry-api' implementation/runtime/*/requirements-mcp-server.lock.txt` must show `1.45.2`, else touch the clone's files (`find implementation -type f -exec touch {} +` in the emage.code clone) and re-run `--update`; one Known Issue line naming TD-T774-01. T820 to grade TD-T774-01. Code fix (`--checksum` or a post-copy compare) is for the register, batch I |
| QA-T818-02 | Medium | `docs/releases/v11.0.0.md` M-1 "To clean up", M-2 "To clean up" | **The cleanup fails in the written order.** Step 1 deletes "the paths listed under `files` in `.pi/.generated-manifest.json` except `mcp.json`". That list holds `mcp.json.provenance.json`, which step 2 needs to know which servers are the generator's. The same holds for Gemini: `.gemini/.generated-manifest.json` lists `settings.json.provenance.json`. A reader who follows the text loses the generator-owned key list; recovery needs the backup the document asks for, or the v10.0.0 tag | Both manifests read: `.pi` files include `mcp.json`, `mcp.json.provenance.json`; `.gemini` files include `settings.json`, `settings.json.provenance.json`. Run in order on a copy: `FileNotFoundError: .pi/mcp.json.provenance.json`. Sidecar first: clean result (Document commands) | Swap the order in M-1 and M-2: first edit the config by the sidecar's `generatorOwnedKeys` (and Gemini's `hooks.AfterTool`), then delete the listed files except the config (the sidecar goes with them), then the manifest and empty folders. Or say "except `mcp.json` and `mcp.json.provenance.json`" (and the Gemini twins). Also: the manifests list `prompts/prepare-release.md` under `authoringOnly`, a file a target does not hold, so `rm` of the list reports one missing path; one clause ("a missing path is fine") avoids alarm |
| QA-T818-03 | Low | `docs/releases/v11.0.0.md` M-5 "Action"; `scripts/install.sh:1746` | **"refuses a `--project-id` that is not the derived lower-case `org/repo` of the git remote `origin`" is broader than the code.** `build.py` checks the form only (`is_derived_project_id`), not equality with the remote. A lower-case id that is not the remote's is accepted, and the server, which derives its id from the remote, then filters every project entry out: the silent empty result of QA-T760-02 in another shape. The printed note says the same ("the build refuses any other") | Remote `Acme/Widget`: `--project-id acme/other` exit 0, index written; `Acme/Widget` exit 2; `acme/widget` exit 0. `implementation/runtime/memory/build.py:51-61` | Document: "refuses a `--project-id` that is not in lower-case `org/repo` form; it does not compare it with the remote, so pass the remote's own id". The printed note and an equality check are for the register (owner `backend-developer`, next release) |
| QA-T818-04 | Low | `docs/releases/v11.0.0.md` K-32; `scripts/publish-release.py:289-316`; `scripts/check-main-develop-drift.py:90-96` | **While the probe tag `v11.0.0-gate.1` exists, it is v11.0.0's previous tag.** K-32 says "A pre-release sorts below its core version in any case", which is true but no comfort here: it sorts below `v11.0.0` and above `v10.0.0`, so `resolve_previous_tag("v11.0.0")` returns `v11.0.0-gate.1`, and the release job's `CHANGELOG.md` artifact (`expire_in: never`) says "Commits since v11.0.0-gate.1" and lists only the commits after `01fe29e4`. The Release description comes from the document and is not affected. The drift check also counts it (previous section). At v10.0.0 the probes were `v9.0.0-gate.*`, below the previous release, so K-32's reasoning held then | In memory with the real tag list plus `v11.0.0`: sorted `['v11.0.0', 'v11.0.0-gate.1', 'v10.0.0', ...]`, previous tag `v11.0.0-gate.1`. `git ls-remote --tags origin`: 1 ref holds `gate` today. That the release job's clone fetches all tags is from v10's correct previous tag, not read in GitLab **(unverified)** | Make the probe tag's deletion a precondition of the tag: the user deletes `v11.0.0-gate.1` (Addendum 3's user action) and the orchestrator checks `git ls-remote --tags origin` holds no `gate` ref before pushing `v11.0.0`. K-32 to say so, and to drop "in any case". A code change (skip pre-releases of the same core version in `resolve_previous_tag`) is for the register |

Observations, not findings: `onnxruntime` prints `pthread_setaffinity_np` lines during the build on this host, harmless. `--update` leaves `.mcp.json` and `.vscode/mcp.json` unchanged on this target; the 35 changed paths are the knowledge-text files of M-9, the three memory runtime files of M-5, the two locks, `AGENTS.md` and the two merged configs of M-4.

## Conditions

- **C1 (QA-T818-02): owner `release-manager`.** Mitigation: fix the order of M-1 and M-2's cleanup as in the Fix column, then re-run `verify-release-docs.py`. Deadline: before T821 issues the verdict.
- **C2 (QA-T818-01, -03): owner `release-manager`** for the document lines (M-6 check, Known Issue for TD-T774-01, M-5 wording); **`security-engineer` (T820)** to grade TD-T774-01 now that it is reproduced; the code fixes go to the register through the orchestrator, owner `backend-developer`, next release. Deadline: before T821.
- **C3 (QA-T818-04): owner `orchestrator`, with the user's action.** Mitigation: the probe tag `v11.0.0-gate.1` is deleted in the web UI and `git ls-remote --tags origin` shows no `gate` ref before `v11.0.0` is pushed; merge `release/v11.0.0` to develop, then to main, before the tag; after the tag, `check-main-develop-drift.py` expects `releases_behind=0` and the `CHANGELOG.md` artifact says "Commits since v10.0.0". Deadline: the v11.0.0 tag push (T822 step 2).

## Acceptance criteria (plan-161 § Task Decomposition item 6)

| Criterion | Evidence | Status |
|---|---|---|
| Full suite | § Gates | PASS |
| Golden suite and scorecard | 173 golden contract tests OK; scorecard `--check` OK, 34 cases, 0 regressions; held-out isolation OK | PASS |
| `verify-release-docs.py` | only the 16 pending verdict values | PASS (until T821) |
| `check-version-consistency.py` | PASS, v11.0.0 | PASS |
| `check-main-develop-drift.py` | PASS, vacuous for v11.0.0 | PASS with C3 |
| Install and `--update` on a throwaway target; Pi and Gemini refusals; no `.pi/` or `.gemini/` tree deleted | § Install and upgrade replay | PASS (with C2 for QA-T818-01) |

## Unverified or not run

- The tag pipeline, the `release` job on the dedicated runner, `check-release-tag-tree.py` on a real tag, and whether the release job's clone fetches the probe tag (QA-T818-04).
- Every live client and MCP server: no assistant started; M-4's live resolution stays with K-20.
- The network steps listed under Document commands, in particular M-6's two `pip install --require-hashes` lines.
- Whether A-22 is done: the user's own settings files were not opened.
- Windows, macOS, a host without `rsync` (the `cp` fallback was not exercised in this gate; the suite covers it).
