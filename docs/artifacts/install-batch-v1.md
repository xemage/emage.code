# T559 — `install.sh` batch: P17, P18, P20, P21, v1

**Based on:** `docs/tasks/task-T559.md`; `docs/plans/plan-089-install-and-golden-batches.md`;
`docs/plans/plan-085-index-leak.md` §3; `docs/plans/plan-086-round-close.md` §2;
`docs/artifacts/install-update-root-v1.md` (T552); `docs/artifacts/install-exclude-parity-v1.md` (T555);
`docs/artifacts/root-refresh-mode-v1.md` (T550) §5; `scripts/install.sh` and `scripts/merge-task-docs.py` at `0d0649e`.
**Author:** DevOps Engineer. **Date:** 2026-10-01. **Tree measured:** `develop` at `0d0649e`.

| Item | Commit | Effect |
|---|---|---|
| P17 | `c750a0b` | Every target strictly inside the repository is refused, in every mode, before anything is written. |
| P18 | `76277e6` | `--help` now says `--update` always rewrites both existing task ledgers, and how. |
| P20 | `234a908` | `__pycache__` is excluded from both `docs/` copies, at any depth. |
| P21 | `975352c` | The `cp` fallback resolves file/directory/symlink type conflicts as `rsync` does, and refuses where `rsync` refuses, before writing. |

## 0. Verdict

1. **P17.** A target that is, or is below, `implementation/` is refused. So is every other target below
   the repository root. The root itself keeps its T550/T552 rules. Overlap is decided by `-ef` on every
   ancestor of the target's physical path. That catches symlinks to `implementation/` or to the root. It
   does **not** catch `<repo>-extra`, whose name merely shares the repository's prefix.
2. **P18.** The help text claimed an existing ledger is "never rewritten beyond its task rows". That
   was false in four measured ways (§2). It now states them.
3. **P20.** `docs/**/__pycache__/` no longer ships. This deliberately changes what installs write
   from a source that has such caches.
4. **P21.** I chose parity, not a blanket refusal. The fallback now removes exactly what `rsync` removes. It refuses
   only the one case `rsync` refuses, and does so before writing anything to that tree, where `rsync`
   fails after a partial transfer. **Scope expansion:** `sync_tree_into`'s fallback had the same class
   of defect, contrary to T555 §8.2. In one case it wrote outside the target and exited 0. It is fixed
   in the same commit.
5. **Every invocation not deliberately changed writes exactly what it wrote before:** 37/79 recorded
   invocations are byte-identical, and all 42 differences fall into a deliberate category (§5).

## 1. P17 — targets inside the repository

### 1.1 What `HEAD` did

These were measured on synthetic repositories, each a copy of `scripts/` and `implementation/` whose own
installer was run. Paths are counted against a pristine copy (bytes, mode, link target).

| Target (synthetic repo `R`) | `rsync` | `cp` fallback |
|---|---|---|
| `R/implementation --update` | exit 1; 40 source paths changed (`AGENTS.md` re-rendered, `implementation/implementation/` created) | same |
| `R/implementation/.cursor --platform cursor` | **exit 0**; 240 source paths changed: `.cursor` copied into its own subdirectory, nested several levels deep, to a depth that varied between runs | exit 1 (`cannot copy a directory into itself`); 59 paths changed |
| `R/implementation/new-dir --platform pi` | **exit 0**; 183 paths written into the source tree | same |
| `R/tmp/scratch-install --platform pi` | exit 0; 184 paths written into the working tree | same |

### 1.2 Decision: refuse every target below the root, not only `implementation/`

- **`implementation/` is not negotiable.** It is the source the installer reads, so an install there is
  written from itself. The brief asks for this refusal.
- **Elsewhere in the repository, I refuse too:**
  1. **No legitimate use was found.** No script, Makefile target, CI job or document installs inside
     the repository. Every recorded install (`docs/tasks/task-T26x`, `T27x`, `T29x`, `T355`, `plan-014`)
     targets `/tmp/...`. The existing root refusal already recommends `--target /tmp/emage-test`.
  2. **It writes a second harness into the repository's own working tree.** That includes `AGENTS.md`,
     `CLAUDE.md`, the platform trees, a second `docs/tasks/` ledger pair, and
     `implementation/runtime/`. In a tracked directory such as `docs/`, those are new repository content.
  3. **One rule is easier to trust than two.** "The repository is never a target, except its root under
     `--projections-only`" needs no case analysis, and the `-ef` walk already pays for it.
