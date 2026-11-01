# Artifact: qa-gate-release-v9-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Executor**: qa-engineer, worktree `agent/qa-engineer/T707`. Scratch install targets and a detached `v8.0.0` worktree were used and then removed. Only this artifact was written to the repository.
- **Gate**: integration (T707). **Date**: 2026-11-01.
- **Target**: `release/v9.0.0` at `ca11bb6ea7eadb76a251d46c18e8fe949b1c7936`. QA did not re-run later commits. The release manager or the orchestrator re-runs the gates on the final tree.
- **Based on**: `docs/tasks/task-T707.md`, `docs/plans/plan-124-release-v9.md`, `docs/releases/v9.0.0.md` (Migration Guide M-1 to M-12), format model `docs/artifacts/qa-gate-release-v8-v1.md`.
- **Credentials**: every installer and suite run had `GITLAB_PERSONAL_ACCESS_TOKEN`, `GITLAB_TOKEN`, `GITLAB_PERSONAL_ACCESS_TOKEN_FILE`, `BRAVE_API_KEY`, `WIKI_TOKEN`, `GITHUB_PERSONAL_ACCESS_TOKEN` and `CWSO_JWT_SECRET` unset. No server was launched.

## Gate Verdict

- **Gate:** integration
- **Verdict:** CONDITIONAL_PASS

There is no critical or major finding, and every executable gate is green. Two findings are minor and one is a minor carry-over (C1 to C3 below). This gate does not cover security findings: they are a T708 matter.

## Results

| Check | Result |
|---|---|
| Full suite (`python3 tests/run.py`) | `Ran 2207 tests in 876.084s`, `OK (skipped=25)`, exit 0. The 25 skip reasons were not enumerated **(unverified)**. Some of them are the T223 CWSO functional tests, which skip because CWSO was not reachable on localhost (their number was not counted). |
| Held-out isolation (`tests.functional.test_golden_held_out_isolation`) | 8 tests OK |
| Golden contract tests (`test_golden_harness_*`, `test_golden_suite_format`, `test_golden_held_out_isolation`, `test_scorecard_artifact_no_drift`) | 173 tests OK |
| Scorecard (`scorecard.py --check`) | OK: 34 cases, 30 pass, 0 regressions, wrote nothing |
| Evaluator hash | NO DRIFT against `evaluator-hash-known-good-v22.json` (commit `0727329a`) |
| `verify-release-docs.py --tag v9.0.0` | exit 1 with 19 errors, all `unfilled verdict` placeholders: 10 under `## Gate Verdicts` (Architecture, Implementation, Integration, Security and Release, each with `<PASS/CONDITIONAL_PASS>` and `YYYY-MM-DD`) and 9 under `## RELEASE VERDICT`. There are no other errors. As the brief allows, this is acceptable until T710 fills them. |
| `check-version-consistency.py` | PASS (canonical v9.0.0), exit 0 |
| `check-main-develop-drift.py --develop-ref HEAD` | FAIL, exit 1: "develop marker version v9.0.0 is not a known git tag". This is expected before the tag exists and is acceptable. Without `--develop-ref` (origin refs): PASS, main=develop=v8.0.0. With `v9.0.0` added in memory to the pure `evaluate()`: main=develop=v9.0.0 gives PASS; main=v8.0.0 with develop=v9.0.0 gives PASS with the 1-release grace NOTE (see QA-T707-03). |
| `sync.mjs --check` | OK, no drift across 494 files |
| `generate-registry.py --check` | registry is up to date |
| `check-maturity.py` | 80 components, 0 failing (agents 28 stable; commands 14 + 5; instructions 4 + 2; skills 7 + 20) |
| `validate-tasks.py` | PASS (6 active, 504 completed) |

## Clean install and projections-only

