# T550 — `install.sh --projections-only`: a harness-only refresh mode, v1

**Based on:** `docs/tasks/task-T550.md`; `docs/plans/plan-082-root-refresh-and-followups.md` §1–§2;
`docs/artifacts/root-projection-resolution-v1.md` (T543) §5–§6; `scripts/install.sh` at `e598547`;
`scripts/merge-task-docs.py`; `scripts/merge-mcp-json.py`; `scripts/render_installed_agents.py`;
`tests/functional/test_root_install_parity.py`; `tests/functional/test_install_script.py`;
`.gitlab-ci.yml` (`unit-tests`); `docs/decisions/ADR-002-mcp-merge-provenance-tracking.md`.
**Author:** DevOps Engineer. **Date:** 2026-09-30. **Tree measured:** `develop` at `e598547` (branch
base), and the §4.3 rehearsal repeated at `develop` `b368c71`, which landed during this task.

## 0. Verdict

1. **New flag: `--projections-only`.** It refreshes only the derived harness of an existing
   install: the eight platform trees, the seven MCP configs and their sidecars, `AGENTS.md` and
   `CLAUDE.md`. It never writes or deletes anything under the target's `docs/` or `implementation/`.
   It is opt-in and mutually exclusive with `--update`. It is permitted at the repository root, but
   only with `--platform all`.
2. **Every existing invocation is unchanged in what it writes.** This was measured, not inferred
   (§4.1).
3. **The real repository root was not refreshed.** A full-copy rehearsal predicts that the
   plan-082 §2 refresh changes exactly the declared paths and nothing else (§4.3). That is 55 paths
   at `e598547` and 80 at `b368c71`.
4. **A new destructive defect was found and not fixed.** On a host without `rsync`, `--update` at a
   repository root deletes `implementation/runtime/memory/` (§5.1). The brief forbids changing
   `--update`, so this needs its own task.

## 1. Decision 1 — the flag's name and contract

**Name.** The flag is `--projections-only`, not T543 §6.2's suggested `--self-refresh`. The mode is
not specific to this repository. Any downstream target can use it to pick up harness fixes without
the `docs/` merge or the runtime copy. The name says what it touches, not where it is used.

**Contract:**

- **Opt-in.** Without the flag, `install.sh` behaves exactly as at `e598547`.
- **Mutually exclusive with `--update`.** Passing both exits 1 before anything is written. Letting
  `--update --projections-only` silently mean one or the other would make the flag's safety
  guarantee depend on how the reader parses the command. That is the misreading this mode exists
  to remove.
- **Requires an existing install.** It uses `require_existing_install`, the same `AGENTS.md` check
  `--update` uses. It is a refresh. On an empty target it would produce a harness with no `docs/`
  and no runtime, which is a broken install rather than a fresh one.
- **Uses `--update` semantics for everything it does run.** Trees are replaced with stale-file
  deletion, and the project-local excludes are honoured. MCP configs are merged, not overwritten.
  Both are needed to reach zero drift:
  - Plain-copy semantics leave files removed upstream in place. T543's gate counts those as drift.
  - A plain copy of the MCP configs would destroy hand-added servers, such as the `cwso` server in
    root `.vscode/mcp.json`.
- **Works with `--dry-run`.** The target is left unchanged, which is tested under both copiers.

**The root refusal (`install.sh` lines 76–88 at `e598547`).** Its stated reason is *"install mode
can overwrite curated repository files"*, and that reason holds:

- A plain install at the root runs `copy_tree_into "$IMPLEMENTATION/docs" "$TARGET/docs"`. That
  overwrites the task ledgers with their templates.
- It also self-copies `implementation/runtime/*` onto itself.
- It plain-`cp`s the MCP configs over hand-added servers.

The curated files at risk are `docs/`, the source under `implementation/`, and hand-merged MCP
state. `--projections-only` writes none of `docs/` or `implementation/`, and it merges MCP configs
instead of copying them. **It therefore does not engage the refusal's reason, and it is permitted
at the root.**

It is permitted there only with `--platform all`:

- The root hosts every platform.
- The T543 gate compares the root with a `--platform all` install.
- A single-platform run would also re-render root `AGENTS.md` with a one-platform path map. That is
  a regression, and the gate would flag it.

**Why `--update` was not made root-illegal**, as T543 §6.2 recommends. That would change what an
existing invocation does, and the brief forbids it. It is now a cheap follow-up decision, and §5.1
strengthens the case for it.

**Message changes.**

- The refusal gains two lines:
  - that `make sync && make verify` do not write the root;
  - the `--projections-only` command.
- The two preflight messages name the flag actually used. The text for `--update` is unchanged.
- In this mode the post-install MCP-dependency and search-index notices are skipped, because they
  describe a runtime install this mode did not perform.

