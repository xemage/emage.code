# Artifact: qa-gate-release-v12-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Executor**: qa-engineer, worktree `agent/qa-engineer/T875`. A detached clean worktree of the target for the suite, a `git archive v11.0.0` tree, install targets, a memory-build fixture and a virtual environment lived in the session scratch folder. Only this artifact was written to the repository.
- **Gate**: integration (T875). **Date**: 2026-11-19.
- **Target**: `release/v12.0.0` at `90124fb6` (`docs(plan-182): briefs for T874 to T877`). QA did not re-run later commits. If the release files change after this gate, the gates are re-run on the final tree.
- **Based on**: `docs/tasks/task-T875.md`; `docs/plans/plan-182-next-release.md` (§ Task Decomposition item 8, Addenda 1 to 3); `docs/releases/v12.0.0.md` at the target; `docs/artifacts/release-next-audit-v1.md` (T869; B-1 to B-18, MI-1 to MI-9); `CONTRIBUTING.md` § Cutting a release; format model `docs/artifacts/qa-gate-release-v11-v1.md`.
- **Credentials**: every suite and installer run had `GITLAB_PERSONAL_ACCESS_TOKEN`, `GITLAB_TOKEN`, `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` and `BRAVE_API_KEY` unset (the suite also `WIKI_TOKEN`, `GITHUB_PERSONAL_ACCESS_TOKEN`, `CWSO_JWT_SECRET`), under `ulimit -v` and `timeout`. No MCP server or assistant was launched, no `docker` command was run, no job log was read, `tests/golden/held-out/` was not opened.

## Gate Verdict

- **Gate:** integration
- **Verdict:** CONDITIONAL_PASS

No critical, high or medium finding, and every executable gate is green. A v11.0.0 install updated by this tree equals a fresh v12.0.0 install byte for byte, with exactly the 36 modified and 1 deleted files the release document states. The Opencode permission maps match their sources for all 28 agents. The v11 findings QA-T818-01 and QA-T818-03 are fixed in the code. Two findings are low and concern the release document's wording (QA-T875-01, QA-T875-02). One condition carries over from v11.0.0: the probe tag `v12.0.0-gate.1` exists on `origin` and must be deleted before `v12.0.0` is pushed (K-32; C3). This gate does not grade security findings: they are a T877 matter.

## Gates

