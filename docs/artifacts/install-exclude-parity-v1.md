# T555 — Excluded paths mean the same thing with and without `rsync`, v1

**Based on:** `docs/tasks/task-T555.md`; `docs/plans/plan-085-index-leak.md`;
`docs/artifacts/install-update-root-v1.md` (T552); `scripts/install.sh` at `2dd7ae7`;
`tests/functional/test_install_handoff_runtime.py` (T553).
**Author:** DevOps Engineer. **Date:** 2026-09-30. **Tree measured:** `develop` at `2dd7ae7`.

## 0. Verdict

1. **The leak is fixed.** Without `rsync`, `--update` no longer copies the source's excluded paths
   into a target. The two fallbacks now never copy a source path that `rsync --exclude` would skip.
   They do not copy it and then delete it; they never copy it.
2. **The fix covers both `cp` fallbacks, not only `sync_tree_into`'s.** `copy_tree_into`'s fallback
   had the same class of defect. The brief says the fresh-install path is safe; it is not (§7).
3. **"Excluded" now has one meaning under both copiers: `rsync`'s.**
   - A name matches at **any depth**.
   - The source's copy is never transferred.
   - The destination's copy is never overwritten or deleted, including inside a directory that was
     removed upstream.
   - I checked this with a differential fuzz against real `rsync`: **0 mismatches in 2000 runs under
     GNU coreutils and 0 in 2000 under busybox**. On `HEAD` the same fuzz gives **1268 mismatches in
     2000 runs**.
4. **Every invocation writes the same files as before, whenever the source has no excluded content.**
   This covers 43 recorded invocations. The only differences are the command echo of two `--dry-run`s
   under the `cp` fallback (§4).
5. **I did not implement a `.gitignore`-aware filter** (§6). It would make the installer's output
   depend on whether `git` is installed on the host. That is the same kind of copier-dependent output
   this task removes.

## 1. The defect, reproduced on `HEAD`

I built a synthetic source repository from the worktree (`scripts/` and `implementation/`, without
`__pycache__` or `_index`). I then planted **synthetic** excluded content in it:
- `memory/_index/em-age-synthetic/{chunks.jsonl,manifest.json}`;
- `__pycache__/` at the top of `memory/`, `security/` and `handoff/`;
- a **nested** `memory/context_retriever_mcp_server/__pycache__/`. The real authoring checkout has
  this directory, and its `.pyc` embeds the author's absolute source path.

The synthetic repository's own installer ran against temporary targets. I never read the real
`_index/`; I only listed that it exists.

The version under test was selected by **swapping `scripts/install.sh` in place** in the worktree.
Each swap was restored and its sha256 verified. A "leaked" file is a target file whose bytes came
from the planted source.

| Scenario | `HEAD`, `rsync` | `HEAD`, `cp` fallback | Now, both copiers |
|---|---|---|---|
| Fresh install | clean | **leaks** `context_retriever_mcp_server/__pycache__/server…pyc` | clean |
| `--update`, target has no excluded content of its own | clean | **leaks all 6 planted files, `_index/` included** | clean, no `_index/` |
| `--update`, target has its own `_index/` and caches | own files kept | **leaks 3 caches; target's own nested cache deleted** | own files kept byte-for-byte, nothing leaked |
| Plain re-install over a target with its own `_index/` | own files kept | **target's own `_index/` and `memory/__pycache__/` deleted**; nested cache leaked | own files kept, nothing leaked |

The same scenarios, run in CI's image (`python:3.12-alpine`, busybox `cp` and `find`, no `rsync`),
fail on `HEAD` in the same way (§3).

## 2. What `rsync --exclude` means, and how the fallback now does the same

**Measured with `rsync` 3.2.7:** `rsync -a --delete --exclude=_index --exclude=__pycache__`.
- The pattern has no `/`, so it matches the **last path component at any depth**.
- Source matches are not sent.
- Destination matches are never deleted, even under `--delete`.
- A directory that was removed upstream but still holds a protected path is kept, holding only
  that path. `rsync` prints `cannot delete non-empty directory` and exits 0.

**In `scripts/install.sh`:**