- **What it costs.** A scratch install in a gitignored in-repo directory (`tmp/`, `.tmp/`, `build/`) is
  now refused. It is a convenience use with a one-word workaround (`/tmp`).
- **An argument I checked and dropped.** I suspected an in-repo install would break
  `test_link_integrity` (which walks `rglob("*.md")` regardless of `.gitignore`). Measured: a standalone
  install has 0 broken links in 500 `.md` files, so that argument does not hold.

### 1.3 Mechanism

- **`physical_path`** resolves the deepest existing ancestor with `cd -P` and appends the rest. The
  target need not exist.
- **`path_within`** compares each ancestor of that path with the anchor by `-ef`.
- **Checked on 16 synthetic paths:**
  - correctly caught: an alias of `implementation/`, an alias of the root plus a subpath, nonexistent
    subpaths, and relative paths;
  - correctly not caught: `R-extra`, `R/../R-extra` and `/`.
- **Bind mounts are not verified:** there was no root access. The `-ef` comparison is the mechanism that
  should catch them.

### 1.4 What else changed

- The refusals happen before `mkdir -p "$TARGET"`, dry-run included.
- `--help` documents them on the `--target` line.
- Tests: `tests/functional/test_install_target_inside_repo.py` (12 tests, refusals under both copiers).
  Each refusal test asserts that the repository's bytes, mode, mtime **and set of paths** are unchanged.
- **On `HEAD`, swapped in place:** 21 failing subtests. The prefix-sibling control passes on both
  versions.

## 2. P18 — `--update`'s ledger wording

**Old text, exact:** *"In docs/tasks/, an existing ledger is never rewritten beyond its task rows — its
surrounding prose is the project's own record, not the template's. Missing files are seeded."*

**Measured** with `merge-task-docs.py`'s `merge_ledger` and `sync_task_docs` on synthetic ledgers:
- **Both existing ledgers are always written.** Even a byte-identical result gets a new mtime.
- **Non-conforming rows are dropped.** That means a `T42` row, with a warning, and an `_Example:` row,
  silently.
- **CRLF becomes LF, and a missing final newline is added.**
- **A ledger with no task table at all is replaced by the template**, keeping only its task-row lines.
  Its own prose (`# My ledger`, notes) is lost. This directly contradicts "never rewritten beyond its
  task rows".
- **Prose around a table is kept,** as is a second table after the first.

**New text:** *"…each existing task ledger (active-tasks.md, completed-tasks.md) is always rewritten: rows
of its task table that are not T<NNN> task rows are dropped (with a warning), line endings become LF and
a missing final newline is added. Prose around the table is kept -- it is the project's own record -- but
a ledger with no task table at all is replaced by the template, keeping only its task rows. Every other
docs/ file is seeded when missing and otherwise left alone."*

**Tests and invocations:**
- `test_install_script.py` gains `test_update_help_text_states_that_the_ledgers_are_rewritten`. It fails
  on the P17-state script. I removed the two old-wording assertions from the existing help test.
- Only `--help` output changes.

**Caveat on the last sentence.** It holds for today's layout:
- `implementation/docs/` holds only subdirectories, and `docs/tasks/` holds only files.
- `--update` would not seed a top-level file in `implementation/docs/`, nor a subdirectory of
  `docs/tasks/`. That was true before this change as well.

## 3. P20 — `docs/**/__pycache__/`

- **Change.**
  - `DOCS_EXCLUDES=(__pycache__)` is passed to `copy_tree_into` on a fresh install.
  - It is also passed to `merge_tree_preserve_existing` on `--update`. That function gains optional
    excludes, with T555's meaning: never copied from the source, at any depth; a target's own is left alone.
  - Its `cp` fallback reuses `copy_contents_excluding`, which now takes the `cp` option (`-r` or `-rn`)
    as its first argument.
  - The `--update` loop also skips an excluded top-level `docs/` subdirectory. Otherwise
    `implementation/docs/__pycache__/` would be merged as if it were a docs section.
