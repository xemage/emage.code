# Artifact: qa-release-v10-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Executor**: qa-engineer, worktree `agent/qa-engineer/T760`. Throwaway clones of `v9.0.0` and of this commit, install targets and virtual environments lived in a scratch folder and were removed. Only this artifact was written to the repository.
- **Gate**: integration (T760). **Date**: 2026-11-07.
- **Target**: `release/v10.0.0` at `3641abfbb9c165c21ad7f4a33a7680efa74739db`. QA did not re-run later commits. If the release files change after this gate, the gates must be re-run on the final tree.
- **Based on**: `docs/tasks/task-T760.md`, `docs/plans/plan-145-release-v10.md` (T760; The user's decisions), `docs/releases/v10.0.0.md` at the target, `docs/artifacts/release-v10-audit-v1.md` § 3, `docs/artifacts/release-rehearsal-t759-v1.md`, format model `docs/artifacts/qa-gate-release-v9-v1.md`.
- **Credentials**: the first suite run, the recording suite run and every installer run had `GITLAB_PERSONAL_ACCESS_TOKEN`, `GITLAB_TOKEN`, `GITLAB_PERSONAL_ACCESS_TOKEN_FILE`, `BRAVE_API_KEY`, `WIKI_TOKEN`, `GITHUB_PERSONAL_ACCESS_TOKEN` and `CWSO_JWT_SECRET` unset. No `docker` command was run. The skip enumeration ran with the session's environment, where `CWSO_JWT_SECRET` is set (checked by name, the value not read), which is why it counts differently (§ Suite).

## Gate Verdict

- **Gate:** integration
- **Verdict:** CONDITIONAL_PASS

No critical or high finding, and every executable gate is green. **The migration path holds: `--update` from a real v9.0.0 install does what M-1 and M-2 say, and `--projections-only` fails as the document warns.** Three medium findings are about what a reader needs for M-2's rebuild to work, and six are low (C1 to C3). This gate does not cover security findings: they are a T762 matter.

## Gates

| Check | Result |
|---|---|
| `sync.mjs --root implementation --check` | exit 0, `OK - no drift across 494 files.` |
| `generate-registry.py --check` | exit 0, `registry is up to date` |
| `check-maturity.py --root implementation` | exit 0, 80 components, 0 failing (agents 28; commands 14 + 5; instructions 4 + 2; skills 7 + 20), as K-1 says |
| `scorecard.py --check` | exit 0, 34 cases, 30 pass, 0 regressions, wrote nothing, as K-2 says |
| `docs/tasks/validate-tasks.py` | exit 0, `TASK LEDGER: PASS (5 active, 557 completed)` |
| Evaluator hash, from `implementation/` | `any_drift= False`, against `evaluator-hash-known-good-v22.json` |
| `tests.functional.test_golden_held_out_isolation` | 8 tests OK |
| `tests.functional.test_root_install_parity --print-drift` | exit 0, `[]` |
| `check-version-consistency.py` | exit 0, PASS, canonical v10.0.0 |
| `check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop`, after the fetch | exit 0, PASS, main=v9.0.0 develop=v9.0.0, `releases_behind=0` (next section) |
| `verify-release-docs.py --tag v10.0.0`, locked parser (`markdown-it-py` 4.2.0, `mdurl` 0.1.2, from `ci/requirements-release.txt`) | exit 1 with 16 lines, every one `unfilled verdict ... value is still pending`: 5 under `## Gate Verdicts` and 11 under `## RELEASE VERDICT`. No other line. As expected until T763. |
| The same on a throwaway copy with those 16 values filled | exit 0, `all documentation checks passed`. One value put back to `pending`: exit 1 (control). |

## What the drift check says before the release merges

Today's PASS **says nothing about v10.0.0**: `origin/main` (`3510b0e9`) and `origin/develop` (`d71002ca`) both still hold the v9.0.0 marker, and the release commits are not on either. `d71002ca` is an ancestor of the target, 6 commits behind.

Against this commit, on a throwaway clone with a local tag `v10.0.0` (never pushed):

| Refs | Result |
|---|---|
| main=v9, develop=this commit, no tag yet (real repository) | FAIL, `develop marker version v10.0.0 is not a known git tag`. By design before the tag; `--develop-ref HEAD` now fails as `refs/remotes/HEAD does not exist` (T730) |
| main=v9, develop=v9, tag exists | PASS, `releases_behind=0` |
| main=v9, develop=v10, tag exists | **PASS** with the grace NOTE, `releases_behind=1` |
| main=v10, develop=v9, tag exists | **FAIL**, main is AHEAD of develop |
| main=v10, develop=v10, tag exists | PASS, `releases_behind=0` |
| `check-release-tag-tree.py --tag v10.0.0 --main-ref`, main=v9 | FAIL. Same tree as the tag: PASS |

So the merge order matters: develop first, then main, then the tag. Main first with develop behind fails the drift gate. A main left behind passes the drift gate and is caught only by `check-release-tag-tree.py`. This is the carry-over of QA-T707-03 (condition C3).

## Suite

`CI=true timeout 1800 python3 tests/run.py`, after `npm ci --ignore-scripts --prefix ci/js --no-audit --no-fund`: **`Ran 2687 tests in 1050.412s`, `OK (skipped=13)`, exit 0.** No failure, so no flake to explain. The worktree stayed clean.

**The skip count differs from the baseline of 24 or 25, and the cause is my run, not the tree.** A second full run through a recording result class gave the same numbers and the reasons: 2703 tests discovered, 2687 started, 13 skips, 0 failures, 0 errors.

- With `CWSO_JWT_SECRET` unset, as in my run, `setUpClass` skips `TestCwsoClientLiveIntegration` (9 tests) and `TestPatternAIntegrationLive` (4 tests) as **one skip each and those tests do not start**. With it set, each of those 13 tests is one skip by its `CWSO_LIVE_CONTRACT_TEST` decorator. That is 11 more, so 24.
- `TestCwsoMcpContractSnapshot` (3 tests) is one `setUpClass` skip either way. It accounts for the rest of the 16 tests not started (9 + 4 + 3).
- A per-module run in the session's environment counted 24 skips, which confirms it. Five slow modules hit that run's 45-second limit (`test_install_script`, `test_poc_audit_server`, `test_install_cursor_removal`, `test_install_exclude_parity`, `test_install_robustness`). None of them skips in the recording run.

The same tests stay unrun in both cases, and no test was lost.

The 13 skips:

| Reason | Count |
|---|---|
| `CWSO_LIVE_CONTRACT_TEST` not set (2 tests, 1 class) | 3 |
| `CWSO_JWT_SECRET` unset, class skipped | 2 |
| CWSO not running on localhost (T223) | 1 |
| `EMAGE_MEMORY_FULL_PIPELINE_TEST` not set | 3 |
| `EMAGE_MEMORY_RETRIEVAL_LATENCY_TEST` not set | 1 |
| `EMAGE_MEMORY_RETRIEVAL_EVAL` not set | 1 |
| `PLAYWRIGHT_CORE_BUNDLE` not set | 1 |
| `pip-audit` not installed | 1 |

Coverage is not measured: this gate has no coverage tool, so the 80% and 95% rows of the report format do not apply. Deployment observability does not apply either: the harness deploys no service.

## Upgrade replay: v9.0.0 install, then v10 `--update`

Setup: clones of tag `v9.0.0` (`e4c7e7d4`) and of the target. An empty git repository with remote `https://gitlab.example.invalid/acme/Widget.git`. `v9 install.sh --platform all` exit 0, committed, so `git status` shows the update's effect. Tag `v10.0.0` does not exist yet, so step 2's `git checkout` was replaced by the clone at the target.

| Item | Outcome | Evidence |
|---|---|---|
| Dry run | **confirmed** | `--update --dry-run`, exit 0: `DRY-RUN: rm -f --` for the five paths, and the target unchanged |
| M-1 five paths | **confirmed** | Present after v9, ABSENT after `--update` on all five, `git status` shows exactly 5 ` D` |
| M-1 renamed copy | **confirmed** | `.claude/commands/my-prepare-release.md` and `.github/prompts/my-pr.prompt.md` deleted by `--update`; no line of the log names them. `--projections-only` (claude-code) deleted it too. A plain install over v9 kept it and deleted `prepare-release.md` |
| M-1 authoring checkout | **confirmed** | Target with `implementation/registry/index.json`, plain install: the command stays (`.claude`, `.pi` checked) |
| M-1 manifest, K-33 | **confirmed** | `authoringOnly` and `files` both name the path in 5 manifests; `.cline` lists none |
| "changed 99 files" | **confirmed** | 94 modified + 5 deleted; nothing in `docs/`, `AGENTS.md`, `CLAUDE.md`; 7 in `implementation/runtime/` |
| "What a target does not receive" | **confirmed**, list incomplete | All eight absent. QA-T760-08 |
| M-2 configs | **confirmed** | No `--index-dir` in `.mcp.json`, Gemini, Opencode, Pi, Cline; `.vscode/mcp.json` has no such server |
| M-2 v9 index not read | **confirmed** | A v9-located directory survives `--update` under the old name. Server start with the generated args: exit 1, `FileNotFoundError ... _index/acme-widget/manifest.json`. Remote `acme/Widget` gave lower case `acme-widget` |
| M-2 `--projections-only` | **confirmed** | v9 install, then v10 `--projections-only` (exit 0, 16 M, 1 D, nothing under `implementation/`): server exit 2, `error: the following arguments are required: --index-dir`. A later `--update` repairs it (the error becomes the index one) |
| M-2 rebuild | **works only with more than M-2 and the install note say** | QA-T760-01, QA-T760-02, QA-T760-03. With `requirements-mcp-server.txt` and `requirements.txt` installed and a lower case id: exit 0, and a real stdio `initialize`, `tools/list` and `retrieve` returned the chunk |
| M-2 no remote | **confirmed** | Exit 1, `RemoteResolutionError` |
| M-2 hand-set `--index-dir` | **confirmed**, and the entry under another name is now **observed** | `custom/index` under the generated name replaced with no note. The same args under `context-retriever-mine` kept |
| M-3 broad root | **confirmed** | Real start of both servers with `HOME` set to the target: exit 1, `PathValidationError`. With `HOME` its parent: both exit 0 |
| M-3 index, child env, names | **confirmed** (functions) | `index_override_error`: all six `PIP_*`/`PIP_AUDIT_*` and `npm_config_registry`, `NPM_CONFIG_REGISTRY`, `npm_config_@acme:registry` refused; `npm_config_cache` allowed. `child_env` drops `NODE_AUTH_TOKEN` and `GITLAB_PERSONAL_ACCESS_TOKEN`. `sensitive_component` true for all eight names |
| M-4 | **confirmed** | The only `tools:` or `mcp__` difference across the agent trees is `[read, search, context-retriever/retrieve]` to `[read, search]` in `.github/agents/context-retriever.agent.md` |
| Rollback Plan | **confirmed** | v10 install, then v9 `--update`: exit 0, 94 M, 5 added, none deleted; 7 in the runtime; `/prepare-release` back; `--index-dir` and the Copilot grant back; `GITLAB_PERMISSION_MODE` still there. v10 `--update` again: exit 0, `git status` empty |

**What the document marks unverified and I ran.** The release manager may use these:

- "No index was built ... so a retrieval on v10 was not run": now run, on a one-chunk project-scope entry, over stdio.
- "Moving the old directory instead ... nobody has tried it": an index built at `_index/em-age-emage.code` and moved to `_index/acme-widget` loaded and answered. `build.py` is unchanged between v9.0.0 and this commit, and I built it with this tree's copy, not with a v9 install.
- "pass `--index-dir` in an entry under a name the generator does not own": `--update` kept the entry. I did not start that entry.

## Document spot-checks

Against the tree or a throwaway clone. Everything here held unless a finding is named.

- **Highlights.** All eight image lines at the `e064671c` digest in `.gitlab-ci.yml`. The five accepted findings (K-15, K-16 with two ids, K-28, K-29). `run-allowlisted` in 7 lines of `.gitlab-ci.yml`. `release-docs-gate` has `timeout: 10 minutes`.
- **Counts.** 6 features, 12 fixes, 5 breaking entries, as the counting rule says. `CHANGELOG.md` has no diff since `v9.0.0` and only `[Unreleased]`. K-18's register numbers match `tracked-debt-register-v11.md`.
- **Citations.** `scripts/install.sh:187`, `:1297-1301` and `:1745-1747` say what the document says. No line of the installer names `releases/v10`. K-33's lines hold, in the generated tree and in a target.
- **M-5.** `sync.mjs` stops on a missing `audience:` and on an `outputFile` outside the allowlist, with the rule in the message.
- **M-6.** `--jwt-secret` and `--jwt-sec` both refused by `sia-executor.py`. `dispatch-test-sia.py` still takes it. `--print-secret`, `-t 1` and `--parquet-store` in the helper, by reading. Docker 29.9.2 and compose v5.6.1 pins and the backslash refusal, by reading. `--workspace` default: QA-T760-06.
- **M-7.** Without the parser: exit 1 with the install command. That command installed the locked set. Refused by a run on a copy: over 131072 characters, a line over 65536, `---` front matter, HTML, `<your-project>` in prose, U+0085, invalid UTF-8 (offset, no content), nesting at the limit, CR in `scripts/install.sh`, a second verdict heading. An HTML comment drew no refusal. `NOT_TAG_CONDITIONS` and `RELEASE_COMMAND` exist in `tests/functional/test_ci_hash_pins.py`.
- **M-8.** `qa-engineer` has `P0 | P1 | P2` and no `P3`. `scrum-master` has `Critical`. `dependency-graphing` colours, `/batch` slug rule, `plan-approve-execute` mapping, `/discover-skills` no packaging step, `/validate-workflow` "(authoring repository only)", the hotfix text in `release-workflow`. No false "differs" note in the v9 to v10 log. The install note no longer says to match an `--index-dir`. `SECURITY.md` § 4.2 and `--strict-storage` exist. `printable`: QA-T760-07.

## Findings

Severity scale: `Critical | High | Medium | Low`. No finding is a regression in behaviour; each is a statement or an omission that this release's readers meet, and the code facts behind QA-T760-01 to -03 also hold at `v9.0.0`: `git diff v9.0.0 HEAD` is empty for both memory requirements files and for `scope_filter.py`, v9's `derive_project_id` lower-cases too, and a v9 `--platform gemini` install generates `--platform-root .claude`.

| ID | Severity | Where | Finding | What I ran |
|---|---|---|---|---|
| QA-T760-01 | Medium | `docs/releases/v10.0.0.md` M-2; `scripts/install.sh:1743-1751` | **M-2's rebuild fails with the dependencies the installer prints.** The note says to run the build "after the dependency install above", and that install is `requirements-mcp-server.txt` (`mcp`, `httpx2`). The build needs `implementation/runtime/memory/requirements.txt`, which neither M-2 nor the printed note names (the comment at `install.sh:1738-1739` does; the target's README does at line 38). A reader who built under v9 may have it, but not on a new machine or in a new venv. | v10 target, `.venv-mcp` with the printed command, then M-2's command: exit 1, `ModuleNotFoundError: No module named 'yaml'`. With `requirements.txt` added: exit 0 |
| QA-T760-02 | Medium | M-2; `implementation/runtime/memory/scope_filter.py:52` | **A mixed-case `--project-id` silently returns nothing.** M-2 says lower case for the directory only, and the command shows `--project-id <org>/<repo>`. `derive_project_id` lower-cases the remote, and the filter compares exactly. A reader who copies `Acme/Widget` from the remote gets a build that succeeds, a server that starts, and an empty `retrieve` with no error. | Remote `acme/Widget`, one project-scope entry: `--project-id acme/widget` and that `project_id` returned the chunk. `Acme/Widget` for both: `wrote 1 chunks`, `"result": []`, `isError: false` |
| QA-T760-03 | Medium | M-2; generated configs; disclosed only in a comment at `implementation/knowledge/mcp/servers.yaml:194` | **On a non-Claude install without `.claude/`, `retrieve` fails even after a correct rebuild.** Every generated entry passes `--platform-root .claude`, and M-2 and Known Issues do not say so. `resolve_platform` needs that directory's manifest. The server starts, so nothing shows until the first query. | `--platform gemini` target, rebuild, stdio call: `isError: true`, `Error executing tool retrieve`. Direct call: `PlatformResolutionError ... .claude/.generated-manifest.json`. With `.gemini` the function returns `gemini`. v9 `--platform gemini` generates the same argument. Opencode, Pi and Cline carry it too (read from an `all` install, not run alone) |
| QA-T760-04 | Low | K-32 | **"Tags `v9.0.0-gate.1` and `v9.0.0-gate.2` are still on the remote" is false today.** Its "(user action A-19, read on 2026-11-06)" is out of date. `resolve_previous_tag`'s point stands. | `git ls-remote` of the project: the newest tags are `v8.0.0`, `v9.0.0`, and 0 refs contain `gate` |
| QA-T760-05 | Low | M-2 | **A nested group is not described.** `https://gitlab.com/group/sub/repo.git` gives `sub/repo` and `_index/sub-repo`, not the top group. `<org>` hides that. The `FileNotFoundError` names the expected path, so a reader can recover for the directory; the `--project-id` then has the same trap as QA-T760-02. | `derive_project_id` and `default_index_dir` on five remotes in temporary repositories |
| QA-T760-06 | Low | M-6 | **"not `/tmp/cwso-credcheck*`" is literally false.** The default is `mktemp -d "${TMPDIR:-/tmp}/cwso-credcheck.XXXXXXXX"`, which matches that glob. What changed is a fresh private directory, not the prefix. | Read `scripts/cwso-deploy-helper.sh:186`, not run (`verify` drives Docker) |
| QA-T760-07 | Low | M-8 Installer | **"a non-ASCII name prints with `?`" holds only where `printable` is used.** `scripts/install.sh:1693` (`Installed emage.code (...) into $TARGET`) and the `--update requires an existing ... install` error print a target name raw. | Target `tgé`: both lines show `tgé`. `--platform 'naïve'`: `na??ve` |
| QA-T760-08 | Low | "What a target does not receive"; M-8 Docs; K-27 | **The list omits `implementation/PREREQUISITES.md` and `implementation/SECURITY.md`**, which M-8 and K-27 point to and which a target does not hold. The install log tells a target's reader "Details: implementation/PREREQUISITES.md". Same class as K-33. | `ls` of a v10 target's `implementation/`: `__init__.py`, `runtime` only |
| QA-T760-09 | Low (carry-over of QA-T707-03) | `scripts/check-main-develop-drift.py` | The 1-release grace passes main=v9 with develop=v10. Today's run is vacuous for v10. See the drift section. | The table above |

