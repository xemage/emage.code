# Artifact: security-review-t832-batch-i-followups-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Review T832: T831 batch I follow-ups (SEC-T829-01, SEC-T829-02)

## Metadata

- **Date:** 2026-11-14
- **Reviewer:** security-engineer. Read-only: I changed no files and ran no tests or code. Every behaviour claim below comes from reading the code.
- **Gate:** security (`validation-gates` § Gate Types), for T831 (plan-165).
- **User's word** (verbatim, via the orchestrator): "Batch I follow-ups go".
- **Based on:**
  - The T831 diff `t832-diff.patch` (commit `ec336566` on `bb9a7a16`, worktree `agent-backend-developer-T831`). It touches `implementation/runtime/memory/context_retriever.py`, `tests/functional/test_context_retriever.py` and `tests/functional/test_memory_indexing_pipeline.py`.
  - In the worktree I read `context_retriever.py:60-232`, `build.py:40-89` and `context_retriever_mcp_server/server.py:115-141`.
  - `security-review-t829-batch-i-v1.md` § 3 (SEC-T829-01, -02).
  - `docs/tasks/task-T832.md` and `docs/plans/plan-165-batch-i-followups.md`, as the brief summarised them. I did not reopen either file.
- **Searches:** `grep_content` refused the worktree. Every search ran on the main checkout at develop `198d35b1`, before the change. I searched for callers of `derive_project_id`, `normalize_remote_to_project_id`, `_redacted`, `default_index_dir`, `derive_requesting_context` and `RemoteResolutionError` under `implementation/`. They are `build.py:73`, `server.py:133` and `context_retriever.py` itself. There are no other production callers.
- **Developer's report (unverified by me):**
  - The fail-first run gave 13 failures and 3 errors; after the fix the tests were OK.
  - 314 related tests OK.
  - Drift `[]`.
  - A stub `git` that sleeps produces `RemoteResolutionError` on the server path and exit 2 in the build CLI.

## 1. SEC-T829-01 (`TimeoutExpired` not caught): closed

- `except (subprocess.SubprocessError, OSError)` covers:
  - `CalledProcessError` and `TimeoutExpired`, which are both `SubprocessError`;
  - `FileNotFoundError` and `PermissionError`, which are both `OSError`.
- The error is raised `from exc`, so `build.py:77` still takes the path-only branch, where `detail` is empty.
- In the server, the error stays uncaught at `server.py:133`, so the server fails closed at startup with a traceback. The chained cause's text names only the command's arguments, which contain the workspace path: for `TimeoutExpired` it reads "Command '[...]' timed out after N seconds". `stdout` is not part of that text, so the URL cannot appear in it.
- `_GIT_TIMEOUT_S = 10` is unchanged in value, and a test pins it.
- The stub uses `exec sleep`, so the kill that `subprocess.run` sends on timeout reaches `sleep` itself and leaves no orphan process.
- One residue in the same class, contrived: see SEC-T832-02.

## 2. SEC-T829-02 (userinfo containing a raw `/`): closed

**How the new `_redacted` works.** The pattern is `^((?:scheme://)?).*@` with `re.DOTALL`.

- It removes everything from the end of the scheme to the last `@` in the string. Every possible end of the userinfo lies before that `@`. This holds whether the userinfo contains a raw `/`, an `@`, a `:` or a newline. So no userinfo character can survive, whatever the parser decides.
- I traced the five test remotes:
  - `https://usrt831:/sect831@host` becomes `https://***@host`.
  - `ssh://usrt831:p/sect831@h:22/r` becomes `ssh://***@h:22/r`.
  - The scp-like `usrt831/x:sect831@host:r` has no scheme, so group 1 is empty, and it becomes `***@host:r`.
  - `https://usrt831:/sect831@x@host` becomes `https://***@host`.
  - `https://usrt831:/a/sect831@host/x` is refused by the new `@` check (§ 3), and its message shows `https://***@host/x`.
