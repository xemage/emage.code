# plan-151 — `context-retriever`: the code behind QA-T760-01 to -03 (batch Z)

**Created:** 2026-11-12
**Based on:** `docs/artifacts/qa-release-v10-v1.md` (QA-T760-01, -02, -03 and condition C1); `docs/artifacts/tracked-debt-register-v13.md` (§ 5 batch Z and "Order" item 1; § 6.2 item 36); `docs/releases/v10.0.0.md` (M-2, K-35). The user's instruction of 2026-11-12, verbatim: "Continue with the next best step". The orchestrator reads it as the word for the first item of the register's suggested order, batch Z, which QA binds to the next release. It is not read as approval of a release, a tag or a root refresh.
**Scopes:** `T790`, `T791`, `T792`.

## Goal

Three ids are open at QA's `Medium`. v10.0.0 fixed their release-document part; the code behind them is unchanged (read here on `4cdf64ac`):

- **QA-T760-01.** The installer's printed note names only `requirements-mcp-server.txt` (`scripts/install.sh:1756-1767`). The index build that the next note asks for needs `implementation/runtime/memory/requirements.txt`, which no printed line names (only the comment at `:1769-1774` does). With the printed command alone the build exits 1 with `ModuleNotFoundError: No module named 'yaml'`.
- **QA-T760-02.** `build.py` takes any `--project-id` (`implementation/runtime/memory/build.py:173`, `:194`). The server derives its own id in lower case (`context_retriever.py:105`), and the query-time filter compares exactly (`scope_filter.py:52`). A build with `Acme/Widget` succeeds, the server starts, and `retrieve` returns nothing, with no error.
- **QA-T760-03.** `servers.yaml:194` passes `--platform-root .claude` on every platform. The generated Cline and Opencode entries carry it (`implementation/.cline/mcp.json`, `implementation/.opencode/opencode.json`). On an install without `.claude/`, `resolve_platform` raises and `retrieve` fails at the first query. Each of the three platform folders that gets this server holds its own `.generated-manifest.json` with its own `platform` value (`.claude`: `claude-code`, `.cline`: `cline`, `.opencode`: `opencode`; read here).

## Task Decomposition

1. **T790** (backend-developer), in worktree `../worktrees/agent-backend-developer-T790`, branch `agent/backend-developer/T790`:
   - **QA-T760-01:** the printed dependency note also gives the install line for `implementation/runtime/memory/requirements.txt` when the target holds `implementation/runtime/memory`, so that the two printed notes, followed in order, give a build that runs. Paths stay shell-quoted (`%q`, SEC-009). The installer still installs nothing itself.
   - **QA-T760-02:** `build.py` refuses a `--project-id` that is not already in the form the server derives (lower case, `<org>/<repo>`), with a non-zero exit and a message that names the expected form. It rejects; it does not silently rewrite (`security-guidelines.md` § Input Validation). **`scope_filter.py` does not change**: the exact compare is the access control. Report what the build does today with a project-scope entry whose `project_id` differs from `--project-id` only by case; if the entry is dropped without a word, make the build say so on stderr with the file path only (no content), and keep it dropped.
   - **QA-T760-03:** each generated `context-retriever` entry passes its own platform's folder as `--platform-root` (`.claude`, `.cline`, `.opencode`). The Claude Code output stays byte-identical. The source is `implementation/knowledge/mcp/servers.yaml` and `implementation/scripts/sync.mjs`; regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`. Update the `servers.yaml` comment at `:185-187`.
   - Tests for each of the three, including a negative case each (the mixed-case id is refused; a platform folder without a manifest still fails closed).
   - The top-level folders (`.mcp.json`, `.cline/`, `.opencode/`, `.claude/`) are **not** edited. Declare the resulting root drift the way earlier tasks did (`tests/functional/test_root_install_parity.py`, `--print-drift`), and list the paths in the report.
   - Text that states the old limits and ships to targets (`implementation/runtime/memory/README.md`, `implementation/PREREQUISITES.md`, `docs/wiki/mcp-servers.md`, `AGENTS.md` sources) is corrected where it would now be false. `docs/releases/v10.0.0.md` is a published record and does not change.
   - *Acceptance:* the three reproductions of `qa-release-v10-v1.md` no longer fail the way QA recorded; `sync.mjs --check` and `generate-registry.py --check` pass; the full suite passes; no top-level platform folder and no file under `tests/golden/` changes.
