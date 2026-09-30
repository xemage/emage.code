# T552 — `install.sh --update` at the repository root, and self-copies anywhere, v1

**Based on:** `docs/tasks/task-T552.md`; `docs/plans/plan-084-round-close-and-fired-triggers.md` §2–§3;
`docs/artifacts/root-refresh-mode-v1.md` (T550) §1, §5.1, §5.3, §5.4; `scripts/install.sh` at `fda6a90`;
`tests/functional/test_install_projections_only.py`.
**Author:** DevOps Engineer. **Date:** 2026-09-30. **Tree measured:** `develop` at `fda6a90`.

## 0. Verdict

1. **`--update` is refused at the repository root**, before anything is written, dry-run included.
   The refusal points to `--projections-only`. This deliberately changes one existing invocation.
2. **Independently, the three tree writers do nothing when source and destination are the same
   directory.** This affects `copy_tree_into`, `sync_tree_into` and `merge_tree_preserve_existing`.
   It fixes the defect class at any target, not only at the root.
3. **The root check now also catches aliases of the root**, such as a symlink to it. Before, the
   string comparison let an alias bypass every root rule.
4. **The inaccurate root warning is gone.** `--update` no longer runs at the root, so there is no
   warning to correct. The refusal says what `--update` would actually have done.
5. **`validate_github_agents` no longer depends on `rg`.** It uses `grep`, and it exits 1 if the scan
   itself fails. Before, a missing `rg` meant the check silently passed.

## 1. Decision 1 — refuse `--update` at the root: yes

At the root, `--update` did three things. None of them was useful, and `--projections-only` does
none of them:

| Step | Effect at the root |
|---|---|
| `merge_task_docs` | Rewrites both task ledgers and drops non-conforming rows. This is the path that took `active-tasks.md` from 2460 lines to 11 in `fee245a`. On the synthetic root it dropped the `T42` row. |
| `merge_tree_preserve_existing` over `implementation/docs/*` | Seeds template files into the repository's own `docs/`. Measured: it re-seeded `docs/tasks/validate-tasks.py`. |
| `install_mcp_server_runtime` | Copies `implementation/runtime/*` onto itself. Under `rsync` this does nothing. Without `rsync` it deletes the source (§4.1). |

Everything else `--update` does at the root is a projection refresh: the eight trees, the MCP
configs, `AGENTS.md` and `CLAUDE.md`. `--projections-only` does exactly that, with the same
semantics (T550 §1). No use case is left for `--update` at the root.

**What changes.** `install.sh --target <root> --update` used to exit 0 under `rsync`, after
rewriting the ledgers and refreshing the harness. Without `rsync` it exited 1 after deleting
`implementation/runtime/memory/`. It now exits 1 with nothing written. The same applies to
`--dry-run`. No script, Makefile target, CI job or document in this repository invokes it; I
grepped `README.md`, both `AGENTS.md` files, `Makefile`, `.gitlab-ci.yml`, `scripts/` and
`implementation/knowledge/`.

**The refusal text** replaces the old warning. The old warning said *"templates will be merged
without overwriting existing docs files"*, which was inaccurate:

    error: refusing --update at the emage.code source repository root:
      <root>
    reason: --update rewrites the task ledgers in docs/tasks/, seeds template files into docs/,
      and copies implementation/runtime/ onto itself -- here docs/ is the repository's own record
      and implementation/ is the source the installer reads.
    use one of the following instead:
      - To refresh the root's own harness projections: scripts/install.sh --target . --platform all --projections-only
      - For repo maintenance: git pull && make sync && make verify
        (these regenerate and check implementation/.<platform>/ only; they do not write the root)

`--help` now says `--update` is refused at the root, and that `--projections-only` is the only
mode permitted there. The old text said "the one mode besides --update".

## 2. Decision 2 — `src` and `dest` are the same directory: a no-op in all three tree writers

**Check.** `same_tree` checks `[[ -d src && -d dest && src -ef dest ]]`, that is, the same device
and inode. It therefore sees through symlinks, `.`, relative spellings and bind mounts. A plain
string comparison would miss `--target .`, because `$TARGET` is used unresolved in the destination
paths.

**No-op, not refusal.**
- When `dest` *is* `src`, "make `dest` match `src`" is already true. A no-op is the correct result,
  not a workaround.
