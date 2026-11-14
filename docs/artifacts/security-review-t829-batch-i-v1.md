# Artifact: security-review-t829-batch-i-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Review T829: T828 batch I (TD-T774-01 / QA-T818-01 rsync fix, QA-T818-03 project-id check)

## Metadata

- **Date:** 2026-11-14
- **Reviewer:** security-engineer. Read-only. I had no shell and no write tool, and I ran nothing.
- **Gate:** security (`validation-gates` § Gate Types), for T828.
- **User's word** (verbatim, via the orchestrator): "I go" (after the orchestrator recommended batch I's installer fix for TD-T774-01, with QA-T818-03 alongside).
- **Based on:**
  - The T828 diff `t829-diff.patch` (commits `c9f282f9` and `f721814a` on `846790e7`, branch `agent/backend-developer/T828`). It touches `scripts/install.sh`, `implementation/runtime/memory/build.py`, `implementation/runtime/memory/README.md`, the new `tests/functional/test_install_equal_size_copy.py` and `tests/functional/test_memory_indexing_pipeline.py`.
  - In the worktree I read `scripts/install.sh:384-405` and `:930-1009`, `build.py:225-324` and `context_retriever.py:60-169`.
  - At develop `8ff89e0d` (the main checkout, before the change) I read `scripts/install.sh:377-383` (`run()`).
  - `docs/tasks/task-T829.md`, `security-review-t820-release-v11-addendum-v1.md` § 1-2, `qa-gate-release-v11-v1.md` (QA-T818-01, -03 rows) and `tracked-debt-register-v17.md` (TD-T774-01 row, item 45).
- **Searches:** `grep_content` refused the worktree root, so every search ran on the main checkout at develop `8ff89e0d`, before the change:
  - all rsync and cp call sites in `scripts/install.sh`;
  - every caller of `BuildConfig(` and `build_index(` in the repository, with `tests/golden/held-out/` excluded.
