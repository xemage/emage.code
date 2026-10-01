# T555 — `install.sh --update` without `rsync` copies this repository's memory index into client projects

**ID:** T555
**Owner:** DevOps Engineer
**Status:** in_review
**Priority:** P1
**Tier:** judgment
**Affects:** —
**Depends on:** T552
**Created:** 2026-09-30
**Based on:** `docs/plans/plan-085-index-leak.md`; `docs/tasks/task-T552.md`; `docs/tasks/task-T553.md`;
`scripts/install.sh`; `.gitignore:92`.

## 1. The defect — a confidentiality leak, not clutter

`install_mcp_server_runtime` installs `implementation/runtime/memory/` with `_index` and `__pycache__`
excluded. Under `--update`, `install_tree_into` calls `sync_tree_into`. With `rsync`, the excludes are
honoured. **Without `rsync`, the fallback copies the whole source tree, excludes included, and only
protects the target's own copies of excluded paths** — so a target with no `_index/` of its own
**receives the source's**.

`implementation/runtime/memory/_index/` in an authoring checkout is **populated**: verified on
2026-09-30, 3 files, 460 KB, under a directory named for this repository (`em-age-emage.code`), built
locally by `implementation/runtime/memory/build.py`. It is gitignored (`.gitignore:92`) — which keeps it
out of source control, but **the installer reads the working tree, not git**.

So on any host without `rsync` (CI's `python:3.12-alpine`, many containers), running
`scripts/install.sh --target <client-project> --update` from an authoring checkout **copies this
repository's memory search index into the client's project.** The same path leaks `__pycache__/` for
every runtime tree, including T553's `runtime/handoff/`.

The **fresh-install** path is not affected: `copy_tree_into`'s fallback removes the excludes it placed.
Found by T553's implementer, who pinned the `__pycache__` side with an `@unittest.expectedFailure`
test in `tests/functional/test_install_handoff_runtime.py` that will turn red once fixed.

`**Affects:** —` — `install.sh` is not a registry component; this P1 row cannot block merges.

## 2. What to do

1. **Fix `sync_tree_into`'s fallback** so excluded paths are never copied from source to destination,
   while still preserving the destination's own copies of them — i.e. match `rsync --exclude`
   semantics exactly under `--delete`. Say how you verified the two copiers now agree.
2. **Convert the pinned `@expectedFailure` test into a normal passing test**, and add one specifically
   for `runtime/memory/_index/`: a synthetic source with a populated `_index/`, `--update` into a target
   without one, under the `cp` fallback → the target must have **no** `_index/` afterwards.
3. **Audit every other exclude-bearing call** (`copy_tree_into`, `merge_tree_preserve_existing`, each
   `install_tree_into`) for the same asymmetry between copiers, and report what you find.
4. **Consider — and argue — whether the installer should additionally refuse to ship any path matched
   by `.gitignore`**, as defence in depth. Don't implement it if it would change other invocations
   beyond this defect; say what it would cost.

## 3. Constraints

- **Never run any install against this repository's root or the main checkout.** Synthetic copies in
  temporary directories only, under **both** `rsync` and the `cp` fallback (hide `rsync` from `PATH`).
- **Do not read the contents of the real `_index/`.** Build synthetic ones for tests.
- Compare old and new behaviour by **swapping `install.sh` in place** and verifying its hash after
  restoring — never by copying it elsewhere.
- Every invocation not deliberately changed must be unchanged in what it writes — prove it.
- **Write scope:** `scripts/install.sh`, files under `tests/functional/`, and
  `docs/artifacts/install-exclude-parity-v1.md`; the `**Status:**` line of this brief.
- Commit locally, one commit; **do not push; never merge or approve anything.**
- A parallel task may be editing `implementation/knowledge/`, its projections and
  `tests/_baselines/root-install-drift.json` — stay out of those.

## 4. Verification

`python3 tests/run.py` (exit code, redirected to a file; the expected-failure count must drop to 0),
`--print-drift` unchanged, `validate-tasks.py`, `check-maturity.py`, `sync.mjs --check`,
`generate-registry.py --check`, `scorecard.py --check`, and `git status` of the worktree and the main
checkout identical before and after.

## 5. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`.
**If anything in this brief is wrong, report it.** Seventeen consecutive tasks have found a defect in
their brief.