- **`check_exclude_names`** requires every exclude to be one literal path component: no `/`, `*`,
  `?` or `[`. This is the only kind of pattern for which `find -name` and a string comparison mean
  exactly what `rsync` means. No current caller passes any other kind.
  A violating caller exits 70 (internal error). I checked this with `a/b`, `*.pyc`, `x?` and `[ab]`.
- **`exclude_hits <root> <names…>`** lists every path under `root` whose name is excluded, without
  descending into a match. It uses `find "$root/." -mindepth 1 \( -name … \) -prune -print0`, so a
  symlinked root is scanned like a real directory.
  - The output goes to a temporary file, not a pipe. If `find` fails, the run stops instead of
    treating the failure as "no hits".
  - The result is returned in `EXCLUDE_HITS`, because bash functions cannot return arrays.
- **`copy_contents_excluding <src> <dest> <hits…>`**:
  - **With no hits** it runs exactly the old `cp -r "$src/." "$dest/"`.
  - **Otherwise** it copies entry by entry and never copies a hit. It descends only into directories
    that contain a hit, so any subtree without one is still copied in a single `cp`.
  - Entries are listed with a sorted `dotglob`/`nullglob` glob, and the caller's shell options are
    restored afterwards.
- **`copy_tree_into` fallback** is now `exclude_hits src` followed by `copy_contents_excluding`. The
  old loop that removed each excluded path after copying is gone. That loop was what deleted the
  target's own copy.
- **`sync_tree_into` fallback:**
  1. It backs up the destination's own hits at **any** depth. Top-level hits come first, in the
     caller's order, so the old command sequence is unchanged when nothing is nested.
  2. It removes the destination and copies the source **minus its hits**.
  3. It restores the backups, as before.
- **The `rsync` branches are unchanged.** The stale comment in `install_mcp_server_runtime` said
  `_index/` "is never present in `$IMPLEMENTATION`"; it now says why that is false.

## 3. Proof that the copiers agree

- **Differential fuzz** (one-off; not committed):
  - It extracts the tree-writer functions from `install.sh` and sources them with a trivial `run`.
  - It builds random source and destination trees. These include excluded names at depth 0–3,
    dotfiles and dangling symlinks.
  - It runs `copy_tree_into` and `sync_tree_into` under real `rsync` and under the fallback, and
    compares the resulting trees: kind, bytes and link target.
  - Destination files are aged so that `rsync`'s size-and-mtime quick check does not mask a
    difference.
  - Destination paths whose type conflicts with the source (a file on one side, a directory on the
    other) are removed first. That is a separate difference between the copiers (§8.2).

  | Copier | `HEAD` | Now |
  |---|---|---|
  | GNU coreutils/findutils, host | 1268 / 2000 mismatch | **0 / 2000** |
  | busybox `cp`/`find` (`python:3.12-alpine` with `rsync` added for the comparison) | — | **0 / 2000** |

- **Tests:**
  - `tests/functional/test_install_exclude_parity.py` is new and has 7 tests, each run under both
    copiers as subtests.
  - `test_update_ships_no_source_pycache_with_cp_fallback` is now a normal test; I removed its
    `@unittest.expectedFailure` and it passes on its merits.
  - **On `HEAD`, swapped in place, on the host:** 15 tests ran with `failures=9, errors=2`. Every
    `cp` subtest fails, plus all four "copiers agree" subtests; every `rsync` subtest passes.
  - **On `HEAD` in the alpine image:** `failures=5, errors=2, skipped=2`.
  - **Now:** all pass, both on the host and in the alpine image. In alpine, 73 tests across the five
    installer test modules gave `OK (skipped=6)`. The skips are the `rsync`-only subtests.

## 4. Every other invocation is unchanged

This is the T552 method. A one-off harness records each invocation's exit code, its normalised
stdout and stderr, and every target path's kind, sha256 and mode. It covers 43 invocations: 21 per
copier plus `--help`.
- a fresh install for each of the 8 platforms;
- a fresh `--dry-run`;
- `--update` with `all`, with `pi`, and with `--dry-run`;
- `--projections-only` with `all` and with `pi`;
- the `--update --projections-only` exclusivity error;
- a plain re-install over an installed project;
- at a synthetic root: a plain install, `--update`, `--update --dry-run`, and `--projections-only`
  with `all` and with `pi`.