- `install.sh --target <tmp> --platform all`: exit 0, 549 files, no `.cursor/`, 6 provenance sidecars (`.mcp.json`, `.vscode`, `.gemini`, `.opencode`, `.pi`, `.cline`).
- `--projections-only` on the same target: exit 0. A plain re-install: exit 0. The sha256 listings of all files are identical after each of the three runs, so the runs are idempotent.
- The generated `brave` entry runs `-y @brave/brave-search-mcp-server@2.1.4 --transport stdio` in all 6 configs (Opencode as one `command` array). No config has a `github` server. Server counts: `.mcp.json`, Gemini, Opencode and Cline 16; Pi 14 (no `hindsight` or `cwso`); `.vscode/mcp.json` 9 (it now includes `security-audit` and `poc-security-audit`). The Pi placeholders are all `${X}`.
- `--platform cursor` and `--platform cursor --update` exit 1, write nothing (the target directory is not created), and print: "platform 'cursor' was removed in v9.0.0 (see the Cursor migration item in docs/releases/v9.0.0.md; the v8.x releases are the last that support it). Existing .cursor/ files in your project are not touched. Nothing was written." The message points to the item by subject and does not print the label "M-1". QA judges this acceptable (observation, not a finding).

## Migration replay (v8.0.0 install, then v9.0.0 `--update`)

Setup:

- A detached worktree at tag `v8.0.0` (`6630dd0e`). `scripts/install.sh --platform all` from that worktree into a fresh target.
- Before the update, the target held `.cursor/` (with manifest and sidecar), `github` in 6 of 7 MCP configs (not `.vscode`), and Pi `${env:X}` placeholders including `hindsight` and `cwso`.
- User content added before the update:
  - `.cursor/my-own-file.md`
  - `.claude/settings.json`
  - `myserver` and `github-mine` (a copy of `github`) in `.mcp.json`
  - in the Pi `gitlab` env: `MY_EXTRA` and a credential-named literal `MY_API_TOKEN` (a dummy value)
  - a Pi server of the user's own, `mypi`, with a `${env:MYVAR}` argument

The v9.0.0 `install.sh --platform all --update` then exited 0.