| Check | Command | Result |
|---|---|---|
| Full suite, clean copy | `git worktree add --detach <scratch>/suite 90124fb6`; `npm ci --ignore-scripts --prefix ci/js` (exit 0); `CI=true timeout 1800 python3 tests/run.py` | exit 0, `Ran 2820 tests in 1110.889s`, `OK (skipped=13)`, no `FAIL:` or `ERROR:` line; the clean copy was left unchanged (`git status` empty apart from the ignored `ci/js/node_modules`). The orchestrator's develop baseline is 2833 OK (skipped=25). **The difference is explained:** the tree discovers 2836 tests (`countTestCases` over the `tests/run.py` suite, 0 loader failures), and the release commits since `6afb6143` change no file under `tests/`. 16 tests were not counted because their class or module skipped in `setUpClass`: `test_cwso_client_live` (9 of 11), `test_pattern_a_integration_live` (4) and `test_cwso_mcp_contract_snapshot` (3). The first two skip at class level when no `CwsoClient` can be built from the environment, and `CWSO_JWT_SECRET` was unset here; the third needs `CWSO_LIVE_CONTRACT_TEST=1`. A run with the CWSO variables set builds the client, so the 13 tests of the first two modules count and skip one by one: 2836 - 3 = 2833, and 13 per-test skips in place of the class-level ones give the 12 more skips. That the orchestrator's run had the CWSO variables set is inferred from the counts **(unverified)**; none of these tests runs without a live CWSO in either case |
| Golden contract tests | `python3 -m unittest` over the eleven `tests.functional.test_golden_*` and `test_scorecard_artifact_no_drift` modules (the repository has no separate golden runner; `tests/golden/README.md` says the cases are not executed live by the suite) | exit 0, `Ran 173 tests`, `OK` (they also run inside the full suite) |
| Held-out isolation | `tests.functional.test_golden_held_out_isolation`, in the run above | OK |
| Scorecard | `python3 scripts/scorecard.py --check` | exit 0, `OK — committed content matches a fresh run (34 cases, 30 pass, 0 regressions). Wrote nothing.` |
| Knowledge drift | `node implementation/scripts/sync.mjs --root implementation --check` | exit 0, `OK - no drift across 314 files.` |
| Registry | `python3 implementation/scripts/generate-registry.py --check` | exit 0, `registry is up to date` |
| Maturity | `python3 implementation/scripts/check-maturity.py --root implementation` | exit 0, 0 failing in every class |
| Task ledger | `python3 docs/tasks/validate-tasks.py` | `TASK LEDGER: PASS (4 active, 672 completed)` |
| Root parity | `python3 -m tests.functional.test_root_install_parity --print-drift` | `[]` |
| Version consistency | `python3 scripts/check-version-consistency.py` | exit 0, `canonical version is v12.0.0; no older version references found outside the exclusion list`, `VERSION CONSISTENCY: PASS` |
| Release docs, locked parser | scratch venv, `pip install --require-hashes --only-binary=:all: -r ci/requirements-release.txt` (exit 0, `markdown-it-py` 4.2.0); `python scripts/verify-release-docs.py --tag v12.0.0` | exit 1 with 16 lines, every one `unfilled verdict ... value is still pending`: 5 under `## Gate Verdicts`, 11 under `## RELEASE VERDICT`. **No other error.** As expected until T878. `git diff --stat v11.0.0 HEAD` of `scripts/verify-release-docs.py` and `scripts/publish-release.py`: empty, as M-9 says; `ci/requirements-release.txt` changed in one header comment line only (the T880 cut-off note), the pin and hashes are unchanged |
| Main/develop drift, as the CI job runs it | `git fetch origin main develop`; `git fetch origin 'refs/tags/*:refs/tags/*'`; `python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop` | exit 0, `main=v11.0.0 develop=v11.0.0 releases_behind=0`, `MAIN-DEVELOP DRIFT: PASS`. `origin/main` `2bb487ef`, `origin/develop` `6afb6143`: neither holds the release commits, so this PASS **says nothing about v12.0.0** (next section). The script accepts only remote refs |

## What the drift check and the changelog say before the release merges

`git ls-remote --tags origin` holds `v11.0.0` and the probe tag `v12.0.0-gate.1` (the v11 probe `v11.0.0-gate.1` is gone from `origin`; a stale local copy remains in this clone and does not matter to CI). The pure functions were run in memory with the real remote tag list plus `v12.0.0`:

| State | `releases_behind` (drift script) | Previous tag of `v12.0.0` (`publish-release.py`, `tag_sort_key` + `resolve_previous_tag`) |
|---|---|---|
| Probe tag present, main v11 / develop v12 | 2: **FAIL** (grace is 1) | `v12.0.0-gate.1` (the `CHANGELOG.md` artifact would say "Commits since v12.0.0-gate.1") |
| Probe tag present, v12 / v12 | 0: PASS | `v12.0.0-gate.1` |
| Probe tag deleted, v11 / v12 | 1: PASS with grace | `v11.0.0` |
| Probe tag deleted, v12 / v12 | 0: PASS | `v11.0.0` |

The code is unchanged since v11.0.0, so QA-T818-04 holds as before. The release document records it as K-32 ("must be deleted before `v12.0.0` is pushed"); `CONTRIBUTING.md` § Cutting a release has no probe-tag step. Condition C3.

## Install and upgrade replay

All runs from the worktree at `90124fb6` and from `git archive v11.0.0` extracted into scratch, into fresh `git init` targets, credentials unset.