The installer ran **in place** from the worktree, so `REPO_ROOT` is the worktree. The seed project
was made once, by `HEAD`, and has its own `settings.json`, `workflows/` and `.cursor/mcp.json`. The
source contained no `__pycache__/` or `_index/`.

| Comparison | Identical | Differing |
|---|---|---|
| `HEAD` vs `HEAD` (determinism control) | 43 / 43 | — |
| `HEAD` vs this change | **41 / 43** | stdout of `cp:fresh-dry-run` and `cp:update-dry-run` only |

**Why the two `--dry-run`s differ.** Five platform trees ship a top-level excluded config:
`.cursor`, `.gemini`, `.opencode`, `.pi` and `.cline`. For those trees the fallback's echoed plan
changes:
- **Before:** `cp -r <src>/. <dest>/`, then `rm -rf <dest>/mcp.json` and the same for the sidecar.
- **Now:** one `cp -r <src>/<entry> <dest>/` per remaining entry.

Nothing is written in either version. Under `rsync` the two versions agree on all 21 invocations,
and within each version `rsync` and `cp` write identical trees (kind and bytes) on all 21.

**Deliberate changes**, all confined to the `cp` fallback, and all of them move it to what `rsync`
already did:
- the source's excluded paths are no longer shipped (§1);
- the target's own nested excluded paths are kept;
- a plain re-install no longer deletes the target's own `_index/` or `__pycache__/`;
- a caller passing a non-literal exclude now exits 70. No caller does.

**Cost.** A fresh `--platform all` install under the `cp` fallback takes about 255 ms, against
189 ms on `HEAD` (3 runs each). The difference is the `find` scans.

## 5. Audit of every exclude-bearing call

| Call | Excludes | `cp` fallback before | Now |
|---|---|---|---|
| `install_tree_into runtime/memory` | `_index`, `__pycache__` | **Update:** shipped the source's index and caches (**the leak**); deleted the target's own nested cache. **Install:** shipped the nested cache; deleted the target's own `_index/` and top-level cache. | = `rsync` |
| `install_tree_into runtime/security`, `runtime/handoff` | `__pycache__` | **Update:** shipped the source's cache. **Install:** clean (no nested cache in these trees today). | = `rsync` |
| `.cursor`, `.pi`, `.cline` | `mcp.json` + sidecar | Update shipped the source's config into a target that had none. **Masked:** `merge_or_copy_mcp_json` writes it right after. Measured: with the configs deleted from the target, `rsync` and `cp` leave identical config bytes on `HEAD` as well. | = `rsync` |
| `.gemini`, `.opencode` | `settings.json` / `opencode.json` + sidecar | Same as the row above: masked by the merge step. | = `rsync` |
| `.claude` | `settings.json`, `settings.local.json` | The source has neither, so nothing leaked. **Update:** a target's own **nested** copy (for example in a retired skill directory) was deleted. | = `rsync` (tested) |
| `.github` | `GITHUB_LOCAL_PATHS` (9 names) | Same as `.claude`: a nested `workflows/` in a retired directory was deleted. | = `rsync` (tested) |
| `.clinerules` | none | — | unchanged; same command |
| `copy_tree_into docs` (fresh install) | none | Ships `docs/**/__pycache__/` under **both** copiers. This is not exclude asymmetry (§8.1). | unchanged |
| `merge_tree_preserve_existing docs/<sub>` (`--update`) | none | `rsync --ignore-existing` and `cp -rn`: no exclude asymmetry. Ships `__pycache__/` in any `docs/<sub>` other than `tasks/` under both copiers (none exists today). | unchanged |
| `merge_task_docs` (`--update`) | — | Copies top-level files only, so no cache directory. | unchanged |

**Any-depth matching withholds nothing that ships today.** No tracked source file at depth 2 or
more carries an excluded name. Every such match in the source trees is either top-level or a
gitignored `__pycache__/`/`_index/`.

## 6. `.gitignore`-aware defence in depth: argued, not implemented

**The case for it.** Git excludes these files from the repository, yet the installer still reads
them from the working tree. A filter keyed on `.gitignore` would also catch §8.1, and any future
build artefact that nobody remembered to add to an exclude list.