| Item | Outcome | Evidence |
|---|---|---|
| M-1 Cursor | **confirmed** | `--update` printed the Cursor warning. It names the `filesystem` entry, the keys `e2b`, `redis`, `figma` and `notion`, the `--force-prune-keys` caveat and "the Cursor migration item". `.cursor/` was byte-identical afterwards (sha256 listing), including the user file, and its `mcp.json` still holds `github` and the old brave args (frozen). `--platform cursor` exits 1 (see above). Rollback: the v8.0.0 installer with `--update` recreated `.cursor/`, deleted `my-own-file.md`, and re-added `github` while keeping `github-mine` and `myserver`, as documented. Two parts were not re-run: the plain install without `--update` that prints nothing, and the `--force-prune-keys` behaviour with the v8 Cursor source (the document marks it (not re-run)). |
| M-2 `github` removed | **confirmed** | Notes "pruned the retired generator server github" for `.mcp.json`, Gemini, Opencode, Pi and Cline, through the sidecars. `github-mine` and `myserver` were kept. Without a sidecar (clean target, sidecar deleted, `github` re-added, plain install): the note text from M-3 appeared and `github` was kept. `merge-mcp-json.py --force-prune-keys github` removed it (exit 0). A second run, with the name absent, exited 1. Opencode also printed a misleading "differs" note (QA-T707-01). |
| M-3 plain install merges, refusals | **confirmed** | A plain install merged and printed the sidecar-less note word for word. An invalid `.cline/mcp.json` stopped the run with exit 1 and wrote nothing (sha256 listing unchanged). A leftover `.claude.emage-old.12345` stopped `--update` with "a previous update of this target was interrupted" and a `mv` restore line. `--target -x` was refused with the `./-x` hint. `--dry-run` created no target (the document says (not re-run); QA re-ran it). The `.tmp`, `.bak` and tree-swap names were not observed: not testable without an interrupted run. |
| M-4 Pi | **confirmed** | Pruned `cwso`, `github` and `hindsight`. The generated placeholders became `${X}`. `GITLAB_PERSONAL_ACCESS_TOKEN` was dropped with the "dropped the retired `${env:` entry" note, and there is no `..._FILE` key in the Pi entry. `MY_EXTRA` and `MY_API_TOKEN` were kept, with the note and the WARNING "holds a literal value; remove it from the file and revoke the token" (name only, no value). The user's own `${env:MYVAR}` in `mypi` was kept silently (QA-T707-02). |
| M-5 GitLab entry | **confirmed** (config content) | `GITLAB_PERMISSION_MODE=modify` and `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` in `.mcp.json`, Gemini, `.vscode`, Cline and Opencode. Claude Code uses `${VAR:-}` and Gemini `${VAR}`. Not testable: the server's refusal behaviour, `check-gitlab-token.py` against a live token, and the Claude Code re-approval prompt. |
| M-6 GitLab grants | **confirmed** (tool lists) | The Claude Code agent files have scrum-master 24, qa-engineer 19, release-manager 17, orchestrator 16, devops-engineer 11, poc-orchestrator 8 and poc-devops-engineer 6 named `mcp__gitlab__*` tools. No list has a merge, approve, push, file-write, delete, branch, tag, release, retry, cancel, trigger, variable, job-output or raw-API tool. `create_merge_request` appears only in orchestrator, poc-orchestrator and release-manager. Live enforcement is not testable here. |
| M-7 Opencode per-agent denies | **confirmed** (files) | All 28 `.opencode/agents/*.md` have the six unsafe Playwright tools `false`, and `filesystem_*`, `git_*` and `supabase_*` `false`. Each file has 10 `<server>_*: false` wildcards, except orchestrator and poc-orchestrator (8) and solution-architect (9), which hold whole servers. No agent has a `false` for the exempt servers (brave, context7, hindsight, cwso, hf-mcp-server, toolradar). The global `permission` holds the six denies, and Gemini `excludeTools` holds the same six. Runtime behaviour in Opencode was not observed **(unverified)**. |
| M-8 Copilot security servers | **confirmed** | `.vscode/mcp.json` gained `security-audit` (`python3 -m implementation.runtime.security.audit_server`) and `poc-security-audit` (`... poc_audit_server --allowed-root .`), each with `"cwd": "${workspaceFolder}"` and no env. As documented, the installer output does not mention them (0 matches). Not testable: Workspace Trust, the tool-approval prompts, and the `mcp==2.2.0` start. |
| M-9 release gate input | **confirmed** (text) | `implementation/knowledge/agents/release-manager.md` item 5, "Independent check of what you authored", and the Gate Inputs row "Release document, independent check (commit: [sha])" are present. Its application is T710's matter. |
| M-10 behaviour changes | **confirmed** | The shipped `playwright` entry blocks 39 origins. Both `requirements-mcp-server.lock.txt` files exist, and both plain files carry `httpx2>=2.12.0`. `TECHNICAL-DEBT.md` placement is in `poc-guidelines`. 28 agents are stable (`check-maturity.py`). The security-audit path refusals are covered by `tests/functional/test_audit_server.py` in the passing suite. The `monkey.key` example was not re-run on its own **(unverified)**. |
| M-11 maintainers | **confirmed** (code reading) | `.gitlab-ci.yml` runs `check-release-tag-tree.py --tag "${CI_COMMIT_TAG}" --main-ref origin/main`. `publish-release.py` documents `--token-env` and the deprecation warning for `--token`. `verify-release-docs.py` carries the Cursor-item rule. `check-version-consistency.py` excludes `docs/decisions/` (T704). `scripts/audit-mcp-pins.py` and `docs/wiki/mcp-pin-bump-checklist.md` exist. `mint-cwso-jwt.py` has no default secret file. The `supportedPlatforms` enum in `package.schema.json` is the six platforms without `cursor`. `sync.mjs` throws `Unknown MCP format`. Not testable: the tag pipeline itself and `CI_JOB_TOKEN` permissions (K-26). |
| M-12 Brave stdio | **confirmed** (config) | After the update, all 6 maintained configs launch brave with `--transport stdio`, and the frozen `.cursor/mcp.json` does not, as M-1 states. The flag-overrides-environment behaviour was observed by the user (UA-T712-1) and was not re-run by QA. |