- **`docs/tasks/` on `--update`** goes through `merge_task_docs`, which copies top-level files only, so it
  needed no change.
- **The source tree.** `implementation/docs/tasks/__pycache__/` exists in the main checkout. A fresh
  worktree does not have it, because it is gitignored. It was not read or deleted; the tests plant
  **synthetic** caches in synthetic repositories.

| Planted synthetic caches | `HEAD`, `rsync` | `HEAD`, `cp` | Now, both |
|---|---|---|---|
| Fresh install | `docs/tasks/__pycache__/`, `docs/plans/__pycache__/` ship | same | none ship |
| `--update` | `docs/plans/__pycache__/` ships | same | none ship |
| Target's own `docs/plans/__pycache__/`, plain re-install or `--update` | source cache merged into it | same | left alone, nothing added |

**This deliberately changes what installs write** from a source that has docs caches.
- **Without such caches:** every recorded invocation writes the same bytes as before.
- **The only other visible change:** under `rsync`, the `--dry-run` echo of the docs copies gains
  `--exclude=__pycache__` (3 invocations).
- **`cp` dry-run echoes are unchanged:** with no hits, the fallback runs the same single `cp`.

**Tests:** `tests/functional/test_install_docs_pycache.py` (3 tests). On `HEAD`, swapped in place, 8
subtests fail, every one under both copiers.

## 4. P21 — type conflicts in the `cp` fallback

### 4.1 `rsync`'s semantics, measured

Measured with `rsync` 3.2.7: `-a`, no `--delete`/`--force`, against GNU `cp` 9.4, one conflict per case.

| Source / target | `rsync -a` | `cp -r` (`HEAD` fallback) |
|---|---|---|
| file over **empty** dir | replaced | exit 1 |
| file or symlink over **non-empty** dir (excluded content counts) | **exit 23** "could not make way", rest transferred; `--dry-run` fails too | exit 1 |
| dir over file, or over any symlink (to a dir, a file, or dangling) | replaced | exit 1 |
| file over symlink to a file | link replaced | **exit 0, wrote THROUGH the link** into the file it points at |
| file over dangling symlink, or over symlink to a dir | link replaced | exit 1 |
| symlink over file or over symlink | replaced | replaced |

### 4.2 Decision: parity, with the one refusal moved before any write

- Exact parity is reasonable here. `rsync` has only four rules (`install.sh`, "Type conflicts"), and
  emulating them is a short pre-pass. The alternative, refusing every conflict, would make the fallback
  fail where `rsync` succeeds: the very asymmetry this item removes.
- **`make_way_for_source`** walks the source, minus excluded names, against the target before
  `copy_tree_into`'s `cp`. For each conflicting path:
  - it removes what `rsync` would remove: `rm -f` for a file or link, `rmdir` for an empty directory;
  - for a non-empty directory where the source has a file or symlink, it exits 1. The message names
    every such path, and nothing has been written to that tree. `rsync` writes the rest of the tree and
    then exits 23. Both fail; the fallback's failure is cleaner.
- **Not provided under either copier:** atomicity across trees. Earlier trees of the same install have
  already been written, as with `rsync`.

### 4.3 Scope expansion: `sync_tree_into` (`--update`)

- **T555 §8.2's claim.** It said `sync_tree_into` "agrees with `rsync` on success or failure in every
  conflict case". The fuzz shows otherwise.
- **The trigger.** A kept (excluded) target path sits below a path that the source ships as a file or
  symlink. `rsync` refuses in that case (exit 23). The fallback ran `rm -rf "$dest"` first, then did one of two things:
  - **It failed at `mkdir -p`.** The kept path was gone from the target, and its backup was stranded in
    a `mktemp` directory. A real instance: my P21 test fixture `{"own": true}`, the target's own
    `.cursor/…/mcp.json`, ended up alone in `/tmp/tmp.ZyyZoifdf4/payload`.
  - **It restored the kept path through a symlink shipped by the source**, writing outside the target,
    and **exited 0**.
- **The fix.** `refuse_kept_paths_under_source_nondirs` applies `rsync`'s refusal before the `rm -rf`.
  It is the same class (type conflicts, `cp` fallback) and the same file, so I fixed it in the P21
  commit rather than leaving half the class. I flag it here as outside the brief's literal wording.

