# Artifact: security-review-t684-installer-hardening-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test, mutation or installer run; the `grep_content` tool failed, files read directly). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-22.
- **Target**: T684, branch `agent/devops-engineer/T684` (from develop `b78b8e0a`), commit `f8cbdb8f`: the three deferred findings of `security-review-t682-installer-residuals-v1.md` (SEC-T682-03, -04, -06): the stale-swap-sibling display and hint (`shell_quote_ascii`, `[ ! -e DEST ] && mv -- OLD DEST`), the physical, case-folded overlap check including `mcp.outputFile` and its sidecar (`physicalFolded`, `mcpFiles`, async `assertNoOverlappingTargets`), and `merge-task-docs.py` plan-then-write with atomic `mkstemp`/`fchmod`/`os.replace` writes for ledgers, backups and seeds.
- **Based on**: `docs/tasks/task-T684.md`, `docs/artifacts/security-review-t682-installer-residuals-v1.md`.
- **Orchestrator checks**: the full suite on the merged tree is recorded in the task outcome; the developer's mutation log (`scratchpad/mutations-t684.txt`; first-run survivors T03c, T03c2, T04k, T06g strengthened and killed; T04j reported equivalent, see SEC-T684-06) was judged credible by the reviewer, not re-run.

## Verdict: CONDITIONAL_PASS (0 critical, 0 high, 0 medium, 6 LOW new)

SEC-T682-03, -04 and -06 are closed in substance. The pasted hint is safe against newline, quote, `$()`, backtick, bidi and non-UTF-8 bytes (every operand is a `%q` data token, the `[ ! -e ]` guard makes a second paste a no-op, `local LC_ALL=C` does not leak because both helpers run inside `$(...)`); the overlap check runs once, awaited before any write, fails closed on every error other than ENOENT/ENOTDIR and has no false positive for the six real manifests (reading; the suite is the developer's claim); `merge-task-docs.py` decodes everything first, orders backups ahead of ledgers, and leaves each file old or new after a process failure; the new message ("each ledger is either unchanged or fully replaced") does not overclaim. No Immutable Security Constraint is breached and no control is weakened.

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T684-01 | LOW | `physicalFolded` follows a dangling link with a lexical `dirname` (`sync.mjs:944`): a dangling `../` link behind a symlinked parent can land in the wrong place; fix: `path.resolve(await fs.realpath(path.dirname(current)), link)` | tracked debt (register v2) |
| SEC-T684-02 | LOW | `mcp.outputFile` is guarded by a deny-list of inputs only: it is not compared with the removal trees of other manifests nor with other files under ROOT; fix: an allowlist (under the manifest's own `outputDir` plus the exact exceptions `../.mcp.json` and `../.vscode/mcp.json`) or a comparison with all removal trees and between mcp files | tracked debt |
| SEC-T684-03 | LOW | the locale-dependent `printable` still shows target-controlled names (readlink targets, managed paths, sibling names) at `install.sh:279-281` and its uses; U+202E passes `[:print:]` in a UTF-8 locale; fix: `printable() { ascii_printable "$1"; }` after checking no test expects a UTF-8 character to survive | tracked debt |
| SEC-T684-04 | LOW | no `fsync` of the temp file or the directory in `_atomic_write_bytes`: "backup ahead of ledger" holds for a process kill, not for a power loss | tracked debt |
| SEC-T684-05 | LOW | seeds are published with `os.replace` and can clobber a file created between planning and writing; `dest_dir.mkdir` runs before the dry-run guard (both pre-existing) | tracked debt |
| SEC-T684-06 | LOW | test and mutation accuracy: T04j (hop limit removed) is not strictly equivalent (a 41-link dangling chain distinguishes it; add a test); no non-UTF-8 name bytes test; bash 3.2 `%q` behaviour and the installer's minimum bash version unverified; the `mode_before == 0o600` assertion in the temp-file mode test cannot fail (use a ledger mode other than 0600) | tracked debt |

## Unverified

Runtime behaviour on macOS or busybox (`printf %q` under `LC_ALL=C` on bash 3.2), case-insensitive or normalising file systems, hard links and bind mounts (documented limits of the overlap check), concurrent installers, whether `install.sh` ever calls `merge-task-docs.py -n` on a missing directory, the `opencode` manifest (not read for false positives).