Observations, not findings: `onnxruntime` prints `pthread_setaffinity_np` lines on this host during a build, harmless here. The build's log says `wrote 0 chunks` on a target with no vault, which is correct, and the server then starts and returns `[]`.

## Conditions

- **C1 (QA-T760-01, -02, -03): owner `release-manager`.** Mitigation: in M-2, name `implementation/runtime/memory/requirements.txt` as needed for the rebuild; say `--project-id` must be the lower case form, with its entries' `project_id`; add a Known Issue that `retrieve` needs `.claude/` as generated. Deadline: before T763 issues the verdict. Then re-run `verify-release-docs.py`. The code behind them (the printed note, the `--platform-root` default) is for the debt register, owner `backend-developer` through the orchestrator, next release. `install.sh` need not change for this release.
- **C2 (QA-T760-04 to -08): owner `release-manager`.** Mitigation: one clause each in K-32, M-2, M-6, M-8 and the target list, or tracked as LOW. Deadline: before T763, with C1.
- **C3 (QA-T760-09): owner `orchestrator`.** Mitigation: merge `release/v10.0.0` to develop, then to main, before the tag; re-run the drift check after the tag and expect `releases_behind=0`. Deadline: the v10.0.0 tag pipeline.

## Acceptance criteria (plan-145, T760)