## 2. Decision 2 — which install functions run, and which are skipped

This is an exhaustive list of every function in `install.sh` and every top-level step with an
effect.

| Function / step | Under `--projections-only` | Why |
|---|---|---|
| argument parsing; `resolve_abs_path` | runs | new flag and mutual-exclusion check |
| repository-root check (lines 76–88) | runs, new branch | permitted with `--platform all` only (§1) |
| `require_existing_install` | **runs** | refresh-only contract (§1) |
| `validate_before_update` | **runs** | the same per-tree data-loss warnings `--update` prints, naming the flag used |
| `validate_github_agents` | **runs** | must not propagate corrupted `.github/agents` aliases (v6.0.5); see §5.4 for a gap |
| `install_common` | **runs, reduced to `install_agents_doc`** | returns early before the two project-owned steps |
| `install_agents_doc` | **runs** | `AGENTS.md` is a render of source (§3) |
| `install_docs` | **skipped**, plus tripwire | `docs/` is project-owned once installed |
| `merge_task_docs` → `scripts/merge-task-docs.py` (the ledger merge) | **skipped**, reached only via `install_docs`; plus its own tripwire | the `fee245a` failure; see §5.2 |
| `merge_tree_preserve_existing` | never reached, called only by `install_docs` | — |
| `install_mcp_server_runtime` | **skipped**, plus tripwire | `implementation/runtime/` is not a projection, and at the root it *is* the source (§5.1) |
| `install_tree_into` | runs, as `sync_tree_into` because `UPDATE=1` | stale-file deletion with the local-path excludes |
| `sync_tree_into` | runs, for the eight trees only | — |
| `copy_tree_into` | never reached | fresh-install semantics would leave removed-upstream files behind |
| `merge_or_copy_mcp_json` | runs: the merge path when the dest exists, a plain copy when it is absent | hand-added servers and `inputs` survive (ADR-002) |
| `install_cursor` | runs | `.cursor/` plus `.cursor/mcp.json` |
| `install_github` | runs | `.github/` minus `GITHUB_LOCAL_PATHS`, plus `.vscode/mcp.json` |
| `install_gemini` | runs | `.gemini/` plus `.gemini/settings.json` |
| `install_opencode` | runs | `.opencode/` plus `.opencode/opencode.json` |
| `install_pi` | runs | `.pi/` plus `.pi/mcp.json` |
| `install_claude_code` | runs | `.claude/` minus `CLAUDE_LOCAL_PATHS`, `.mcp.json`, `cp` of `CLAUDE.md` |
| `install_cline` | runs | `.cline/`, `.clinerules/`, `.cline/mcp.json` |
| `run` | runs | dry-run wrapper, unchanged |
| post-install notices (not a function) | **skipped** | they describe the runtime install |
| `refuse_in_projections_only` (new) | tripwire | first statement of `install_docs`, `merge_task_docs` and `install_mcp_server_runtime`. Exits 70 before writing anything if a future edit reaches them in this mode. |

The tripwire is unreachable by design. It was proven live by mutation: with `install_common`'s
early return removed, the run exits 70 with `install_docs must never run under
--projections-only`, and the ledger is untouched.

## 3. Decision 3 — `AGENTS.md`, `CLAUDE.md` and the MCP configs are in scope

All three are refreshed. The reasons:

1. **Existing contract.** The installer already treats them as harness-owned.
   - `install_agents_doc` re-renders `AGENTS.md` on every install and every `--update`.
   - `install_claude_code` `cp`s `CLAUDE.md` every time.
   - The MCP configs are merge-owned under ADR-002.

   None of them is project-owned by the installer's own rules. Leaving them out would make the
   new mode *more* conservative than `--update` about files `--update` already owns, with no
   safety gain.
2. **The gate compares them.** If the mode skipped them, the next source change to `AGENTS.md` or
   an MCP config would create drift that no safe mode could cure. That recreates exactly the
   asymmetry this task removes (T543 §5).
3. **Measured today, they are no-ops at the root:**
   - T543 measured 0 drift in all nine files.
   - I merged copies of the seven root MCP configs through `merge-mcp-json.py` exactly as the mode
     does. All seven, including their sidecars, came out **byte-identical**. That includes the
     main checkout's uncommitted edit to `.vscode/mcp.json`, whose contents I did not read.
   - In the rehearsal (§4.3), none of the nine files changed.
4. **Merged, not copied.** The MCP configs go through `merge_or_copy_mcp_json`. Hand-added servers
   and `inputs` survive, which is tested.

## 4. Proof

### 4.1 Existing invocations unchanged (measured, one-off)