### 4.4 Differential fuzz against real `rsync`

- **Harness.** One-off, in the scratchpad. It is T555's method: it extracts `run() { … }` up to
  `install_tree_into() {` from `scripts/install.sh` **in place**, and runs each writer under real
  `rsync` and with `rsync` absent from `PATH`.
- **Trees.** Random source and target trees are built from one name alphabet (`a b c .h _index
  __pycache__`), so type conflicts are frequent. They include dangling links and links that point
  outside the target. Target files are aged to defeat `rsync`'s quick check.
- **A mismatch is any of:**
  - `cp` wrote outside the target;
  - the two copiers differ on success;
  - both succeed with different trees.
- **Reported separately, not as mismatches:** cases where both fail. For those I record whether `cp`
  wrote anything first.

| Writer, run | `HEAD` | Now |
|---|---|---|
| `copy_tree_into`, host (GNU, `rsync` 3.2.7), seeds 0..299 | **43 / 300** (41 `rsync` ok / `cp` fails, 2 `cp` wrote outside); plus 20 both-fail cases where `cp` wrote first | **0 / 300**; all 37 both-fail cases wrote nothing |
| `copy_tree_into`, host, seeds 1000..2999 | — | **0 / 2000** |
| `sync_tree_into`, host, seeds 0..299 | **5 / 300** (all wrote outside, exit 0 vs 23); plus 18 both-fail cases after `rm -rf` | **0 / 300**; all 23 both-fail cases wrote nothing |
| `sync_tree_into`, host, seeds 1000..2999 | — | **0 / 2000** |
| both, busybox `cp`/`find` + `rsync` 3.5.0 (`python:3.12-alpine`), seeds 0..299 | — | **0 / 300** each |

My generator is not T555's. T555's was not committed, so its "26/300 (58 before)" cannot be re-run. The
before/after counts above come from one generator, measured on `HEAD` and on this change.

**`merge_tree_preserve_existing` (`--ignore-existing` vs `cp -rn`)** is unchanged by P21. 6/300 cases
still mismatch, all two symlink cases (§8.1).

### 4.5 Tests

`tests/functional/test_install_type_conflicts.py` has 6 tests.

**End-to-end, under both copiers:**
- five conflict kinds are replaced on a plain re-install, and the outside file is never written;
- a non-empty directory is refused, and `.cursor/` is untouched under `cp`;
- `--dry-run` writes nothing, and its plan names the `rm -f`s;
- `--update` refuses a kept `mcp.json` below a shipped file.

**Differential:** a seeded 120-case differential test of both writers against real `rsync`. It is
skipped without `rsync`. On `HEAD` those seeds give 28 `copy_tree_into` and 9 `sync_tree_into`
mismatches; now none.

**On `HEAD`, swapped in place:** 9 failures and 1 error. Every `cp` subtest and both differential tests
fail; every `rsync` subtest passes. The error is the `--update` case: `HEAD` deleted the file the test
reads.

## 5. Every other invocation is unchanged

This uses the T552/T555 method.
- **What is recorded per invocation:**
  - exit code;
  - normalised stdout and stderr;
  - every target path's kind, sha256, mode and link target;
  - for synthetic-repository cases, the repository tree;
  - for conflict cases, the outside directory.
- **The installer under test** is `scripts/install.sh` **swapped in place** in the worktree. Every
  restore was sha256-verified.
- **The seed project** was made once, by `HEAD`, and shared.

**Coverage:** 79 invocations, i.e. `--help` plus 39 per copier:
- fresh install × 8 platforms, and a fresh `--dry-run`;
- `--update` `all`, `--update` `pi`, and `--update --dry-run`;
- `--projections-only` `all` and `pi`;
- the exclusivity error, and a plain re-install;
- synthetic root × 5;
- **P17:** 9 in-repository targets, plus a prefix sibling;
- **P20:** 2 planted-cache cases;
- **P21:** 5 conflict kinds, plus a conflict `--dry-run`.

| Comparison | Identical | Differing |
|---|---|---|
| `HEAD` vs `HEAD` (determinism) | 79 / 79 | — |
| `HEAD` vs this branch | **37 / 79** | 42, every one deliberate (below) |

