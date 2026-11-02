# Artifact: security-review-t722-t725-batch-a-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer. The review was read-only: the reviewer had no shell and read the source diff from a file the orchestrator exported. The orchestrator recorded this artifact from the reviewer's report.
- **Gate**: security. **Date**: 2026-11-02.
- **Target**: T722, T723, T724 and T725 (LOW batch A, plan-128) on `docs/plan-128-batch-a` at `7c73b51b`.
- **Based on**:
  - `docs/tasks/task-T722.md` to `task-T725.md`
  - `docs/plans/plan-128-batch-a-installer-generator.md`
  - `docs/artifacts/tracked-debt-register-v4.md` (batch A)
  - the changed files: `implementation/scripts/sync.mjs`, `scripts/install.sh`, `scripts/merge-task-docs.py`, `scripts/merge-mcp-json.py`, `implementation/knowledge/mcp/servers.yaml`, and the `context_retriever` modules under `implementation/runtime/memory/`

## Verdict: PASS

- There is no CRITICAL, HIGH or MEDIUM finding.
- No Immutable Security Constraint is breached.
- No required control is removed or weakened. Each changed control (C1 to C18) is either stricter than before, or new and failing closed.
- The PASS holds because the nine LOW findings below are tracked as debt. This artifact is the record of that tracking; the next register version takes them over.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 9 | 0 | 9 (tracked, section 3) |

## 1. Rulings on the changes

- **T725, the `audience:` filter.**
  - **The generator requires `audience:`.** It refuses a missing or unknown value before any write (`sync.mjs:1156-1174`).
  - **The installer validates the `authoringOnly` list before its first write.** An entry must be a list item made of `[A-Za-z0-9._-]` path components and contain no `..` (`install.sh:1490-1522`). The check also runs in a dry-run, and it fails closed when `python3` is missing.
  - **Each `rm -f` is guarded.**
    - `refuse_unsafe_path` runs first, and `--` comes before the path (`install.sh:1526-1537`).
    - A symlink anywhere below `$TARGET` is refused, and containment is checked against the physical path.
    - A symlinked tree is refused before any write.
    - A dry-run removes nothing.
  - **The authoring-checkout test** is `-f $TARGET/implementation/registry/index.json`. The installer never creates that file in a target, so a normal target is never mistaken for an authoring checkout. A hostile or odd target can only switch the filter off, which writes and deletes nothing.
- **T722.**
  - **K5:** the index directory is derived from the git remote. The slug is one plain path component (`^[a-z0-9][a-z0-9._-]{0,199}$`), so it cannot traverse. If the remote is missing or cannot be read, the server does not start (fails closed). Removing the hard-coded name also ends the default of sharing one index across projects.
  - **SEC-T684-02:** `mcp.outputFile` is now allowed only under its own `outputDir` or at the two root files, which is strictly narrower than before. `assertMcpFilesApart` adds a collision check.
  - **SEC-T684-01:** a dangling link behind a symlinked parent is resolved from the physical parent; if the parent cannot be resolved, the generator refuses. Residual: SEC-T722-01.
  - **SEV-T690-01:** the denials now include servers selected through `extraPlatforms`, and they stay in place under `skipFormats`.
  - **SEV-T690-06:** a grant for a server the platform does not carry is dropped, and the agent then gets the whole-server deny. Residual: SEC-T722-03.
- **T723.**
  - `printable` is now byte-wise: under `LC_ALL=C`, every byte outside 0x20-0x7E becomes `?`.
  - The temp file is fsynced before it is published, and its directory after.
  - The publish never overwrites an existing name (`os.link`). The fallback creates the file with `O_CREAT|O_EXCL|O_NOFOLLOW` and sets the mode with `fchmod` before writing, so the umask has no effect.
  - A dry-run creates no directory.
  - No finding.
- **T724.** The wider `GENERATED_REF` only decides the extra "differs" note. Pruning, and the "pruned" note that names each server, do not depend on it, so it cannot make a hand-edited entry disappear silently. Residual: SEC-T724-01.

## 2. OWASP coverage