I built two synthetic repositories with identical `implementation/`. One held `HEAD`'s
`install.sh`, the other the modified one. I ran the same invocations through each, under `rsync`
and with `rsync` removed from `PATH`, and compared exit code, stdout, stderr, file set, bytes and
modes.

The invocations:
- fresh `--platform` for each of the 8 values;
- `--update --platform all` and `--update --platform pi` on a stale, seeded project;
- `--update --dry-run`;
- fresh `--dry-run`;
- the plain-install root refusal, run against each copy's own root.

**Result: 26 of 26 identical**, with one exception, which is not a real difference: the cp-fallback
`--update --dry-run` stdout. `HEAD` itself differs from run to run there, because the fallback
prints `mktemp -d` paths. With those normalised, old and new are identical.

### 4.2 `tests/functional/test_install_projections_only.py` (new, 15 tests)

It runs only against temp directories. The repository-root cases use a synthetic copy of `scripts/`
and `implementation/` whose own installer targets its own root. That is the real code path, but
not the real root.

**The stale synthetic root** is a fresh install with the following changes:
- **Stale projections:** six edited, including `AGENTS.md` and `CLAUDE.md`. One shipped file is
  deleted, and three removed-upstream files are added.
- **MCP configs:** a stale leaf in `.pi/mcp.json`, and a hand-added server plus `inputs` in
  `.vscode/mcp.json`.
- **Task ledgers:** a 60-row `active-tasks.md` with project prose, a non-conforming `T42` row and
  no trailing newline, plus a 311-row `completed-tasks.md`.
- **Other project-local files:**
  - `.claude/settings.json` and `.claude/settings.local.json`;
  - seven `.github/` project-local paths, including `workflows/ci.yml`;
  - a task brief and a checkpoint;
  - a runtime `_index/` and a local edit to `implementation/runtime/security/__init__.py`;
  - `README.md` and `src/app.py`.
- **A removed template:** `docs/tasks/validate-tasks.py` is deleted.

**What the tests assert, under both `rsync` and the `cp` fallback:**
- `compute_drift` is non-empty before the refresh and **empty** after it.
- Removed-upstream files are gone, and the hand-added MCP server survives.
- **Every file outside the harness trees keeps its bytes, mode *and mtime*.** This covers `docs/`,
  `implementation/` and the project's own files, so they were not even rewritten.
- The project-local paths inside `.claude/` and `.github/` keep their bytes and mode. Under
  `rsync` they also keep their mtime. §5.3 explains why the fallback cannot.
- **Ledger, specifically:** both ledgers are byte-identical with unchanged mtime and the same line
  count, and `validate-tasks.py` is not re-seeded.
  - **Non-vacuity control:** the same fixture under `--update` *is* rewritten, and the template is
    re-seeded. So the ledger assertion proves the merge never ran, not that it happened to be a
    no-op.
- `--dry-run` leaves the target unchanged.

**Contract tests:**
- a `--platform pi` refresh writes only `.pi/` and `AGENTS.md`;
- combining the flag with `--update` exits 1 and writes nothing;
- on an empty target it exits 1 and writes no files;
- `--help` documents the flag;
- a guard checks that the merge-owned classifier finds all seven MCP configs.

**Repository-root tests (synthetic):**
- `--projections-only --platform all` succeeds under both copiers.
- `docs/` and `implementation/` keep bytes, mode and mtime, and drift reaches 0.
  - Under the `cp` fallback this is exactly the case where `--update` deletes the runtime source
    (§5.1).
- `--platform pi` is refused and nothing changes.
- A plain install is still refused, and the refusal names `--projections-only`.

**Mutation checks** (`install.sh` was temporarily edited and then restored; its hash was verified):
- Letting the mode run `install_docs` and the runtime copy fails 9 tests, including both ledger
  tests under both copiers.
- Letting the mode keep fresh-install copy semantics fails 5 tests.

**In CI's own image:** I ran `python:3.12-alpine` with `apk add bash`, busybox `cp` and no
`rsync`. The worktree was streamed in with `tar`, because the Docker daemon cannot see host paths.
The final run covered the new file, T543's six parity tests (all except the one that compares the
real root) and all of `test_install_script.py`. It gave **54 run, OK, 4 skipped**. The skips are
exactly the three new `rsync`-only variants plus T518's existing `rsync`-only test.

### 4.3 Rehearsal of the plan-082 §2 refresh, on a full copy

I copied every tracked file of a revision, with this change's `install.sh` overlaid, to a temp
directory. I then ran that copy's `install.sh --target . --platform all --projections-only` against
the copy's own root. I did this twice:
- at this branch's base, `e598547`, copied from the worktree;
- at `b368c71`, the `develop` head after T547/T551 landed mid-task, taken via `git archive`, which
  only reads objects.