| Step | Result |
|---|---|
| Fresh install, `scripts/install.sh --target <t> --platform all` | exit 0, 364 files; `.claude`, `.cline`, `.clinerules`, `.github`, `.opencode` (28 agents), `.vscode`, `.mcp.json` with sidecar, `AGENTS.md`, `CLAUDE.md`, `docs/`, `implementation/`; no `.pi/` or `.gemini/` |
| Opencode maps, 28 `.opencode/agents/*.md` parsed with PyYAML | every agent has `permission:`, none has `tools:`. `bash: deny` 13; `edit: deny` 8; `webfetch: deny` and `websearch: deny` 6 each; `task: deny` 26 |
| The 13 agents without `execute` (context-retriever, demo-agent, evaluation-agent, poc-security-engineer, poc-technical-writer, product-owner, scrum-master, security-engineer, solution-architect, technical-debt-narrator, technical-writer, technology-scout, ux-designer) | each: `bash: deny`, `task: deny`, `read: {gitlab-mcp, gitlab-mcp/*, */gitlab-mcp, */gitlab-mcp/*: deny}`, `external_directory: {*/gitlab-mcp/*: deny}`. No other agent has a `read` or `external_directory` key |
| Grants against the sources | scripted cross-check of every agent's source `tools:` line in `implementation/knowledge/agents/` against its map (`execute`→`bash`, `edit`→`edit`, `web`→`webfetch`/`websearch`, `agent`→`task`, `execute`↔ the `read` map): **0 mismatches** over 28 agents |
| The two orchestrators | `task: {"*": deny, ...}` with 14 named allows each: `orchestrator` the 14 production subagents, `poc-orchestrator` the 14 PoC subagents; no other value. The keys are frontmatter display names (`Backend Developer`); `mcp-agent-denials-evidence-v3.md` § source reading says the `task` pattern is matched against the frontmatter `name`, so this is consistent (a refused or allowed launch is not observed; K-20) |
| No `read` / `external_directory` allow; no `bash`/`webfetch`/`websearch` allow | none found. `edit: allow` is written for the 20 agents that hold `edit` (QA-T875-01) |
| MCP pins in the generated configs | `.mcp.json`, `.opencode/opencode.json`, `.cline/mcp.json`: `@brave/brave-search-mcp-server@2.1.5` and `@modelcontextprotocol/server-filesystem@2.4.0`; `.vscode/mcp.json`: Brave 2.1.5 only (GitHub carries no `extended` server, as `AGENTS.md` says). No other Brave or filesystem version anywhere in the target |
| v11.0.0 `--platform all` install (from `git archive v11.0.0`), plus an own file `.opencode/agents/qa-own.md`, committed | exit 0, 365 files |
| This tree `--platform all --update` | exit 0; the five `rsync --delete` warnings; **36 modified, 1 deleted** (`qa-own.md`): the 28 agents, `.mcp.json`, `.vscode/mcp.json`, `.opencode/opencode.json`, `.cline/mcp.json`, `AGENTS.md`, `implementation/runtime/memory/{README.md,build.py,context_retriever.py}`. Matches the Migration Guide's count and list word for word |
| Updated target vs fresh install | `diff -rq --exclude=.git`: **empty** (identical) |
| A second `--update` | exit 0, 0 changes (idempotent) |
| Rollback: the v11.0.0 installer `--update`, then this tree's `--update` again | exit 0; target equals the v11 commit except the own `qa-own.md` (not restored), `.mcp.json` back to Brave 2.1.4; forward again exit 0, 0 changes against the v12 state. Matches the Rollback Plan |
| `--platform pi`, `PI`, `Pi`, `gemini`, `GEMINI`, `Gemini`, each plain, `--update`, `--projections-only`, `--dry-run`, on the existing target and on a non-existent target (24 x 2 runs) | every run exit 1 with the ADR-013 / ADR-014 message (`error: platform 'pi' was removed in v11.0.0 (see docs/releases/v11.0.0.md). Existing .pi/ files in your project are not touched. Nothing was written.`, and the Gemini twin); the non-existent target was never created; the existing target unchanged (`git status` empty) |
| "What a target does not receive" | absent: `scripts/`, `docs/releases/`, `.gitlab-ci.yml`, `CONTRIBUTING.md`, `implementation/PREREQUISITES.md`. **Present: `docs/wiki/`** with `README.md` and `home.md` (QA-T875-02) |