| Category | Reviewed | Findings |
|---|---|---|
| A01 Broken Access Control | yes | SEC-T722-03, SEC-T725-01, SEC-T725-03 |
| A03 Injection | yes (rm argv, the `authoringOnly` pattern, terminal escapes) | 0 |
| A04 Insecure Design | yes | SEC-T725-02, SEC-T722-02 |
| A05 Security Misconfiguration | yes | SEC-T722-01, SEC-T722-05 |
| A08 Data Integrity | yes (fsync, no-clobber publish, no pickle in the index load) | 0 |
| A09 Logging | yes | SEC-T722-04, SEC-T724-01 |

A02, A06, A07 and A10 are not affected: the change touches no package manifest and adds no server-side request.

## 3. Findings (all LOW and tracked as debt; owner devops-engineer, except SEC-T724-01: backend-developer)

| Id | Location | Finding | Fix (reviewer) |
|---|---|---|---|
| SEC-T722-01 | `sync.mjs:1071, 918-921` | A dangling link's text is still resolved lexically. With `sym/../y`, where `sym` is a symlink, the kernel's path differs, and a new file can be created inside a generator input. This needs a crafted layout in the trusted authoring tree. | Refuse any `..` in the text of a dangling link, or resolve the text one component at a time. |
| SEC-T722-02 | `sync.mjs:1043, 1053, 1079`; `test_sync_symlink_hop_limit.py:44` | Off by one: only 39 hops resolve, while the comment says 40. The test does not pin the boundary. This fails closed. | Make the bound mean 40 resolved hops and test that 40 links pass and 41 are refused, or correct the comment. |
| SEC-T722-03 | `sync.mjs:654-662` | The drop step compares the exact key. A token for an unknown server or a case variant is kept, and the `slash` renderer lower-cases it to a grant on Copilot. An object-form `tools` map is not filtered. No shipped agent has these forms. | Refuse a token whose server is not a `servers.yaml` key. Filter or refuse object-form maps that hold an `mcp__` key. |
| SEC-T722-04 | `context_retriever.py:99, 103`; `server.py:133` | The error message for an unrecognised remote contains the raw remote URL, which may hold userinfo credentials. Through `default_index_dir` this error can now also occur at server startup, so the traceback reaches the client log. | Redact the userinfo. Catch `RemoteResolutionError` in `main()` and exit with one line instead of a traceback. |
| SEC-T722-05 | `sync.mjs:979-984, 1089-1105` | The allowlist is lexical. If `<ROOT>/.vscode` is a symlink that points outside ROOT, `.vscode/mcp.json` is written outside ROOT. This needs a change in the trusted authoring tree. | Require each MCP file's physical path to lie under the physical ROOT, or under its `outputDir`. |
| SEC-T724-01 | `merge-mcp-json.py:114, 131, 457` | `GENERATED_REF` is the same for every platform. An edited entry, for example one with a renamed variable or `{env:X}` in a client that does not expand it, gets no "differs" note. Only the notice is affected. | Accept only the reference forms the generator writes for that wrapper. |
| SEC-T725-01 | `install.sh:1526-1536` | If `$TARGET/<tree>` is the same directory as `$IMPLEMENTATION/<tree>` through a bind mount, `withhold_authoring_only` deletes `prepare-release` from the source mirror. `make sync` or git can restore it. This is a contrived case. | Return early when `-ef` shows the two are the same directory. Skip any file that is the same file in both places. |
| SEC-T725-02 | `install.sh:1492-1509` | Any safe relative path is accepted, so a listed entry could name a kept local path or a directory. A missing `authoringOnly` key, or a missing manifest, reads as an empty list, so the filter fails open. The manifest comes from the trusted source. | Require the key. Require each entry to be in `files` and under the platform's commands directory. Refuse kept local names. Treat a missing manifest as an error, except for `.clinerules`. |
| SEC-T725-03 | `install.sh:1483-1485` | `-f` follows symlinks. Under `--projections-only`, `implementation/` is not a guarded path, so a link there can switch the filter off. The only effect is that authoring-only commands are kept. | Refuse symlinks on the path components, or document this as accepted. |

## 4. Not verified by the reviewer

- **The sha**: the reviewer had no shell.
- **Some sync.mjs line numbers** were counted from the diff hunk headers.
- **Repo-wide searches** ran on develop, because the `security-audit` grep tool fails on worktree roots.
- **Gates and the suite**: the orchestrator runs them independently before the merge.
