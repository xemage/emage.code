# Artifact: security-review-t682-installer-residuals-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test, mutation or installer run; files read at the worktree tip; the `grep_content` tool failed, files read directly). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-22.
- **Target**: T682, branch `agent/devops-engineer/T682` (from develop `84312bb0`): the eight LOW findings N-1..N-8 of the T672 delta re-review. Reviewed tip `ff042baf`; follow-up commit `535b40fe` (SEC-T682-01, -02, -05 and the root guards) was not re-read by the reviewer.
- **Based on**: `docs/tasks/task-T682.md`, `docs/artifacts/security-review-t672-installer-robustness-v1.md`.
- **Orchestrator checks**: the full suite on the merged tree is recorded in the task outcome; the developer's mutation log (`scratchpad/mutations-t682.txt`: first round 57 lines, second round for the follow-up; three initial survivors N3a, N3f, N7d strengthened and killed; one equivalent survivor S02f in the second round) was judged plausible by the reviewer, not re-run.

## Verdict: PASS (0 critical, 0 high, 0 medium, 6 LOW new)

N-1..N-8 are closed: N-1 `printable()` at the three print sites; N-2 mode applied after the copy and `discard_old_tree` restoring owner `rwX`; N-3 `trap '' HUP INT QUIT TERM` at the start of `swap_cleanup` (inherited only by the cleanup commands, intended); N-3b `mv -T` only when `mv --version` says GNU coreutils (fails safe elsewhere); N-4 `path.resolve`; N-5 separator-terminated overlap checks over all manifests before the first write and `extras.from` against `_extras`; N-6 `relPath` regex crosses newlines and has no ReDoS risk; N-7 stale `emage-old/new` siblings refuse in every mode with a copy-paste-safe `%q` hint; N-8 `_preflight` before the first write and a one-line message for OSError/ValueError/RecursionError. No Immutable Security Constraint is breached and no control is weakened.

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T682-01 | LOW | the cleanup could not remove a read-only build tree (left `.emage-new.<pid>`) | fixed in `535b40fe` (`chmod -R u+rwX` guarded by `-d` and `! -L` before the `rm -rf`) |
| SEC-T682-02 | LOW | `swap_cleanup` inferred "the swap is complete" from `dest` existing: a failed second rename with `dest` recreated, or a foreign `old` planted after the check, could delete the user's only old tree (pre-existing weakness, `mv -T` changed its reachability) | fixed in `535b40fe` (explicit `SWAP_DONE`; restore only when `dest` is missing; ambiguous state leaves both trees and prints a note); equivalent survivor S02f documented |
| SEC-T682-03 | LOW | N-7 display and hint: `printable` is locale-dependent; the `mv -- old dest` hint nests if pasted after `dest` was recreated; tests do not paste a hostile name through `bash -c` | tracked: T684 |
| SEC-T682-04 | LOW | N-5 residuals: `mcp.outputFile` and its `.provenance.json` are only constrained to ROOT (a manifest could overwrite a generator input); lexical, case-sensitive comparison, no symlink resolution | tracked: T684 |
| SEC-T682-05 | LOW | `chmod -R` on a symlink argument in `discard_old_tree` | fixed in `535b40fe` (`-d` and `! -L` guard) |
| SEC-T682-06 | LOW | the N-8 message overclaims ("never partly written"); `_preflight` decodes but does not run the merge; `.bak`/seed copies are not atomic | tracked: T684 |

The root-guard gap (permission tests passing vacuously under uid 0) was fixed in `535b40fe` (`needs_non_root` skips).

## Unverified

No suite, mutation or installer run by the reviewer; GNU `chmod -R` behaviour on a command-line symlink; `printf %q` and `[[:print:]]` handling of U+202E in UTF-8 locales; `find` on a non-searchable `dest` in the cp fallback (600/000 old trees end to end); macOS, busybox and uutils behaviour (the non-GNU `mv` path is simulated with a shim); concurrent-installer behaviour; the `gemini`, `opencode` and `pi` manifests were not read for the overlap check. A signal arriving between the second rename succeeding and `SWAP_DONE=1` takes the ambiguous path (both trees left, safe, not self-healing).