- **Not read:** `docs/plans/plan-163-batch-i-rsync-and-project-id.md` (the brief's acceptance criteria were enough), `_CopierMatrix` and `run_installer` in the test helpers, and the single-file writers of `install.sh`.
- **Not run:** the tests and the installer. Every pass, failure and fail-first count below is **the developer's report (unverified)**.

## 1. Fix 1: `--checksum` in `copy_tree_into` and `sync_tree_into`

**Does it close TD-T774-01 / QA-T818-01? Yes, once T828 is merged.**

- **All three rsync call sites accounted for.** `install.sh` calls rsync in three places, and the search found no other.
  - `copy_tree_into` (`:937`) and `sync_tree_into` (`:987`) now pass `-a --checksum`. Each function's `--dry-run` branch uses the same array.
  - `merge_tree_preserve_existing` (`--ignore-existing`) never overwrites a file, so the quick-check skip does not apply to it. Leaving it unchanged is correct.
- **Why this fixes the skip.** With `--checksum`, rsync decides whether to copy a file by size and content, not by size and mtime.
  - QA saw the skip with mtimes `22:33:22.00` vs `22:33:22.28`, so rsync compared whole seconds only. `--checksum` removes mtime from that decision entirely.
  - The test plants an exact nanosecond mtime match, which is a strict superset of QA's case.
- **The root refresh path is covered.** A root refresh is `install.sh --update` into the repository root, which goes through `sync_tree_into`.
- **The no-rsync fallbacks have no equivalent skip.** In the code I read, `copy_tree_into` falls back to `copy_contents_excluding` (cp). The `sync_tree_into` fallback rebuilds the tree.
- **No migration gap.** `install.sh` runs from the new clone, so the very next `--update` (v11 to the next release) already uses the fixed code.
  - Once this ships, the next release document can drop the K-39 / M-6 check and the `touch` workaround.
  - v11.0.0's own document keeps them, because they are correct for v11's installer.
- **Register v17 item 45 (regrade trigger).** The trigger asked for the code fix to land before any release whose MEDIUM-or-higher fix is a same-size change. Once T828 is merged that condition is met for every later release, so the trigger is retired.
  - The residue "which three files QA's 30-file case skipped" (SEC-T820-02 / TD-T774-01) becomes moot: every equal-size file is now compared by content.
- **Tests (developer's report, unverified).** Three modes (plain, `--update`, `--projections-only`), each with and without rsync.
  - Fail-first: 5 rsync failures. That matches 2 + 2 + 1 planted files.
  - After the fix: all OK.

**Is there new risk from `--checksum`? None found.**

- **Symlinks.** `-a` includes `-l`, so rsync copies symlinks as links and does not follow them. `--checksum` only compares regular files of equal size on both sides. A destination symlink, FIFO or device where the source has a regular file is a type mismatch: rsync replaces it without reading it.
  - Managed roots and their ancestors are still checked by `refuse_unsafe_path` (`:933`, `:983`) before rsync runs.
  - rsync still writes to a temporary file and renames it (`--inplace` is not used), so it never writes through a hard link or a symlink.
- **Permissions.** `-p` and `--chmod=go-w` are applied whether or not content is transferred. An identical file whose mode differs is still fixed.
- **`--delete`.** No interplay. The delete set comes from the file list and the excludes, not from the transfer decision. Excluded paths are still protected, because `--delete-excluded` is not used.
- **Root refresh.** Behaviour is the same as before, except that an equal-size file with changed content is now written.
- **Cost.** rsync's sender checksums every regular source file, not only the equal-size ones (rsync man page, `--checksum`). For these trees that is acceptable. It is not a denial-of-service vector, because the source is the harness's own clone. See SEC-T829-03 for the comment that understates this cost.

## 2. Fix 2: `build.py` compares `--project-id` with the remote-derived id

**Does it close QA-T818-03? Yes.**

- `main` calls `remote_project_id_problem`, which uses `derive_project_id(own_repo_root)`, the server's own function and normalisation. The comparison is exact, with no rewriting.
- `main` returns 2 before `--check-against`, `build_index` and `write_index`, so nothing is written. The tests assert this with mocks.
- QA's case is a test: `acme/other` beside the remote `Acme/Widget` is refused.
- The installer note (`install.sh`, `print_memory_index_notice`) and the README now describe the code correctly.
- **Log injection:**
  - The project id has already passed the argparse form check.
  - The root path is printed with `!r` and truncated to 200 characters.
  - The redacted remote is quoted with `!r` inside the exception text.
  - All three are safe for a terminal.

**Is the CLI-only placement acceptable? Yes.**

- In this repository, only tests call `BuildConfig` or `build_index` directly: `tests/functional/test_memory_indexing_pipeline.py`, `tests/functional/test_hybrid_retrieval.py`, `tests/performance/test_retrieval_eval_scorecard.py` and `tests/performance/test_hybrid_retrieval_latency.py`. Their fixture corpora have no `origin` remote. The CLI is the only documented production entry point (README, installer note, release documents).
- The check is not a security boundary. The authoritative control stays the server's own remote-derived filter (`scope_filter.is_visible`, exact compare), which fails closed: a wrong id returns nothing and data never crosses projects. The CLI check corrects a silent functional failure.
- Recommendation, not a finding: one sentence in the `BuildConfig` or `build_index` docstring stating that library callers get only the form check.

**Is the no-remote refusal right? Yes.**

- The server refuses to start without a usable `origin` (`RemoteResolutionError`, fail closed). An index built without that remote could never be served under a checked id, so refusing is consistent.
- A git error (no repository, no `origin`, `safe.directory` refusal) prints only the root path. A remote of the wrong shape adds the redacted reason.
- **New behaviour:** the build now runs `git -C <own-repo-root> remote get-url origin`.
  - That command reads configuration only. It runs no hooks, `fsmonitor` or pager, because its output is captured.
  - The server already runs the same call on the same root.
  - No new execution risk.

**Is redaction complete?** Yes, for every remote that git can use.

- The mismatch message names only the derived id, and only when `is_derived_project_id` accepts it; otherwise it says "no valid id".
- A shape error passes through `_redacted`, the SEC-T796-01 fix.
- I traced the following by reading:
  - `https://u:p@h/x`;
  - scp-like `u:p@h:o/r`;
  - `ssh://u:p@h:22/o/r`;
  - a secret that contains `@`;
  - the test's `bob:S3cr3t-T828@` in both the mismatch case and the shape-error case.
- One contrived residue remains, a raw `/` in the userinfo: SEC-T829-02.

## 3. Findings

| ID | Severity | OWASP | Location | Summary | Status |
|----|----------|-------|----------|---------|--------|
| SEC-T829-01 | SECURITY:LOW | A04 / A09 | `implementation/runtime/memory/context_retriever.py:128-138` (`derive_project_id`); now also reached from `build.py:303` | `subprocess.TimeoutExpired` is not caught (pre-existing) | open, tracked-LOW, batch I |
| SEC-T829-02 | SECURITY:LOW | A09 | `context_retriever.py:94-99` (`_redacted`); exposed by `build.py:67` (`detail`) | userinfo with an unencoded `/` escapes redaction in a shape error (pre-existing, contrived) | open, tracked-LOW, batch I |
| SEC-T829-03 | SECURITY:LOW (accuracy of a code comment; no security impact) | — | `scripts/install.sh` new comment above `copy_tree_into` | the comment's `--dry-run` and cost claims are wrong | open, tracked-LOW, batch I |

### SEC-T829-01: `derive_project_id` does not catch `subprocess.TimeoutExpired`

- **Grade: `SECURITY:LOW`.** The developer flagged this. It is pre-existing and shared with the server.
- **What happens.** `subprocess.run(..., timeout=10)` raises `TimeoutExpired`, which is a `SubprocessError`. It is neither a `CalledProcessError` nor an `OSError`.
  - A git call that hangs (for example an `include.path` on a stalled network filesystem) escapes as an uncaught exception.
  - In the build CLI that means a traceback and exit 1, before anything is written.
  - In the server it means a crash at startup.
- **Why LOW:**
  - It fails closed in both places.
  - The exception text names the argv: the root path, never the remote URL. The captured `stdout` (which could hold the URL) is not part of `str(exc)` or the default traceback.
  - Only the local user can trigger it, through their own git configuration.
- **Remediation (backend-developer):** catch the timeout together with the existing errors. Add a test with a stub `git` on `PATH` that sleeps past the timeout.

  ```python
  # Before
  except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
  # After
  except (subprocess.SubprocessError, OSError) as exc:  # CalledProcessError, TimeoutExpired; FileNotFoundError is an OSError
  ```

### SEC-T829-02: `_redacted` misses userinfo that contains a raw `/`

- **Grade: `SECURITY:LOW`.** This is pre-existing in SEC-T796-01's redaction. T828 adds a second place where the result is printed (the build CLI's `detail`).
- **What happens.** `_USERINFO_RE` (`^((?:scheme://)?)[^/]*@`) stops at the first `/`.
  - For a remote such as `https://bob:/tok@host`, the path has fewer than two parts, so `normalize_remote_to_project_id` raises "no <org>/<repo> path".
  - Its message then repeats the URL unredacted.
  - I traced this by reading; it is not run.
- **Why LOW.** RFC 3986 requires `/` to be percent-encoded in userinfo. Such a remote cannot authenticate, so a user would notice it. The output goes only to the local user's own stderr.
  - For a password with a raw `/` that still yields at least two path parts, the derived "id" carries `@host` and fails the slug check, so the message shows "no valid id". No leak in that case.
- **Remediation:** do either or both.
  - (a) In `build.py`, drop `str(exc)` from `detail` and state a fixed reason. The user can run `git remote get-url origin` to see the URL.
  - (b) Over-redact in `_redacted`: when the URL holds an `@`, replace everything between the scheme and the last `@` that comes before the path.

  ```python
  # Before (build.py)
  detail = "" if exc.__cause__ is not None else f" ({str(exc)[:300]})"
  # After
  detail = "" if exc.__cause__ is not None else " (its URL has no <org>/<repo> path; see `git remote get-url origin`)"
  ```

### SEC-T829-03: the new `install.sh` comment is inaccurate

- **Grade: `SECURITY:LOW`.** This is code-comment accuracy only, with no security impact. It is recorded so that it is not lost.
- **Dry-run claim.** The comment says "`--dry-run` still lists exactly the files that change". In fact `run()` (`install.sh:377-383`, develop) only echoes `DRY-RUN: rsync ...` when `DRY_RUN=1`. rsync never runs, and no file list is printed.
- **Cost claim.** The comment says the cost is "reading both copies of each equal-size file". rsync's sender checksums every regular source file; only the receiver limits itself to equal-size files.
- **Remediation:** correct both sentences, for example "a dry run prints the rsync command only" and "the sender checksums every source file; the receiver only equal-size ones".

## 4. Statuses

| ID | Status after T828 merges |
|----|--------------------------|
| TD-T774-01 | **fixed** (`--checksum` at both overwriting rsync sites; regression test, unverified run). The regrade trigger (register v17 item 45) is retired. The next release document may drop K-39 and M-6's check and workaround. The "three unidentified files" residue is obsolete. |
| QA-T818-01 | **fixed** (counted with TD-T774-01, as in register v17). |
| QA-T818-03 | **fixed** (CLI exact-equality check against `derive_project_id`; no-remote refusal; corrected installer note and README; tests, unverified run). Library callers keep only the form check, which I accept (§ 2). |
| SEC-T829-01 to -03 | new, `SECURITY:LOW`, tracked as technical debt, batch I, owner backend-developer through the orchestrator. |

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 3 new (SEC-T829-01, -02, -03) and 2 prior (TD-T774-01/QA-T818-01, QA-T818-03) | 2 prior, fixed by T828 | 3, tracked as technical debt |

### Justification
- Both fixes do what TD-T774-01, QA-T818-01 and QA-T818-03 asked for.
- No required control is removed or weakened. The server's remote-derived filter and `refuse_unsafe_path` are unchanged.
- No Immutable Security Constraint is breached. In particular, no credential is printed in the tested or traced realistic cases.
- No MEDIUM or higher finding exists. The three new LOWs are pre-existing or comment accuracy, and are tracked as debt under the user's LOW policy.
- The test runs are the developer's and are not verified by me. The merge-time suite run by the orchestrator covers that.

### Conditions (if CONDITIONAL_PASS)
- None.

### Blockers (if FAIL)
- None.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (project scoping stays server-side) | 0 |
| A02: Cryptographic Failures | N/A (rsync checksums are used only for change detection) | 0 |
| A03: Injection | Yes (rsync argument array; git argv list; repr in messages) | 0 |
| A04: Insecure Design | Yes | 1 (SEC-T829-01) |
| A05: Security Misconfiguration | Yes | 0 |
| A06: Vulnerable Components | No (no dependency changed) | 0 |
| A07: Auth Failures | N/A | 0 |
| A08: Data Integrity Failures | Yes (update-channel integrity, TD-T774-01) | 0 new; TD-T774-01 fixed |
| A09: Logging & Monitoring | Yes (redaction of messages) | 1 (SEC-T829-02) |
| A10: SSRF | N/A (no network request; `git remote get-url` reads configuration only) | 0 |

SEC-T829-03 has no OWASP category (comment accuracy).

## Gate Verdict
**Gate:** security
**Verdict:** PASS
