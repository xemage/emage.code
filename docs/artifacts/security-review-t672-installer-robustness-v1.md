# Artifact: security-review-t672-installer-robustness-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test, mutation or install run; files read at the worktree tip). Recorded by the orchestrator from the reviewer's two reports (first review, delta re-review).
- **Gate**: security. **Date**: 2026-10-22.
- **Target**: T672, branch `agent/devops-engineer/T672` (from develop `5dfd12fa`): installer and generator robustness (tracked debt): `scripts/install.sh`, `scripts/merge-mcp-json.py`, `scripts/merge-task-docs.py`, `implementation/scripts/sync.mjs`, `generate-registry.py`, `implementation/platforms/_manifest.schema.json`. Reviewed tips: `6fb858ee` (first review), fix commit `1d81dea5` (delta).
- **Based on**: `docs/tasks/task-T672.md`, `docs/artifacts/tracked-debt-register-v1.md` (SEC-T658-05/-07b, TL-T649-02/-03/-04/-06/-08, QA-T648-02, SEC-T662-03/-07, SEC-004..010, SEC-015, TD-T671-P8).
- **Orchestrator checks**: the full suite on the tip `41075955` was re-run by the orchestrator: 1611 tests OK (skipped 23); the developer's mutation log (69 entries, 68 killed, 1 equivalent survivor N13b: `validate_existing_mcp_configs` also exits 70 before any write) is in `scratchpad/mutations-t672-final.txt` and was judged plausible by the reviewer, not re-run.

## First review: CONDITIONAL_PASS (0 critical, 0 high, 1 medium, 11 low)

| Id | Grade | Finding | Disposition (delta review) |
|---|---|---|---|
| SEC-T672-01 | MEDIUM | the replacement temp file of both merge scripts held merged config (user `env` tokens, `headers`) at 0666 minus umask, with a predictable name, until it was chmod-ed | fixed: `mkstemp` (random name, 0600), `fchmod` to the old file's mode before any byte is written, unlink on failure; test asserts an empty file at `fchmod` time; CLOSED |
| SEC-T672-02 | LOW | `swap_cleanup` left the old tree after an interrupt following the second rename; HUP/QUIT not trapped | fixed (restore only if dest is missing, discard otherwise; HUP/INT/QUIT/TERM 129/130/131/143; scan files removed); CLOSED |
| SEC-T672-03 | LOW | predictable swap sibling names with a check-then-create window | fixed (`mkdir --` atomic, both siblings refused when pre-existing, `old` re-checked before the first rename); CLOSED, residual N-3b |
| SEC-T672-04 | LOW | the fail-closed claim held for one of the three per-platform maps | fixed (`verify_platform_maps` in the main shell before any write); CLOSED |
| SEC-T672-05 | LOW | help text overclaimed the replaced-value notes | fixed (help lists exactly what is noted; non-object top level noted); CLOSED |
| SEC-T672-06 | LOW | a plain install now merges, so retired entries survive when there is no sidecar | fixed (stderr note naming the kept servers, with a pointer to `--force-prune-keys`); CLOSED; migration line goes into the v9.0.0 notes (T679 brief) |
| SEC-T672-07 | LOW | atomic-write robustness gaps (traceback, NaN, writability) | fixed; CLOSED |
| SEC-T672-08 | LOW | `sync.mjs` did not validate manifest paths at runtime | fixed (`assertUnderRoot` over outputDir, mcp.outputFile, extras.to/from, fileMap dirs; schema `relPath`); CLOSED, residuals N-4..N-6 |
| SEC-T672-09 | LOW | `splitInlineArray` read some YAML forms differently | fixed (trailing comment, indicator characters); CLOSED |
| SEC-T672-10 | LOW | any `_*.json` in `platforms/` skipped silently | fixed (only `_manifest.schema.json` is skipped); CLOSED |
| SEC-T672-11 | LOW | test gaps (vacuous assertions, uncovered branches) | fixed; mutation log produced; CLOSED |
| SEC-T672-12 | LOW | the swap reset the tree root mode | fixed (old mode, go-w stripped); CLOSED, regression N-2 |

## Delta re-review: PASS

No ordering regression from moving the main-flow block below the function definitions; nothing is written before the checks; dry-run still creates nothing; the user's tree is never deleted before the new one is in place. New LOW items, tracked as T682:

| Id | Grade | Finding |
|---|---|---|
| T672-N-1 | LOW | `merge-mcp-json.py` prints user-file key, server and permission names unsanitised (terminal injection from a third-party project file) |
| T672-N-2 | LOW | availability regression: the old directory's mode is applied to `$build` before the copy, so a 555/500/600 destination makes `cp` fail; apply the mode after the copy |
| T672-N-3 | LOW | a second signal while `swap_cleanup` runs from the EXIT trap may cut the cleanup short (unverified); N-3b: `mv -T` for the two renames |
| T672-N-4 | LOW | `sync.mjs` does not normalise an absolute `--root` (`path.resolve`) |
| T672-N-5 | LOW | `assertUnderRoot` only prevents leaving ROOT: `outputDir` of `knowledge`, `platforms`, `_extras`, `scripts` or `runtime` passes and the recursive `rm` would delete generator inputs; overlapping manifest trees are not checked; `extras.from` is asserted against ROOT rather than `_extras` |
| T672-N-6 | LOW | schema `relPath` pattern: `.*` does not cross a newline, `"a\n/../.."` passes the schema (caught at run time) |
| T672-N-7 | LOW | after SIGKILL or power loss between the two renames the tree sits in `<dest>.emage-old.<pid>`; the next run installs fresh and carries over nothing; scan for `*.emage-old.*` / `*.emage-new.*` at start and warn |
| T672-N-8 | LOW | `merge-task-docs.py` `main()` catches only `SymlinkRefused` (traceback on a failed write or invalid UTF-8) |

INFO (not graded): a leftover `.<name>.<random>.tmp` after SIGKILL could be committed by mistake; `--validate-only` requires W_OK on the file itself, so a deliberately read-only (0444) config is refused up front; replacing a file drops its owner, ACL and hard links.

## Unverified

busybox/alpine behaviour of the `cp` fallback and the `stat -f` BSD fallback; the shim-based interrupt tests; the SIGHUP test needs SIGHUP reset to default in the child (done with `preexec_fn`); a stale `<tree>.emage-old.<pid>` after SIGKILL is not detected (N-7); the reviewer matched SEC-T672 ids to fixes by code comments for -05, -06, -09, -10, -11 (theme only).
