# Artifact: qa-gate-release-v8-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Executor**: qa-engineer (runs in detached scratch worktrees; the release worktree was unchanged). Recorded by the orchestrator from the executor's report.
- **Gate**: integration (T648). **Date**: 2026-10-15.
- **Target**: `release/v8.0.0` at `57d0107d437110d12a2d3cf46cf19597bed913e1` (develop `34ab1c0` + T644 version markers + T645 release document). The later commits (the T645 amendment and what follows) were not re-run by QA; the orchestrator re-runs the gates named in the T652 checklist on the final tree.
- **Based on**: `docs/tasks/task-T648.md`, `docs/plans/plan-122-release-v8-wave-3.md`, `docs/releases/v8.0.0.md`, `docs/artifacts/release-v8-audit-v2.md`.

## Verdict: CONDITIONAL_PASS

No critical or major finding; every executable gate is green; four minor findings. QA does not cover the two open SECURITY:MEDIUM findings (SEC-T658-01, SEC-T657-02): they are a T650/T651 matter.

## Results

| Check | Result |
|---|---|
| Full suite (`python3 tests/run.py`) | 1267 tests, OK (skipped 23), exit 0; the 23 skip reasons were not enumerated (unverified) |
| Held-out isolation | 8 tests OK |
| Scorecard (`scorecard.py --check`) | OK: 34 cases, 28 pass, 0 regressions; 6 `known_failing` (2 `tracked_defect`, 4 `capability_gap`), 0 `unexpected_pass` |
| `verify-release-docs.py --tag v8.0.0` | all checks passed, marker verified |
| `check-version-consistency.py` | PASS (v8.0.0) |
| `check-maturity.py` | 80 components, 0 failing (agents 27 stable + 1 experimental, commands 14 + 5, instructions 4 + 2, skills 7 + 20) |
| `sync.mjs --check`, `generate-registry.py --check`, `validate-tasks.py` | no drift across 584 files; registry up to date; PASS (7 active, 450 completed) |
| Evaluator hash | no drift against v21 (computed from commit `cc0b411`) |
| `dry-run-publish-release.py --tag v8.0.0` (+ `--template-shaped`) | DRY RUN OK; description equals the document byte for byte; no root `release-notes.md` |
| `check-main-develop-drift.py` (offline) | PASS but vacuous (main v7.0.1, develop v7.0.1); pre-tag runs on the release refs FAIL by design ("marker version v8.0.0 is not a known git tag"); with `v8.0.0` added in memory to the pure `evaluate()` function: main=develop=v8.0.0 passes, main=v7.0.1 with develop=v8.0.0 passes at 1 behind (inside the one-release grace window), so the gate cannot catch a forgotten main merge for one release |

## Clean install and migration

- Plain install (`--platform all`: 638 files; `--platform claude-code`: 138 files) exit 0; `--update` exit 0 and idempotent (sha256 listing identical); `--projections-only` on an rsync copy of the repo root exit 0, no file changed (root drift 0); `--update` or a plain install at the repo root and any `--target` inside the repo refused with exit 1. No stray files except the 7 provenance sidecars. The 7 generated MCP configs carry no `fetch`/`docker`/`postgresql`; the `playwright` entry is identical in all 7; Gemini `excludeTools` and Opencode `permission` hold exactly the six denied tools; `.vscode/mcp.json` has 7 servers and no `security-audit`/`poc-security-audit` (K-3).
- Migration replay (v7.0.1 `git archive` installed, then `--update` with this tree) on a scratch target with user files: M-1 (a hand-written `.claude` file deleted, `settings.json`, `workflows/` and `CODEOWNERS` untouched, new runtime files and skill appear, ledger rewrite rules, symlink refusals), M-4, M-8 with sidecar (fetch/docker/postgresql removed, user `env`, `myserver`, `playwright-local` kept, Gemini `excludeTools` unioned, Opencode `permission.bash=ask` kept with the six denies last), M-8 without sidecar (the three servers stay; the combined `--force-prune-keys docker,postgresql,fetch` refuses with exit 1 and writes nothing; per-name forms remove all three where present), M-9 (`npm view` returns E404 for the four launchers; `@anthropic/mcp-filesystem` in every tag v5.0.0 to v7.0.1), pins resolve, Rollback Plan replay matches the document.
- 12 Known-issues statements spot-checked against the repository: all hold (K-1, K-2, K-3, K-5, K-6, K-12, K-13, K-15, K-16, counts 28/19/27, Features 13 / Fixes 24 / Breaking 20, cited artifacts exist).

## Findings

| ID | Severity | Where | Finding | Disposition |
|---|---|---|---|---|
| QA-T648-01 | minor | `docs/releases/v8.0.0.md` M-8 | `--force-prune-keys` "once per file and once per name": on the Copilot `.vscode/mcp.json` the `docker` and `postgresql` calls exit 1 (name not present) and look like a failure | Condition C1: fixed by the T645 amendment (666f36f) |
| QA-T648-02 | minor | M-8 / install notices | `install.sh` prints neither the Playwright browser step nor the `.playwright-mcp/` advice | Fixed by the T645 amendment (text states it); tracked: print it in a later release |
| QA-T648-03 | minor | `scripts/check-main-develop-drift.py` | The offline run is vacuous and the one-release grace hides a missed `main` merge | Condition C2: the T652 procedure does the merges in the B1 order and checks the tag pipeline's gate output |
| QA-T648-04 | minor | M-9 | "confirmed in the tagged `servers.yaml` and `.mcp.json`": the root `.mcp.json` carries the package only from v6.4.1 (`implementation/.mcp.json` from v6.4.0) | Fixed by the T645 amendment |

## Unverified or not run

Chrome for Testing revision and size and any live launch of the `playwright` server or `--sandbox`; the Copilot/Opencode/Gemini/Pi behaviour in a live client (K-20); the `github` image digest pull, `uvx mcp-server-git` start and the venv `pip install`; the `@anthropic` scope ownership; the GitLab API half of the release job and the description size limit; the D-4 settings; the skip reasons of the 23 skipped tests; Windows and Cline's global MCP file.