| Criterion | Evidence | Status |
|---|---|---|
| Full suite | § Suite, exit 0 | PASS |
| Golden suite and scorecard | Scorecard, hash, isolation; the golden contract tests are inside the suite | PASS |
| `verify-release-docs.py` | Only the verdict lines; a filled copy passes | PASS (until T763) |
| `check-version-consistency.py` | PASS | PASS |
| `check-main-develop-drift.py` | PASS, vacuous for v10 | PASS with C3 |
| Install and `--update` on a throwaway target, showing the T725 deletion | § Upgrade replay | PASS |

## Unverified or not run

- Every live client: no assistant started a server; my stdio calls came from a small script.
- A rejection by the eMudhra block, the tag pipeline, the `release` job, `check-release-tag-tree.py` on a real tag. All remain with K-30 and K-34.
- `--update` from an index really built by a v9 install: the "moved" check used this tree's `build.py`, unchanged since v9.0.0.
- NuGet with a credential in a variable; `run_pip_audit` and `run_npm_audit` end to end (`pip-audit` is not installed here).
- `cwso-deploy-helper.sh verify`, `export` and `cwso-proxmox-setup.sh`: read, not run. Docker is out of scope.
- The `.tmp` and `.bak` names of `merge-task-docs.py`, read by the document, not run here.
- GitLab's rendering of `CHANGELOG.md` entries. Windows.
- The `--platform-root .claude` failure alone on Opencode, Pi and Cline: read, not run.
