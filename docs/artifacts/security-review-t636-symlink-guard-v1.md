# Artifact: security-review-t636-symlink-guard-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no execute tool; static review). Recorded by the orchestrator from the reviewer's report.
- **Task**: T636 (plan-121 addendum 2): the fix for audit finding SEC-001 (`security-review-release-v8-v1.md`): the installer followed symlinks at managed target paths. Reviewed commit `af30f3f`; the developer fixed L1-L5 in one round (`7434029`), which the orchestrator verified but the reviewer did not re-read.
- **Date**: 2026-10-15.
- **Orchestrator checks on `7434029`**: the original reproduction (scratch target whose `.claude` links to a sibling directory holding a canary) now ends refused with the canary intact and nothing written; `git diff --stat 30ef8ba HEAD` shows only `scripts/` and `tests/functional/` (8 files; no projected file); the held-out isolation test passes; the developer ran `install.sh --target . --platform all --projections-only --dry-run` at a repository root: exit 0, nothing written.

## Verdict: PASS

0 critical, 0 high, 0 medium, 7 low. SEC-001 is fixed for every path the installer writes or deletes at a directly managed location, in every mode (plain, `--update`, `--projections-only`, `--dry-run`); the reviewer found no write-through or bypass of the guard. The expectation change in `test_install_update_root.TestSelfCopyIsANoOp` and `test_install_handoff_runtime` (a target whose `implementation/runtime` is a symlink back to the installer's own source is now refused with exit 1 instead of being a silent no-op) was judged acceptable: it is stricter, data-safe and replaces the T552/T559 protection with an earlier check; `same_tree` stays as a second line of defence.

| ID | Grade | Concern | Disposition |
|---|---|---|---|
| T636-L1 | LOW | The up-front guard omitted `docs/<subdir>` and the other `docs/tasks/*` support files (caught only at the per-site call; "Nothing was written" could be false). | Fixed in `7434029`: `docs_managed_paths` feeds the guard; test for symlinked `docs/<sub>`. |
| T636-L2 | LOW | The refusal message printed `readlink` output raw (terminal injection); `physical_path` printed an empty prefix when `cd -P` failed. | Fixed: `printable()` on every attacker-influenced value; `physical_path` fails closed; tests. |
| T636-L3 | LOW | `same_tree` was unreachable by any test. | Fixed: a test asserts the three call sites and exercises the function in a bash harness. |
| T636-L4 | LOW | Test coverage narrower than the guard; layers masked each other; partial writes undetected. | Fixed: the matrix is driven from the single list the guard uses (about 60 paths) with sentinels; a link whose target is inside the target is refused. |
| T636-L5 | LOW | A behaviour change not documented in `--help` (any symlink at a managed path is refused, even one pointing inside the target; previously `CLAUDE.md` -> `AGENTS.md` overwrote `AGENTS.md`). | Fixed: `usage()` sentence and a pinning test. Goes into the v8.0.0 notes. |
| T636-L6 | LOW | The Python checks are final-component `is_symlink()` without `O_NOFOLLOW`; ancestors are covered by `install.sh` only. | Accepted; documented. |
| T636-L7 | LOW (accepted residual) | TOCTOU between the guard and the writes; matters only if the installer runs under `sudo` into a shared tree. | Accepted; `usage()` says not to run the installer as root into a directory others can write to. |

Not verified by the reviewer: test results, real `rsync`/`cp` behaviour (BusyBox `cp` and `rsync --ignore-existing` for the `merge_tree_preserve_existing` fallback), the diff scope (verified by the orchestrator above).