- It is also what `rsync` already did with such a call. The two copiers now agree.
- A refusal would turn a harmless `rsync` self-sync into a failure. That failure would come in the
  middle of a run, after earlier steps had already written.

A single stderr line, `note: <dest> is <src> itself; nothing to copy.`, makes the skip visible.

**Why all three writers, not only `sync_tree_into`.**
- `copy_tree_into`'s fallback runs `cp -r src/. dest/`. GNU `cp` refuses a self-copy, so the run
  exits 1. If a `cp` accepted the self-copy, the loop that follows would `rm -rf` each exclude
  "the copy placed", which here means the source's own `_index/`.
- `merge_tree_preserve_existing` is harmless on a self-copy, but it is the same shape. Guarding it
  costs one line.

**Where it matters beyond the root.** Consider a target whose `implementation/runtime` is a symlink
to the installer's own. That is a plausible development setup. Its runtime destinations are then
the installer's runtime sources.

| Scenario | `HEAD` | Now |
|---|---|---|
| Symlinked runtime, `--update`, `cp` fallback | exit 1; the **installer's own** `implementation/runtime/memory/` went from 22 files to 0 | exit 0; source untouched |
| Symlinked runtime, plain install, `cp` fallback | exit 1 on `cp: … are the same file`; nothing deleted | exit 0; source untouched |
| Either case under `rsync` | source untouched | same result, plus the `note:` line |

Both decisions are kept, and each covers a gap in the other:
- The refusal (Decision 1) is the only one that stops the ledger rewrite at the root.
- The guard (Decision 2) is the only one that protects a non-root target.

## 3. `validate_github_agents` without `rg`: fall back to nothing, use `grep`, fail loudly

**Before.** `if rg -q '^name:' …` inside an `if` turned "`rg` not installed" (exit 127) into "no
match". On every host without ripgrep, the v6.0.5 `name:` check passed without having checked
anything. CI's `python:3.12-alpine` image is one of those hosts.

**Now.** A helper, `source_matches`, runs `grep -rq -e <pattern> <path>` and keeps grep's three
outcomes apart:
- `0`: match;
- `1`: no match;
- anything else: **exit 1**, with `could not scan … refusing to run --update unchecked`.

**Why not an `rg`-then-`grep` fallback.** `grep` is POSIX and in busybox. The function already
called it unconditionally for its second check. One tool means one behaviour on every host.

**Result on today's source.** `rg` and `grep` agree: both exit 1 (no match) on
`implementation/.github/agents`, which has no hidden files that `rg` would have skipped.

The second check, the orchestrators' `agents:` list, goes through the same helper. It had the same
silent-on-error shape.

## 4. Proof — synthetic roots only

This repository's root was never used as a target.

- **Root cases.** A synthetic repository is a stale installed root with `scripts/` and
  `implementation/` copied in. Its own installer runs against its own root, which is the real
  root code path (T550 §4.2).
- **The one-off measurements** used `git archive` extractions, which only read objects.

`HEAD` was compared with the new file by **swapping `scripts/install.sh` in place** in the worktree,
and never by copying it elsewhere. Every swap was restored, and its sha256 was verified afterwards.

### 4.1 The defect reproduces on `HEAD`

`git archive HEAD` extracts a full copy, and that copy's own installer runs with
`--target <copy> --platform all --update`, with `rsync` genuinely absent from `PATH`:
- exit 1;
- `cp: '…/implementation/runtime/memory/.' and '…/implementation/runtime/memory/.' are the same file`;
- `implementation/runtime/memory/` went from 22 files to 0;
- `security/` (6) and `handoff/` (3) were not reached.

The abort came after `merge ledger …/active-tasks.md` and `…/completed-tasks.md`, as T550 reported.

### 4.2 `tests/functional/test_install_update_root.py` (new, 10 tests)

Each behavioural test runs under `rsync` and under the `cp` fallback, as subtests:

- **`--update` at the synthetic root is refused.**
  - Exit 1, and the refusal names `--projections-only`.
  - No `merge ledger` line appears.
  - Every file in the repository keeps its bytes, mode **and mtime**.
  - `runtime/memory` and `runtime/security` keep their file counts.
- The same holds for `--update --dry-run`, and for `--update` through a **symlink alias** of the
  root.