**Why not now:**
1. **It needs `git`.** Exact `.gitignore` semantics (negation, anchoring, `**`, nested
   `.gitignore` files) mean `git check-ignore` or `git ls-files`. Reimplementing them in bash is not
   credible. The installer can also run from a source that is not a git checkout, such as a tarball,
   an archive or a `git archive` extraction, or on a host without `git`.
   So there would be two behaviours, "git available" and "git absent", and the files written would
   depend on the host. That is exactly the rsync-versus-cp problem this task removes.
2. **It changes other invocations.** Every install from an authoring checkout with ignored files
   would change, for example `docs/tasks/__pycache__/` would stop shipping. The brief rules that out
   for this task.
3. **Tracked-only is the stronger form, and it is a policy decision.** Shipping only
   `git ls-files` output is effectively an allowlist. It would need a defined answer for non-git
   sources, which is really a release-packaging question.

**Recommended instead, cheap and host-independent:**
- **(a)** Add `__pycache__` to the `docs/` copies (§8.1). This is a one-line change to the
  `copy_tree_into` call, plus an exclude parameter for `merge_tree_preserve_existing`.
- **(b)** Optionally, run a post-install tripwire. It would fail the run if any `_index/` or
  `__pycache__/` exists in a shipped tree of the target that was not there before. It detects
  rather than filters, so it needs neither `git` nor a pattern language.

## 7. Defects in the brief

1. **"The fresh-install path is not affected."** This is wrong for nested excludes. `copy_tree_into`'s
   fallback removed only top-level excluded paths, so a fresh install without `rsync` from an
   authoring checkout ships `runtime/memory/context_retriever_mcp_server/__pycache__/`. That
   directory exists in the main checkout, and its `server.cpython-312.pyc` contains the absolute
   path `/home/emage/Code/emage/emage.code/…`. The same fallback also deleted a target's own
   `_index/` on a plain re-install (§1). I fixed it in the same change, because the two fallbacks
   now share one helper, and I flag it here as a scope expansion.
2. **`install.sh`'s own comment** said `_index/` "is never present in `$IMPLEMENTATION`". The brief
   is right on this point and the comment was wrong. I corrected the comment.

## 8. Findings not fixed here

1. **Minor, security: `docs/tasks/__pycache__/` ships on a fresh install under both copiers.**
   `copy_tree_into "$IMPLEMENTATION/docs" "$TARGET/docs"` passes no excludes. The main checkout has
   `implementation/docs/tasks/__pycache__/validate-tasks.cpython-312.pyc`, which contains no `/home`
   path; its source is shipped anyway. On `--update`, `docs/tasks` goes through `merge_task_docs`,
   which copies files only. Any other `docs/<sub>/__pycache__/` would ship on `--update` too.
   Measured with planted synthetic caches: `docs/plans/__pycache__` and `docs/tasks/__pycache__` both
   ship under `rsync` and under `cp`. Fix: §6(a). Not done, because it changes the `rsync` path and
   is not exclude-parity.
2. **Pre-existing: type conflicts.** When the target has a directory where the source has a file,
   or the reverse, or a symlink in the target where the source has a file, `copy_tree_into`'s `cp`
   fallback fails (`cannot overwrite directory`). `rsync` replaces the path instead.
   - Fuzz with conflicts left in, 300 cases: 26 `copy_tree_into` runs where `rsync` succeeds and
     `cp` exits 1. On `HEAD` there were 58.
   - In 1 case `cp` wrote **through** a destination symlink. That is a pre-existing `cp -r` hazard.
   - `sync_tree_into` now agrees with `rsync` on success or failure in every conflict case. It fails
     only where `rsync` also fails (exit 23). There `HEAD` "succeeded" by silently dropping the
     protected path.
   - All of these are out of scope. The failures are loud, not silent.
3. **Metadata.** The `cp` fallback does not preserve modes or mtimes the way `rsync -a` does (T550
   §5.5, inherited). Directories created to descend towards an excluded path get the umask mode
   rather than the source directory's mode.
4. **Parked P17 and P18** (plan-085 §3) are untouched.
