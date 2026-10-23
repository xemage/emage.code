# Artifact: security-review-t677-function-size-refactor-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test, hash comparison or installer run; the base was read in `/home/emage/Code/emage/emage.code`). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-23.
- **Target**: T677 (function-size refactors, TL-T649-01 and TD-T671-FN1), branch `agent/devops-engineer/T677` (from develop `eb692776`), commits `66326404` and the clean merge `7870ad70` of develop `f9001692`: `sync.mjs` (`emitMcp` 134 to 8 lines via a `MCP_EMITTERS` map, `syncPlatform` 131 to 18, `parseServersYaml` 68 to 33, `main` 53 to 16), `merge-mcp-json.py` (`_main` 101 to 43; `build_parser`, `refuse_bad_paths`, `prune_retired_servers`, `force_prune`, `report_and_write`; `merge_json` loses its private `_top` parameter), `verify-release-docs.py` (`main` 63 to 38), `render_installed_agents.py` (`render` 91 to 20), `install.sh` (`replace_tree_by_swap` 53 to 41 with the new `swap_build_into_place`; `usage` allowlisted), and the guard `tests/functional/test_function_size.py`.
- **Based on**: `docs/tasks/task-T677.md`, `docs/artifacts/tracked-debt-register-v1.md` (TL-T649-01, TD-T671-FN1).
- **Orchestrator checks**: the full suite on the merged tree is recorded in the task outcome. The developer's equivalence evidence (not reproduced by the reviewer): all 764 generated files hash-identical between old and new `sync.mjs`; old and new `install.sh` compared on 7 platforms x {fresh, `--update` over edited configs, `--projections-only`, `--update --dry-run`, invalid option, corrupted MCP JSON}, with and without rsync, with identical normalised stdout/stderr/exit codes/tree hashes; `verify-release-docs.py` identical on 5 synthetic states; 8 of 9 mutations of the refactored code caught.

## Verdict: PASS (0 critical, 0 high, 0 medium, 3 LOW)

No control added in T662-T685 is omitted, removed, disabled or weakened. Verified by reading: the order of operations in `install.sh` (the swap helper is called as a plain statement, not in a subshell, so `SWAP_OLD`/`SWAP_DEST`/`SWAP_DONE` are set in the main shell before the first rename and `refuse_unsafe_path` stays in the caller); `merge-mcp-json.py` (validation before any write, symlink refusal, atomic write, sidecar ordering, the force-prune refusal, escaped names; `merge_json` has no caller passing `_top`); `sync.mjs` (every validation still runs before the first write and in `--check`; an unknown MCP format still throws; placeholder-only secret handling, `secret`/`optional`/`skipFormats`/`denyTools`/`excludeTools`/Opencode permission denies unchanged); `verify-release-docs.py` (the three extracted checks hold the old blocks verbatim, called in the old order); `render_installed_agents.py` (identical six substitutions, no silent skip).

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T677-01 | LOW | the size guard cannot see some function shapes (Bash `function name {`, `name () {`, brace on the next line; JS arrow functions, class methods, nested/indented functions; a column-0 `}` inside a heredoc or template literal ends a function early; a redefined Python name hides the earlier body); it only asserts more than 3 functions per file | tracked debt (register v2); use a real parser (`bash -n`/shfmt, acorn) or extend the shapes and fail on an unclosed or duplicate function |
| SEC-T677-02 | LOW | no test pins that `verify-release-docs.py` `main` still calls `check_section_requirements` (a pre-existing gap), nor that an interrupted swap sets `SWAP_*` before the first rename through the new helper | tracked debt; add mutation-style tests |
| SEC-T677-03 | LOW | `usage` is allowlisted as "no logic" but contains one command substitution (`join_bar`) | tracked debt; reword the reason or split the dynamic line into a helper |

INFO: `SHIPPED_TOOLING` covers six files by design (the runtime is TD-T671-FN2, accepted debt); a 12-line placeholder-form comment block in `sync.mjs` is indented two spaces between the emitter header and `emitMcpVscodePi` (cosmetic).

## Unverified

The "764 identical files" and the 7-platform installer comparisons are the developer's claims; whether `test_function_size.py` runs in the CI pipeline; non-Python callers of `merge_json`; the files the two commits touched beyond the diff read.