## Migration items spot-checked

| Item (doc / audit) | Check | Result |
|---|---|---|
| M-1 / MI-1, M-2 / MI-2 | permission maps and `--update` replay above | hold, except the sentence of QA-T875-01; own file in `.opencode/agents/` deleted, as stated |
| M-3 / MI-3 | `implementation/PREREQUISITES.md:66` | "1.0.224 up to the latest 1.x; tested on 1.19.2; 2.x is not supported". Holds |
| M-4 / MI-5 | `servers.yaml:143` Brave 2.1.5 with `--transport stdio`, `:241` filesystem 2.4.0; `PREREQUISITES.md:4` Node 22.23.5 / 24.22.3 / 26.13.1; Install section's Node ≥ 24 note for `filesystem` | hold. The doc does not claim Node 22 runs `filesystem` (TL-T869-01). This host has Node v24.19.0, below 24.22.3; nothing warned, as stated |
| M-5 / MI-6 | `scripts/install.sh:938`, `:988` carry `-a --checksum`, comment at `:907` | holds. Not reproduced at equal size here; the suite covers it |
| M-6 / MI-7 | `build` with remote `https://gitlab.com/Acme/Widget.git`: `acme/widget` exit 0; `acme/other` **exit 2** (`is not the id the server derives from the git remote 'origin'`); `Acme/Widget` exit 2; no `origin` remote exit 2 (`cannot be checked`). Install note `:1759-1760` | holds. **QA-T818-03 fixed** (v11 accepted `acme/other`) |
| M-7 / MI-8 | not run by hand; the suite's `context-retriever` tests cover it | (suite only) |
| M-8 / MI-4 | `_manifest.schema.json:51` `tools` enum `["array", "permission", "string"]`; `opencode.json` holds the five new `permission*` keys | holds |
| M-9 / MI-9 | `.gitlab-ci.yml:25` `ci_images_reviewed_on: 2026-11-19` (120 days: fails from 2027-03-20, as K-41 says); `opentelemetry-api==1.45.2` in `ci/requirements-ci.txt:423` and both runtime locks `:244`; release scripts unchanged | holds |
| Install notices | `scripts/install.sh:187`, `:192`, `:196`, `:1313`, `:1317`, `:1339`, `:1363` | each holds what the Migration Guide says |

## Findings

Severity scale: `Critical | High | Medium | Low`.

| ID | Severity | Where | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| QA-T875-01 | Low | `docs/releases/v12.0.0.md` M-1 first bullet ("These keys are never written as an allow, so an agent that holds the tool keeps Opencode's default for it"); `docs/artifacts/release-next-audit-v1.md` B-2; `docs/wiki/mcp-servers.md:121` | **`edit` is written as an allow.** The generator writes `edit: allow` for every agent whose source holds `edit` (20 of 28), through `permissionKeys: ["edit"]` (`implementation/platforms/opencode.json:17`). Only `bash`, `webfetch`, `websearch` and `task` are never allows. The effect equals Opencode's default `edit` allow, but by `AGENTS.md` (an agent's own allow comes after the user's global config) a user's global `edit: ask` or `deny` would be overridden for those 20 agents, which M-1's "keeps Opencode's default" and the wiki's "your own global rules apply to it" do not say. Whether v11.0.0's `tools: edit: true` had the same effect was not checked | `.opencode/agents/tech-lead.md` and 19 others: `edit: allow` first in the map; the wiki itself says "(for `edit` it keeps `edit: allow`)" in the same sentence | Release document: "`bash`, `webfetch`, `websearch` and `task` are never written as an allow; `edit` is written as `edit: allow` for an agent that holds it, which comes after a global `edit` rule of yours". T877 to say whether the override of a user's global `edit` rule needs a K item |
| QA-T875-02 | Low | `docs/releases/v12.0.0.md` § Migration Guide, "What a target does not receive" | **The install does write `docs/wiki/`.** The paragraph says "The install writes no `scripts/`, `docs/releases/`, `docs/wiki/`, ...". A fresh `--platform all` target holds `docs/wiki/README.md` and `docs/wiki/home.md` (the project-wiki templates; v11.0.0 wrote the same two files). It does not hold this repository's wiki pages such as `docs/wiki/mcp-pin-bump-checklist.md`, which is what the sentence means. Also, M-3 and M-4 cite `implementation/PREREQUISITES.md`, which a target does not receive, and the paragraph's closing sentence names only `scripts/`, `docs/releases/` and `docs/wiki/` paths as living in the emage.code repository | fresh target: `docs/wiki/README.md`, `docs/wiki/home.md` present; `implementation/PREREQUISITES.md` absent; v11 target commit lists the same two wiki files | Say "writes no `scripts/`, `docs/releases/`, `.gitlab-ci.yml` or `CONTRIBUTING.md`, and of `docs/wiki/` only the two project-wiki templates `README.md` and `home.md`", and add `implementation/PREREQUISITES.md` to the paths that are in the emage.code repository |