| | `e598547` `rsync` | `e598547` `cp` | `b368c71` `rsync` | `b368c71` `cp` |
|---|---|---|---|---|
| exit | 0 | 0 | 0 | 0 |
| files changed | 55 | 55 | 80 | 80 |
| changed set == that revision's `root-install-drift.json` | **yes** | **yes** | **yes** | **yes** |
| changes under `docs/` or `implementation/` | 0 | 0 | 0 | 0 |
| `current_drift()` afterwards | `[]` | `[]` | `[]` | `[]` |

**What the rehearsal does not model:**
- **Untracked or ignored files** in the real root's eight trees. I checked read-only with
  `git ls-files --others` and with `--ignored`: there are none, and none of the trees contains
  symlinks or special files.
- **The main checkout's uncommitted `.vscode/mcp.json`.** This is covered by the separate MCP
  measurement in §3.

## 5. Findings and corrections to the brief

1. **New defect (major, not fixed): `--update` at a repository root without `rsync` deletes source.**
   - **Mechanism.** At the root, `install_mcp_server_runtime` calls `sync_tree_into` with
     `src == dest` (`implementation/runtime/memory`). The fallback runs `rm -rf "$dest"`, which
     deletes the source, and then `cp`s from the now-missing source. That fails, and `set -e`
     aborts with exit 1.
   - **Where it stops.** The abort comes *after* the ledger merge and the `AGENTS.md` render, and
     *before* any projection tree.
   - **Measured** on a synthetic copy of the repository: `implementation/runtime/memory/` went from
     22 files to 0.
   - **With `rsync`** the same call is a self-sync no-op.
   - **Why not fixed.** It is `--update` behaviour, which the brief forbids changing.
   - **Recommendation.** Open a follow-up either to refuse `--update` at the root (T543 §6.2) or
     to skip the self-copy when `src == dest`.
   - `--projections-only` never reaches this code, and the repository-root tests prove that under
     the fallback.
2. **Brief §2's function list omits the two functions that decide the outcome.** They are
   `install_tree_into`, which chooses between copy and delete-sync by `UPDATE`, and
   `merge_or_copy_mcp_json`, which chooses between `cp` and merge by `UPDATE`.
   - Without them, "run `install_<platform>`" is ambiguous. With fresh-install semantics, drift
     does not reach zero (mutation check, §4.2).
   - The list also omits the preflight functions (`require_existing_install`,
     `validate_before_update`, `validate_github_agents`) and the post-install notice block.
   - "The ledger-merge path" is `merge_task_docs` → `scripts/merge-task-docs.py`, reached only
     through `install_docs`.
3. **The `--update` root warning overstates its safety.** It says *"templates will be merged
   without overwriting existing docs files"*, but `merge_task_docs` unconditionally rewrites both
   ledgers.
   - It drops non-conforming rows and normalises the trailing newline. The control test shows a
     real rewrite.
   - On today's real ledgers it is byte-neutral: 474 and 349 lines, measured in-process on file
     contents with nothing written. It still rewrites the files, though.
   - The text is left unchanged, as `--update` behaviour.
4. **`validate_github_agents` uses `rg`, which CI's alpine image does not install.** Inside
   `if rg -q …`, command-not-found (127) reads as "no match", so the v6.0.5 `name:` check is
   silently skipped there. This is by bash semantics, not run. Minor.
5. **Fallback metadata.** The `cp` fallback of `sync_tree_into` saves and restores project-local
   in-tree files with `cp -r`.
   - Their bytes and mode survive (measured with 0600 and 0755 files).
   - Their mtime does not, and under a restrictive umask their mode bits could be narrowed. That
     second point is by inspection, not measured.
   - This is existing `--update` behaviour, and the new mode inherits it. The test states it rather
     than hiding it.
6. **Brief §3's CI claim is correct.** `unit-tests` installs `git bash nodejs docker-cli`, and
   there is no `rsync`. It is confirmed in the image itself.
7. **Cosmetic.** `validate_before_update` warns about all eight trees even for a single-platform
   run. This is pre-existing and inherited.

## 6. Next step (not done here)

Plan-082 §2 describes the next step: one refresh of the real root, **with explicit user approval at
the time**, using:

    bash scripts/install.sh --target . --platform all --projections-only

The same MR must:
- empty `tests/_baselines/root-install-drift.json`;
- diff `docs/tasks/` byte-for-byte before and after;
- record `git status` before and after.

§4.3 predicts that the set of changed files equals the declared list at that revision: 80 paths
at `b368c71`, and more if further knowledge MRs land first. If the changed set differs from the
declared list in either direction, abandon the refresh and investigate.