- `--projections-only --platform pi` through an alias is refused as at the root, and nothing is
  written.
- **Self-copy is a no-op at a non-root target** whose `implementation/runtime` is a symlink to the
  installer's own. Under `--update` and under a plain install:
  - exit 0;
  - the `note:` line appears;
  - the installer's whole `implementation/` keeps bytes, mode and mtime.
- **`name:` corruption is caught without `rg`.**
  - With `rg` and `rsync` removed from `PATH`, an injected `name:` key exits 1 before the target is
    touched.
  - With `grep` removed, the run exits 1 with `could not scan`.
  - The clean source still updates with `rg` absent. This is the non-vacuity control.
- `--help` states the refusal.

**On `HEAD`**, swapped in place, the file has **13 failing subtests** and 1 passing test (the
control). Every refusal test fails because `HEAD` proceeds. Under `cp` it wrote the ledger and then
failed at the self-copy, and under `rsync` it rewrote the ledger. Both `rg` tests fail because
`HEAD` proceeds with exit 0.

The `rsync` variants of the symlinked-runtime tests fail on `HEAD` **only** on the missing `note:`
line: `rsync` never destroyed anything there. Their `cp` variants fail on the data.

### 4.3 Every other invocation is unchanged

This is a one-off harness (`record`/`diff` over exit code, normalised stdout and stderr, and every
target file's sha256 and mode). It covers 41 invocations, 20 per copier plus `--help`:

- a fresh install for each of the 8 `--platform` values, and a fresh `--dry-run`;
- `--update` with `all`, `pi` and `--dry-run` on a stale seeded project;
- `--projections-only` with `all` and `pi`;
- the `--update --projections-only` exclusivity error;
- at a synthetic root: a plain install, `--update`, `--update --dry-run`, `--projections-only`
  with `all`, and with `pi`.

The seed project was made once, by `HEAD`, and shared by both runs.

| Comparison | Identical | Differing |
|---|---|---|
| `HEAD` vs `HEAD` (determinism control) | 41 / 41 | — |
| `HEAD` vs this change | **36 / 41** | `--help`; root `--update` and root `--update --dry-run`, each under both copiers. All deliberate. |

The root `--update` difference, measured:
- **`HEAD` `cp`:** exit 1. 22 `runtime/memory` files were lost, `active-tasks.md` and `AGENTS.md`
  rewritten, and `validate-tasks.py` seeded.
- **`HEAD` `rsync`:** exit 0. `active-tasks.md` was rewritten, `validate-tasks.py` seeded, and 12
  harness paths refreshed: 8 rewritten, 1 restored, and 3 removed-upstream files deleted.
- **Now:** nothing written, under either copier.

In the synthetic-root rows, the installer under test is itself a file of the repository. It is
excluded from the file comparison because it differs by construction and is never written by the
run.

## 5. Interaction with T553

T553 adds `runtime/handoff/` as a third `install_tree_into` in `install_mcp_server_runtime`, in the
next commit on the same branch. Either layer alone keeps it out of the data-loss path:
- the root refusal means `install_mcp_server_runtime` is never reached at the root;
- the self-copy guard covers every other `src == dest` spelling.

T553's own test proves that `runtime/handoff/` survives both.

## 6. Findings not fixed here

1. **Minor: `--target <repo>/implementation --update` still writes the source.**
   `implementation/AGENTS.md` exists, so `require_existing_install` passes. The run then:
   - re-renders `implementation/AGENTS.md` over itself;
   - creates `implementation/implementation/`;
   - exits 1 at `cp CLAUDE.md` onto itself.

   **Before this change**, the `cp` fallback also deleted the `implementation/.cursor/` source
   projection first. The guard now stops that; measured on a `git archive` copy, 29 differing
   paths became 2.

   Suggested follow-up: refuse any target that is `-ef` `$IMPLEMENTATION`, the same way the root
   is refused. It is not done here because it changes another invocation that the brief does not
   name.
2. **`--update`'s `--help` text says an existing ledger "is never rewritten beyond its task rows".**
   Read narrowly this is accurate: the dropped non-conforming rows are table rows. But the file is
   still rewritten, including its trailing newline (T550 §5.3). Left unchanged: not at the root,
   and not in the brief.
3. **Inherited `cp` fallback metadata loss (T550 §5.5)** is unchanged.
