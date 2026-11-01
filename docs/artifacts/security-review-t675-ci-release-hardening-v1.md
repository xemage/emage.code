# Artifact: security-review-t675-ci-release-hardening-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test, mutation harness, pipeline or `pip-audit` run; the files were read at the worktree tip, not as commit diffs; the digests were fetched from the Docker Hub registry API through a summarising fetch tool). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-16.
- **Target**: T675, commits `992f5f7` and `2273138` (reviewed) and `aa0371e` (the review's cheap findings) on `agent/devops-engineer/T675` (from develop `91d899f`): CI and release tooling hardening and the `security-audit` MCP server.
- **Based on**: `docs/tasks/task-T675.md`, `docs/plans/plan-123-post-release-follow-ups.md`, `docs/artifacts/tracked-debt-register-v1.md` (20 ids), `security-review-t635-*`, `-t640-*`, `-t619-*`, `-release-v8-v2.md`, `code-review-release-v8-v1.md`.
- **Orchestrator checks**: the developer reports 1375 tests OK (skipped 23; with `CI=true` the audit-server, publish-release and verify-release-docs modules, 167 tests, pass with 1 skip) and all gates after the last commit, and a mutation harness of 46 single mutations of which 44 are killed (the 2 survivors are equivalent guards: the dry-run `os.environ` assignment placement and the redundant `/` anchor rule, which `$HOME` ancestry also covers).

## Verdict: PASS

0 critical, 0 high, 0 medium, 10 LOW (SEC-T675-01..10). No Immutable Security Constraint is breached; no required control is omitted or weakened. All 20 register ids in scope are fixed or reduced to documented residuals: SEC-T635-01..04, SEC-T640-01..04, SEC-T619-05, SEC-003 (argv part; the token in the job environment, its reuse and the D-4 statement remain), SEC-015 (except the leading-dash `--target` in `install.sh`, re-homed to T672), SEC-T650-04, TL-T649-14, SEC-T650-05, TL-T649-05, -07, K-12, TL-T649-12 (after the follow-up), TL-T649-13 and QA-T648-03 (documented and visible as a NOTE, not enforced; an ancestor check of `$CI_COMMIT_SHA` against `origin/main` is the real fix, tracked).

## What the review verified

- The 3 pinned index digests (`node:20-alpine`, `python:3.12-alpine`, `alpine:3.20`) equal the digests Docker Hub serves for the tags; the `apk add` packages resolve on their Alpine branches; `~=` is accepted by apk (a character-set operator; the documented fuzzy operator is `~`; the pipeline going green is the proof).
- `publish-release.py`: `--token-env` with `ENV_NAME_RE`, the `--token` warning, the both-flags error, control characters in the token refused (header injection); `validate_api_target` as a URL parse; `--expected-host` pinned to `CI_SERVER_HOST`; the redirect-refusing opener applies to every request including the GET existence check and to 301/302/303/307/308; read-time errors become `ReleasePublishError`; symlink and decode guards in `load_release_brief`; tags filtered through `TAG_RE`; subjects stripped of control characters; changelog placement.
- `security-audit` server: ripgrep appends `--iglob` after `--glob`, so the deny globs win regardless of the caller's glob; the four-tool surface, fixed argv, `shell=False` and the single `subprocess.run` site are unchanged; the new roots are launch-time options only.

## Findings and dispositions

| ID | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T675-01 | LOW | The `.env*` deny was narrower than the intent: a `root_dir` inside a `.envs/` directory, `*.env`, `credentials.json`, `*.pem`, `*.key`, `id_rsa`, `secrets.yaml` and `.git/config` were reachable | Fixed in `aa0371e`: path components `.env*`, `*.env`, `*.pem`, `*.key`, `id_rsa*`, `id_ed25519*`, `credentials.json`, `secrets.y*ml` and `.git` refused case-blind for `root_dir`, its ancestors up to the matched root and the matched path, for all four tools; rg globs generated from the same list; `.env.example` stays blocked |
| SEC-T675-02 | LOW | Roots from `--allow-git-worktrees` were not filtered like explicit roots (`/` and ancestors) | Fixed in `aa0371e`: `root_is_too_broad` refuses `/`, `$HOME`, its ancestors and strict ancestors of the allowed root for every root source; server-level tests |
| SEC-T675-03 | LOW | The digests freeze two end-of-life bases (`alpine:3.20` serves `wiki-sync`, which holds `WIKI_TOKEN`, and `release-docs-gate`; `node:20-alpine` is the default image of five jobs) | Tracked debt (T676 area). Proposal: move the default to `node:22-alpine` or `node:24-alpine`, move `wiki-sync` and `release-docs-gate` to the Alpine 3.24 line of the python image, re-read the digests and `~=` pins together, green pipeline first (Node 22/24 may change `sync.mjs` behaviour) |
| SEC-T675-04 | LOW | CI skipped the tests that prove the new controls (ripgrep and `mcp` were not installed in `unit-tests`) | Fixed in `aa0371e`: `'ripgrep~=15.1'` and `"mcp==2.2.0"` installed in the job; with `CI` set those tests fail instead of skipping; the apk pin test parses every token of every `apk add` and requires `--no-cache`. Unverified until the first pipeline: the install on musl/Alpine 3.24 |
| SEC-T675-05 | LOW | An empty `--expected-host` silently turned the host pin off | Fixed in `aa0371e`: empty or whitespace is an error; with `CI` set the host is required |
| SEC-T675-06 | LOW | The placeholder gate could be skipped silently (heading variant, stray fence) and missed `TBD`/empty values; `FIELD_RE` backtracked | Fixed in `aa0371e`: a heading present but not found as a section is an error; linear `FIELD_RE`; new markers; all 34 published release documents still pass |
| SEC-T675-07 | LOW | The dry run's "refuse network" guard no longer covered the real request path (`OPENER.open`) | Fixed in `aa0371e`: `module.OPENER` replaced by an object that raises; token variable set inside the `try` |
| SEC-T675-08 | LOW | Several controls pinned only by redundant checks or untested (symlink to a sibling file, a bare `?`/`#`, redirects other than 302, the worktree wiring) | Partly fixed in `aa0371e` (worktree and env wiring, the case-sensitive component match); the rest tracked (T673) |
| SEC-T675-09 | LOW | Floating PyPI packages in the job that binds the host Docker socket | Tracked debt (T676). Proposal: `ci/requirements-ci.txt` hash-pinned (`pip-compile --generate-hashes`), `pip install --require-hashes -r`, and a test that every `pip install` line uses `-r` |
| SEC-T675-10 | LOW | Residual nits in the release script | Mostly fixed in `aa0371e` (404 matched on the status code, git/apk run without the token variable, non-UTF-8 `CHANGELOG.md`, `.`/`..` segments refused); tracked: Markdown escaping of subjects beyond control characters, bidi/C1 stripping |

## Conditions and follow-ups

- Record the remaining items (SEC-T675-03, -08 remainder, -09, -10 remainder, the ancestor check of TL-T649-13, the leading-dash `--target` in `install.sh` re-homed to T672, the `WIKI_TOKEN` reuse question: evaluate `CI_JOB_TOKEN` or a dedicated minimal-scope token) in the tracked-debt register at its next version (owner devops-engineer).
- The first tag pipeline is the first real run of the new release-job code path (`--token-env`, `--expected-host`, the pinned images); `WIKI_TOKEN` must be set as before.

## Limits

L-1 no shell (no test, mutation harness, pipeline, `pip-audit`); L-2 the commit diffs were not available to the reviewer; L-3 `grep_content` could not read the worktree (outside its allowed root, which is SEC-T650-05 itself); L-4 the rg depth-0 and `.envs` points rest on the ignore crate's semantics and were not run by the reviewer (the developer ran real rg); L-5 `docs/wiki/*`, `implementation/SECURITY.md`, `servers.yaml` and the knowledge text were not read; L-6 the user's local settings files and `tests/golden/held-out/` were not opened.