2. **T791** (security-engineer), read-only: review T790's diff. Points: the scope filter is untouched and still fails closed; the refusal cannot be bypassed into a mixed-case index; `--platform-root` per platform cannot make one platform resolve as another; the printed note cannot run a name in a path. Verdict and final status of the three ids on the `SECURITY:*` scale where a point is a security point.
3. **T792** (qa-engineer): re-run QA's three reproductions against T790's tip in temporary directories, and record observed results. No `docker`. Writes only its report; the orchestrator commits it as `docs/artifacts/qa-recheck-t792-context-retriever-v1.md`.
4. **The orchestrator:** gates and the full suite in a clean worktree; the MR and its pipeline; commits the review artifacts; closes the tasks; merges on green, pinned to the verified sha. The ids' new status goes into register v14 through this plan's Outcome. **The root refresh that the drift then needs is a separate step and needs the user's approval at that moment.**

## Constraints

- No `docker` command. Never open `tests/golden/held-out/`; recursive searches over `tests/` exclude it. Read no `.env*` or credential file, and not the user's `.claude/settings*.json` or `.vscode/*.json`.
- Derived folders are generated, never hand-edited. Top-level platform folders are not touched in this plan.
- Functions stay at 50 lines and 4 parameters at most. Conventional Commits.
- Subagents never merge, tag or release.
- Token budget: T790 120k, T791 and T792 60k each.

## Outcome (2026-11-12)

- **T790 is done** (commits `c757e409`, `f5c1fba7`, `69889ce3`, `ab6412e7`, `cf7366b7`):
  - **QA-T760-01:** `scripts/install.sh` `print_memory_index_notice` prints the install line for `implementation/runtime/memory/requirements.txt` before the build command (`%q`; nothing installed).
  - **QA-T760-02:** `build.py` refuses a `--project-id` that is not the derived lower-case `<org>/<repo>` (CLI exit 2; `BuildConfig` raises `ValueError`); `scope_filter.py` is unchanged. The build already indexed a project-scope entry whose `project_id` differs only by case (never returned); it now names it on stderr, path only.
  - **QA-T760-03:** `servers.yaml` passes `--platform-root {{platformDir}}`, which `sync.mjs` writes as each platform's `outputDir` (`.claude`, `.cline`, `.opencode`) after validating it; `implementation/.mcp.json` is byte-identical.
  - Root drift declared: `.cline/mcp.json`, `.opencode/opencode.json`.
- **T791 is done: PASS** (`docs/artifacts/security-review-t791-context-retriever-v1.md`). New LOWs for register v14: **SEC-T791-01** (the platform identity change goes into the v11.0.0 migration notes, before the tag; batch Q), **SEC-T791-02** (project-scope entries naming another project are dropped without a message), **SEC-T791-03** (`is_derived_project_id` not total over non-strings; dot segments).
- **T792 is done: PASS** (`docs/artifacts/qa-recheck-t792-context-retriever-v1.md`). All three reproductions fixed on Cline and Opencode, and each negative check brings back the old failure without the fix. New: **QA-T792-1** (Low, QA scale): each printed install line activates `.venv-mcp` in its own shell, and the printed build command does not.
- **For register v14:** QA-T760-01, -02 and -03 fixed (batch Z empties); SEC-T791-01 to -03 and QA-T792-1 tracked-LOW.
- **The orchestrator's checks:** `sync.mjs --check`, `generate-registry.py --check`, `scorecard.py --check`, the ledger validator and `test_link_integrity` pass; the full suite in a clean worktree at `a4552400` ran 2719 tests, OK (skipped=24); MR !670 pipelines on `a4552400` green. The skip count differs from the 25 of earlier runs because `test_every_active_task_has_a_plan` skips only when the active queue is empty, and it held T790 to T792 here (checked by running that test in both checkouts).
- **Open:** the root refresh of the two declared paths needs the user's approval at that moment.
- **Root refresh done (T793)**, with the user's approval of 2026-11-12, verbatim: "refresh". Only the two declared files changed; `--print-drift` gives `[]`; the drift baseline is empty.