Observations, not findings: the stale local tag `v11.0.0-gate.1` in this clone (deleted on `origin`) would be counted by a local run of the drift script without a tag prune; CI clones fresh. `.mcp.json` and its sidecar are top-level files besides "the platform trees" in the observed-target sentence; harmless.

## Conditions

- **C1 (QA-T875-01): owner `release-manager`** for the M-1 wording (and the audit's B-2 restatement in the document); **`security-engineer` (T877)** to say whether the `edit: allow` override of a user's global rule needs a Known Issue; the wiki line goes to the register through the orchestrator, owner `technical-writer`. Deadline: before T878 issues the verdict.
- **C2 (QA-T875-02): owner `release-manager`.** Fix the "What a target does not receive" paragraph as in the Fix column, then re-run `verify-release-docs.py`. Deadline: before T878.
- **C3 (QA-T818-04, K-32, carried over): owner `orchestrator`, with the user's action.** The probe tag `v12.0.0-gate.1` is deleted and `git ls-remote --tags origin` shows no `gate` ref before `v12.0.0` is pushed; merge `release/v12.0.0` to develop, then to main, before the tag; after the tag, `check-main-develop-drift.py` expects `releases_behind=0` and the `CHANGELOG.md` artifact says "Commits since v11.0.0". Deadline: the v12.0.0 tag push (T879).

## Acceptance criteria (plan-182 § Task Decomposition item 8)

| Criterion | Evidence | Status |
|---|---|---|
| Full suite | § Gates: 2820 OK (skipped=13), difference to 2833 / 25 explained | PASS |
| Golden suite and scorecard | 173 golden contract tests OK; scorecard `--check` OK, 34 cases, 0 regressions; held-out isolation OK | PASS |
| `verify-release-docs.py` | only the 16 pending verdict values | PASS (until T878) |
| `check-version-consistency.py` | PASS, v12.0.0 | PASS |
| `check-main-develop-drift.py` | PASS, vacuous for v12.0.0 | PASS with C3 |
| Fresh install and `--update` on a throwaway target, including the Opencode permission maps | § Install and upgrade replay | PASS (with C1 for the wording) |

## Unverified or not run

- The probe tag's pipeline and the hardened release-gate runner (watched separately by the orchestrator; K-36), the `release` job, `check-release-tag-tree.py` on a real tag.
- Every live client and MCP server: no Opencode session was started, so how 1.19.2 or 1.0.224 applies the maps at call time stays with K-20; whether `filesystem` 2.4.0 runs on Node 22 (M-4).
- M-7 by hand; the network steps of the Migration Guide (`git clone`, `git fetch --tags && git checkout v12.0.0`).
- Windows, macOS, a host without `rsync`.
