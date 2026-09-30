# T552 — `install.sh --update` at the repo root deletes source code on a host without `rsync`

**ID:** T552
**Owner:** DevOps Engineer
**Status:** pending
**Priority:** P1
**Tier:** judgment
**Affects:** —
**Depends on:** T550
**Created:** 2026-09-30
**Based on:** `docs/plans/plan-084-round-close-and-fired-triggers.md` §2;
`docs/artifacts/root-refresh-mode-v1.md`; `docs/tasks/task-T550.md`; `scripts/install.sh`.

## 1. The defect — found by T550, confirmed by the orchestrator

At the repository root, `install_mcp_server_runtime` passes the **same path** as source and
destination: `install_tree_into "$IMPLEMENTATION/runtime/memory" "$TARGET/implementation/runtime/memory"`
(and `…/security`), `install.sh` ~lines 490–491, with `IMPLEMENTATION=$REPO_ROOT/implementation` and
`TARGET=$REPO_ROOT`. Under `--update`, `install_tree_into` calls `sync_tree_into`, whose **`cp`
fallback** (taken when `rsync` is absent) runs `rm -rf "$dest"` **before** `cp -r "$src/." "$dest/"`.
Because `src == dest`, it deletes the source before copying from it.

T550's implementer measured it on a synthetic copy of the repository: `implementation/runtime/memory/`
went from **22 files to 0**, exit 1. The abort comes **after** the ledger merge and the `AGENTS.md`
render. With `rsync` the same call is a no-op. CI's `python:3.12-alpine` image has no `rsync`.

`**Affects:** —` is correct: `install.sh` is not a registry component, so this P1 row cannot turn
`check.py --maturity` red (`plan-081` §1).

## 2. Two more `install.sh` findings from T550, in scope here

- **The `--update`-at-root warning is inaccurate.** It says "templates will be merged without
  overwriting existing docs files". `merge_task_docs` always rewrites both task ledgers and drops
  non-conforming rows. (T550 measured the merge byte-neutral on today's ledgers — but it still
  rewrites them, and it is the path that took `active-tasks.md` from 2460 lines to 11 in `fee245a`.)
- **`validate_github_agents` uses `rg`**, which CI's alpine image lacks, so that check is silently
  skipped in CI. Decide: fall back to `grep`, or fail loudly — **not** silently skip.

## 3. Decide, and argue

`--projections-only` (T550) is now the sanctioned way to refresh the repo root. So:

1. **Should `--update` be refused at the repository root outright**, pointing at
   `--projections-only`? That removes both the data-loss path and the ledger-rewrite risk at the root,
   but it changes an existing invocation — which is the point here, and must be stated.
2. **Independently, should `sync_tree_into` refuse or no-op when `src` and `dest` resolve to the same
   directory?** That fixes the class, not just the root call site, at any target. Consider doing both.
3. The accurate text for the warning, if `--update` at the root survives at all.

## 4. Proof — synthetic roots only

**Never run `--update` or any destructive mode against this repository's root.** Build tests under
`tests/functional/` against temporary full copies of the repository, as T550 did, under **both**
`rsync` and the `cp` fallback (hide `rsync` from `PATH`). Show the data loss reproduces on `HEAD` and
does not after your change.

## 5. Constraints

- **Batched with T553** in one dispatch (both edit `scripts/install.sh`; `plan-083` §2). Keep the two
  tasks' changes in separate commits.
- **Write scope:** `scripts/install.sh`, new files under `tests/functional/`, and
  `docs/artifacts/install-update-root-v1.md`. Nothing under `implementation/`, `tests/golden/**`,
  `scripts/scorecard.py`, `tests/_baselines/`.
- Every invocation you do **not** deliberately change must be unchanged in what it writes — prove it,
  and **compare by swapping the file in place**, never by copying `install.sh` elsewhere (a copy
  resolves `REPO_ROOT` to the wrong directory; the orchestrator made exactly that mistake once).
- Commit locally on your branch; **do not push; never merge or approve anything.**

## 6. Verification

`python3 tests/run.py` (exit code; redirect to a file, never pipe to `tail`), `validate-tasks.py`,
`check-maturity.py --root implementation`, `sync.mjs --root implementation --check`,
`generate-registry.py --check`, `scorecard.py --check`, `--print-drift` unchanged, and `git status` of
your worktree and the main checkout identical before and after the suite.

## 7. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`.
**If anything in this brief is wrong, report it.** Sixteen consecutive tasks have found a brief defect.