## Findings

| ID | Severity | Where | Finding | Disposition |
|---|---|---|---|---|
| QA-T707-01 | minor | `scripts/merge-mcp-json.py:112-128` (`GENERATED_REF`, `differs_from_generated`) | When `--update` prunes an **unedited** retired generator entry from `.opencode/opencode.json` (for example v8.0.0's `github`), it also prints "github differs from the generated entry; its old content is not kept (copy the entry to another name and re-add it)". Opencode writes placeholders as `{env:NAME}` without `$`. `GENERATED_REF` matches only `${NAME}` and `${env:NAME}`, so every Opencode `environment` value counts as hand-edited. The prune itself is correct and nothing is lost that M-2 does not already announce, but the note is a false positive. Repro: install v8.0.0 `--platform all` (or `opencode`), then run the v9.0.0 installer with `--update`. | Condition C1: owner backend-developer through the orchestrator. Accept the `{env:NAME}` form in `GENERATED_REF` (with a regression test), or record it as tracked LOW debt. This does not block the release. |
| QA-T707-02 | minor | `docs/releases/v9.0.0.md` M-4 | "every placeholder changes from `${env:X}` to `${X}`" holds for generated entries only. A server of the user's own in `.pi/mcp.json` with `${env:X}` is kept unchanged, with no note, and Pi does not expand it. | Condition C2: owner release-manager (T710 or the release document). Add "in generated entries; convert your own entries by hand". This is a documentation precision fix. |
| QA-T707-03 | minor (carry-over of QA-T648-03) | `scripts/check-main-develop-drift.py` | Before the tag, the run on the release ref fails by design. After the tag, the 1-release grace lets main=v8.0.0 with develop=v9.0.0 PASS, so the gate cannot catch a forgotten merge to main for this release. | Condition C3: owner orchestrator. The release procedure merges `release/v9.0.0` to main and develop before the tag, re-runs the drift check after the tag, and expects `releases_behind=0`. |

Observation (not a finding): the `--platform cursor` error points to "the Cursor migration item" rather than the label "M-1". M-1 says the message "names this item". QA reads that claim as satisfied.

## Conditions

- C1 (QA-T707-01): owner `backend-developer` (assigned through the orchestrator). Mitigation: fix the regex with a test, or list the issue as tracked LOW debt. Deadline: before v9.0.1 or the debt-register refresh.
- C2 (QA-T707-02): owner `release-manager`. Mitigation: one clause in M-4. Deadline: before T710 closes.
- C3 (QA-T707-03): owner `orchestrator`. Mitigation: the drift check after the tag must show `releases_behind=0`. Deadline: the tag pipeline of v9.0.0.

## Unverified or not run

- The 25 skip reasons of the suite.
- Every live client behaviour (Opencode denies, Copilot Workspace Trust, the Claude Code re-approval).
- The GitLab server's refusal in `modify` mode and `check-gitlab-token.py` against a real token.
- The Brave transport behaviour (user-observed, not re-run).
- The tag pipeline, `check-release-tag-tree.py` on a real tag, and the `CI_JOB_TOKEN` release job.
- `--force-prune-keys` with the v8 Cursor source.
- A plain install (without `--update`) over a v8 `.cursor/`.
- The `.tmp`, `.bak` and `.emage-new` names during an interrupted run.
- The `monkey.key` refusal on its own.
- Windows.