| Category | Count | What differs |
|---|---|---|
| P17 targets inside the repository | 18 | now exit 1, nothing written (repository equal to a pristine copy) |
| P21 `cp` conflict cases | 6 | now `rsync`'s outcome; non-empty-dir case refused cleanly; outside file no longer written |
| P20 planted docs caches | 4 | only the `__pycache__` paths |
| P20 `rsync` `--dry-run` echo | 3 | `--exclude=__pycache__` in the docs `rsync` lines only |
| synthetic-root cases | 10 | only `scripts/install.sh` itself, which is the file under test and differs by construction |
| `--help` | 1 | P17 and P18 text |

**Within this branch, the two copiers agree on all 39 invocations:**
- same success or failure;
- identical trees (kind and bytes) whenever both succeed;
- identical outside directory.

On `HEAD` they agree on 34/39.

## 6. Verification (worktree, branch base `0d0649e`)

| Gate | Result |
|---|---|
| `python3 tests/run.py` | exit 0; `Ran 904 tests`, `OK (skipped=23)`. The baseline is 882 / 23 skipped; this adds 22 tests. |
| All 10 installer test modules | `Ran 106 tests`, `OK`. This ran before the last, behaviour-neutral split of `make_way_for_source`; the full suite above ran after it. |
| The 3 new modules, `test_install_exclude_parity` and `test_install_update_root`, in `python:3.12-alpine` (busybox `cp`/`find`, `rsync` 3.5.0), on the final script | `Ran 38 tests`, `OK` |
| `python3 -m tests.functional.test_root_install_parity --print-drift` | the 6 committed `/batch` paths |
| `tests.functional.test_command_audience_paths` | OK |
| `docs/tasks/validate-tasks.py` | `TASK LEDGER: PASS` |
| `check-maturity.py --root implementation` | exit 0, 0 fail |
| `sync.mjs --root implementation --check` | no drift across 577 files |
| `generate-registry.py --check` | up to date |
| `scorecard.py --check` | OK, wrote nothing |
| `git status`, worktree and main checkout | unchanged by the suite |

`develop` moved to `ea0dd4a` (T560) during this task. It touches no file here, and `git merge-tree` shows
a clean merge.

## 7. Defects in the brief and in prior artifacts

1. **T555 §8.2** says `sync_tree_into`'s fallback "agrees with `rsync` on success or failure in every
   conflict case". That is false (§4.3). On `HEAD`, 5 of 300 cases exit 0 where `rsync` exits 23, writing
   outside the target. A further 18 fail only after deleting the target tree.
2. **The brief's "26 of 300 (58 before)"** comes from T555's uncommitted generator and cannot be
   reproduced. §4.4 gives this task's own before/after.
3. **The brief's "exists in the source tree today"** is true of the main checkout, not of a fresh
   worktree (the directory is gitignored). This is immaterial to the fix.

## 8. Findings not fixed

1. **`merge_tree_preserve_existing` symlink cases** (`--update`, `docs/<sub>` other than `tasks/`).
   - **Directory over a symlink to a directory:** `rsync --ignore-existing` exits 0 and writes
     **through** the link. Here `rsync` itself writes outside the target. `cp -rn` exits 1.
   - **File over a dangling symlink:** `rsync` keeps the link and exits 0; `cp -rn` exits 1.
   - The fuzz gives 6/300 mismatches, all of these two kinds.
   - Parity would mean emulating a write-through, so the right fix is a policy decision for both copiers.
     It is not P21's literal scope.
2. **The `sync_tree_into` fallback still strands its backups** in `mktemp` directories if a later
   command fails for a reason other than a type conflict, for example a full disk.
   - `/tmp` holds 178 `tmp.*` directories from 2026-09-30 22:xx that hold `payload` backups. They
     predate this task and were left alone.
   - The 188 that this task's runs on `HEAD` stranded were each verified as this task's synthetic data
     and removed.
3. **Function length.**
   - `sync_tree_into` was 74 lines on `HEAD` and is 75 now, above the 50-line standard. This predates
     the change.
   - Every function added here is at most 43 lines.
4. **`cp` fallback metadata** (T550 §5.5) is inherited and unchanged.