- **Order of operations is correct.** The substitution runs first and the `[:200]` truncation second. Truncating first could cut the URL before its `@`, so the userinfo would not be matched and would be printed unredacted. The result is then printed with `!r`, which escapes newlines and control characters (no log or terminal injection).
- **Newlines.** `DOTALL` matters here. `_REMOTE_RE` has no `DOTALL`, so a URL value with an embedded newline does not match it and goes to "unrecognized shape". `_redacted` still removes across the newline.
- **Crafted scheme.** For a remote such as `ab://sec@host:o/r`, group 1 is `ab://`. Git also reads this as a URL whose scheme is `ab`, not as an scp-like `user:password` form (git looks for `://` first, **unverified** against git's source). Nothing after `ab://` survives.
- **Over-redaction is accepted.** A path that contains `@` loses detail from the message but exposes no secret.

**Regular-expression denial of service: none.**

- The pattern has one greedy `.*` and no nested or overlapping quantifiers.
- The scheme class `[\w+.-]*` cannot match `:`, so `://` can match at only one place.
- At position 0, the worst case is:
  - one scan to the end of the string;
  - one backtrack to the last `@`;
  - if there is no `@`, at most k failed `://` checks while the scheme gives back characters, then one more scan with an empty group 1.
- Every other position fails at once on `^`.
- So the cost is linear, about 3n steps at most.
- The input is the output of `git remote get-url`, which comes from the user's own local configuration (`.git/config` is not cloned). Even a very long value costs only linear time.

## 3. The new `@`-in-path refusal: correct

- **It closes the second leak path the developer found.** For `https://u:/a/SECRET@host/x`, the org was `secret@host`. Before T831, the server printed it in `default_index_dir` through `slug[:80]`, and it also went into `RequestingContext` through `derive_requesting_context`.
- **No part of the userinfo can reach the id without an `@`.**
  - The last character of the userinfo is followed by `@host`, in the same path segment.
  - Any earlier fragment of the userinfo lies in an earlier segment.
  - If the segment that holds the `@` is one of the last two, the remote is refused. Otherwise `<org>/<repo>` both come from the real path after the host.
  - I traced every test remote and `u/x:sec@host:a/o/r`, which derives `o/r` and carries no secret.
- **Regression risk: none for any configuration that worked before.**
  - GitLab, GitHub and Gitea/Forgejo name rules allow only letters, digits, `-`, `_` and `.` (from my knowledge of their documentation, **unverified** today).
  - Before T831, an id containing `@` already failed `_INDEX_SLUG_RE`, both in `default_index_dir` and in `is_derived_project_id`. The build CLI refuses such an id (`project_id_problem`). So no index could be built and served under such an id.
  - The only change in behaviour is that a server started with `--index-dir` beside such a remote now refuses at startup. Before, it started and returned nothing. Both outcomes fail closed.
  - Subgroups are not affected, because only the last two segments are checked.
- `is_derived_project_id` remains total, because the new raise is caught at `:175`.
- The code comment overstates its premise (SEC-T832-03).

## 4. Remaining paths to a message or log

- Every `RemoteResolutionError` text that contains a URL goes through `_redacted`. This applies at `:122`, `:126`, `:129` and `:131`.
- `default_index_dir` prints only an id that contains no `@`.
- `build.py:83` shows the derived id only when `is_derived_project_id` accepts it.
- `derive_project_id` messages name only the path.
- I found no remaining path by which userinfo reaches a message or a traceback.
- Non-userinfo parts of the URL are printed verbatim (SEC-T832-01).

## 5. Option (a) (a fixed `detail` in `build.py`): not required

- With redaction now total for userinfo, option (a) would remove useful diagnostics for no gain against userinfo.
- It would also not cover the server path, where a traceback carries the same message.
- If any hardening is wanted, apply it at the source in `_redacted`, so that both paths get it. That is SEC-T832-01's remediation.
- My recommendation is not to apply (a).

## 6. Findings

| ID | Severity | OWASP | Location | Summary | Status |
|----|----------|-------|----------|---------|--------|
| SEC-T829-01 | SECURITY:LOW | A04 / A09 | `context_retriever.py:146` | `TimeoutExpired` not caught | **fixed** by T831 |
| SEC-T829-02 | SECURITY:LOW | A09 | `context_retriever.py:96-109`, `:130-132` | userinfo with a raw `/` escaped redaction; second path through `default_index_dir` | **fixed** by T831 |
| SEC-T832-01 | SECURITY:LOW | A09 | `context_retriever.py:109` (`_redacted`), `:185` (`slug[:80]`) | the query and fragment of a remote are printed verbatim | new, tracked-LOW |
| SEC-T832-02 | SECURITY:LOW | A04 | `context_retriever.py:142-152` | a remote that is not valid UTF-8 raises an uncaught `UnicodeDecodeError` | new, tracked-LOW |
| SEC-T832-03 | SECURITY:LOW (accuracy of a code comment; no security impact) | — | `context_retriever.py:98-99` | the comment "git hosts allow no `@`" overstates its premise | new, tracked-LOW |

### SEC-T832-01: query string and fragment are not redacted

- **What happens.** `_redacted` removes only the userinfo. For a remote such as `https://host/r?private_token=X`:
  - the shape error "no `<org>/<repo>` path" repeats `?private_token=X`;
  - for `https://host/o/r?token=X`, the slug check in `default_index_dir` prints the slug, `o-r?token=x`.
- **Why LOW.** Git smart HTTP appends `/info/refs?service=...` to the URL string, so a token in a query string does not authenticate in a git remote (**unverified**). The output goes only to the local user's own stderr.
- **Remediation (backend-developer).**
  - After the substitution, cut the string at the first `?` or `#`.
  - In `default_index_dir`, drop the slug from the message.

  ```python
  # Before
  return _USERINFO_RE.sub(r"\1***@", remote_url, count=1)[:200]
  # After
  return re.split(r"[?#]", _USERINFO_RE.sub(r"\1***@", remote_url, count=1), maxsplit=1)[0][:200]
  ```

### SEC-T832-02: `UnicodeDecodeError` from `text=True` is not caught

- **What happens.** If the remote URL is not valid in the locale's encoding, decoding raises `UnicodeDecodeError`, which is a `ValueError`. This happens inside `subprocess.run` and is not caught. The result is a traceback, or exit 1 in the build CLI.
- **Why LOW.** It fails closed. The exception text names only the byte offset, not the content. It is also contrived: the user would have to set such a URL in their own configuration.
- **Remediation.** Pass `errors="replace"` to `subprocess.run`, or add `UnicodeDecodeError` to the `except`.

### SEC-T832-03: the comment overstates "git hosts allow no `@`"

- **What is wrong.** Plain SSH or self-hosted path remotes, such as `ssh://host/srv/a@b/repo`, can contain `@`.
- **No security impact, no regression.** Such ids were already unusable (§ 3).
- **Remediation.** Reword the comment, for example: "an id with `@` is never a valid index slug (`_INDEX_SLUG_RE`); refusing it here keeps parser-unseparated userinfo out of the id".

## 7. Statuses

| ID | Status after T831 merges |
|----|--------------------------|
| SEC-T829-01 | **fixed** |
| SEC-T829-02 | **fixed**, including the second `default_index_dir` / `RequestingContext` path found by the developer |
| SEC-T829-03 | not reviewed here; outside T831's diff |
| SEC-T832-01 to -03 | new, `SECURITY:LOW`, tracked as technical debt (register: next batch), owner backend-developer through the orchestrator |

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 2 prior (SEC-T829-01, -02) and 3 new (SEC-T832-01 to -03) | 2 (SEC-T829-01, -02) | 3, tracked as technical debt |

### Justification
- Both prior findings are closed by reading (§ 1-3).
- Redaction is total for userinfo, applied before truncation and printed with `repr`.
- The pattern runs in linear time.
- The `@` refusal breaks no configuration that worked before.
- No required control is removed or weakened, and no Immutable Security Constraint is breached.
- The three new findings are LOW and are tracked as debt under the user's LOW policy.
- The test runs are the developer's and are unverified. The orchestrator's merge-time suite covers them.

### Conditions (if CONDITIONAL_PASS)
- None.

### Blockers (if FAIL)
- None.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (the id still comes only from the remote; fails closed) | 0 |
| A02: Cryptographic Failures | N/A | 0 |
| A03: Injection | Yes (argument list for git; `repr` in messages; regex DoS) | 0 |
| A04: Insecure Design | Yes | 1 (SEC-T832-02) |
| A05: Security Misconfiguration | Yes | 0 |
| A06: Vulnerable Components | No (no dependency changed) | 0 |
| A07: Auth Failures | N/A | 0 |
| A08: Data Integrity Failures | N/A | 0 |
| A09: Logging & Monitoring | Yes (redaction) | 1 (SEC-T832-01) |
| A10: SSRF | N/A (`git remote get-url` reads configuration only) | 0 |

SEC-T832-03 has no OWASP category (comment accuracy).

## Gate Verdict
**Gate:** security
**Verdict:** PASS
