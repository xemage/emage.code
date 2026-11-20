# Artifact: security-review-t835-batch-i-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Review T835: T834 batch I (SEC-T832-01, SEC-T832-02)

## Metadata
- **Date:** 2026-11-14
- **Reviewer:** security-engineer. I worked read-only: I changed no files and ran no tests or code. Every behaviour claim comes from reading the code.
- **Gate:** security (`validation-gates` § Gate Types), for T834 (plan-167).
- **User's word** (verbatim, from the orchestrator): "Continue with one of the LOW batches". The orchestrator chose SEC-T832-01 and -02 from batch I.
- **Based on:**
  - The T834 diff `t835-diff.patch`: commit `a4143f81` on `92a8c8a0`, worktree `agent-backend-developer-T834`.
  - In the worktree I read:
    - `context_retriever.py:60-244`
    - `build.py:40-89`
    - `context_retriever_mcp_server/server.py:110-141`
  - `security-review-t832-batch-i-followups-v1.md` § 6.
  - I did not reopen `docs/plans/plan-167-batch-i-sec-t832.md`. I used it as the brief summarised it.
- **Searches:** `grep_content` refused the worktree, so I searched the main checkout at develop `198f8237`, which is before the change. I searched `context_retriever.py`, `scope_filter.py` and `server.py` for `project_id`, `.stderr`, `errors=`, `text=True` and `encoding=`. Results:
  - There is one `subprocess` decode site, `context_retriever.py:144` on develop (`:150` in the worktree).
  - No code logs or prints `RequestingContext.project_id`. `scope_filter.py` only compares it.
- **Developer's report (theirs, unverified by me):**
  - Fail-first run: 7 failures and 2 errors. After the fix: 17 OK.
  - 243 related tests OK.
  - Drift `[]`.
  - They chose to raise `RemoteResolutionError from exc` instead of `errors="replace"`, so that a partly decoded remote never reaches the id logic.

## 1. SEC-T832-01 (query string and fragment printed verbatim): fixed for the reported shapes, one gap left (SEC-T835-01)

What T834 changed:
- **`_redacted`** (`:110-115`) now does three things in this order:
  1. Replaces everything from after the scheme to the last `@` with `***@`.
  2. Drops everything from the first `?` or `#` on.
  3. Cuts the result to 200 characters.
- **`default_index_dir`** (`:197-198`) no longer prints the slug. Its message is now fixed text.

Cases I traced by reading:
- `https://host/r?private_token=X`: no `@`, so step 1 does nothing. Step 2 gives `https://host/r`. Fixed.
- `https://host/o/r?token=X` and `https://host/o/r#X` reach the server path. The id `o/r?token=x` fails `_INDEX_SLUG_RE`, and the message carries no slug. Fixed.
  - In the build CLI, `build.py:83` shows the id only if `is_derived_project_id` accepts it. It does not accept `?`, `=` or `#`.
  - On the server path with `--index-dir`, the id `o/r?token=x` does reach `RequestingContext`. My grep found no code that prints it. It never matches a chunk, so the server fails closed with no results.
- **A `?` or `#` inside the userinfo**, for example `https://bob:p?w@host/r?private_token=X`:
  - Step 1 removes everything up to the last `@`, giving `https://***@host/r?private_token=X`.
  - Step 2 gives `https://***@host/r`.
  - Doing the userinfo first is correct here. If the query cut ran first, the output would be `https://bob:p` and the user and part of the password would leak.
- **A `?` in the path:** cut correctly.
- **scp-like remotes**, for example `git@host:o/r?x=S`:
  - There is no scheme, so the step-1 pattern has an empty scheme group, giving `***@host:o/r?x=S`.
  - Step 2 gives `***@host:o/r`. Fixed.
- **Truncation last:** correct. Truncating earlier could cut the string before its `@` or `?`, and the secret would survive.
- **Percent-encoded `%3F`:** it is not a delimiter. It stays in the path and separates nothing, so there is nothing to redact.

**The gap: an `@` inside the query or fragment (SEC-T835-01).**
- Step 1 is greedy: it runs to the **last** `@` in the whole string, even when that `@` is in the query. The `?` is removed with it, so step 2 then finds nothing to cut.
- Example: `https://host/r?email=a@b&private_token=SECRET`.
  - `_REMOTE_RE` matches it. The path is `r?email=a@b&private_token=SECRET`, which has only one part, so it is refused at `:132`.
  - The message prints `'https://***@b&private_token=SECRET'`.
- Example: `https://host/o/r?e=a@b&t=SECRET`.
  - It is refused at `:137` (`@` in the repo), with the same leak.
- The same happens with `#…@…` in a fragment and with scp-like `git@host:o/r?a=b@c&t=S`.
- Where the message goes:
  - The build CLI prints it at `build.py:77`. That error has no chained cause, so the detail text is shown.
  - The server prints it in its startup traceback.
- **Severity: LOW**, the same as SEC-T832-01. The remote comes from the user's own configuration, and the output goes only to the local user's stderr. A token in a query string probably does not authenticate git smart HTTP **(unverified)**.
- **Test gap:** none of the new tests puts an `@` after the `?` or `#`.

## 2. SEC-T832-02 (`UnicodeDecodeError` not caught): closed

- **Where the error comes from.** `UnicodeDecodeError` is a `ValueError`, so the T831 handler for `SubprocessError` and `OSError` did not catch it. The new `except` at `:158` catches it.
- **All decode paths are covered.**
  - With `text=True`, `subprocess.run` decodes both `stdout` and `stderr` after `communicate()` returns. One `except` around the call therefore covers an undecodable `stderr` too. That case is decoded before `CalledProcessError` is built.
  - If decoding fails inside `communicate()`, `run()` kills the process and re-raises. Nothing is left running.
  - This is the module's only decode site (my grep). `resolve_platform` reads with an explicit `encoding="utf-8"`, and its `UnicodeDecodeError` is outside T834's scope. That path is a manifest built by `sync.mjs`, not a remote, and the error carries no remote content. Not a finding.
- **The message is safe.**
  - The new message names only `workspace_root`. The chained cause names byte offsets and the codec, not the content.
  - In the build CLI, `exc.__cause__` is set, so `build.py:77` shows no detail text. The CLI exits 2, and the test asserts this.
- **Choosing to fail closed is right.** With `errors="replace"`, a partly decoded remote would be passed on to normalisation. The ids are ASCII-only, so the remote would be refused in the end anyway, but raising is simpler and stricter.
- **Non-UTF-8 locales.**
  - Under a single-byte locale such as Latin-1, every byte decodes, so no error is raised. The mojibake then fails `_REMOTE_RE` or `_INDEX_SLUG_RE` and is refused, so it still fails closed.
  - Under the C or POSIX locale, Python 3.7+ coerces to UTF-8 (PEP 538/540) **(unverified on the CI image)**.
  - `text=True` makes the behaviour depend on the locale. That is SEC-T835-02.

## 3. The locale-gated test skip: acceptable

- **Why the skip is needed.** Under a single-byte locale, the bytes `0xff 0xfe` decode, so the test would assert something false. Skipping is honest there.
- **Is the gate exactly right?**
  - The gate checks UTF-8 mode, or `locale.getpreferredencoding(False)` resolving to `utf-8`.
  - On Python 3.11+, `subprocess` may pick its text encoding through a different function. It might be `locale.getencoding()` **(unverified)**.
  - If the two differ, the gate could run the test where it should be skipped. That would fail loudly, not hide anything.
- **CI.** The CI images run a UTF-8 locale **(unverified)**, so the test should run there. The expected skip count, 25, was set before T834. The orchestrator should check that T834 leaves it at 25 in CI, which shows the two new tests ran.
- **Forcing a locale in the test would not help.** The library calls `subprocess.run` in the test's own process, so the test cannot force the locale without a child interpreter.
- **The better design is SEC-T835-02:** pass an explicit encoding to `subprocess.run`. The tests would then not need a skip at all.

## 4. Other ways a message could leak query, fragment or userinfo
- Every message that contains a URL goes through `_redacted`: `:128`, `:132`, `:135` and `:138`.
- `default_index_dir` no longer prints the slug.
- `build.py:83` prints only an id that `is_derived_project_id` accepts.
- `derive_project_id` messages name only the path.
- `project_id_problem` (`build.py:61`) repeats the user's own `--project-id` argument, not the remote. That is out of scope.
- The only remaining leak is SEC-T835-01.

## 5. Findings

| ID | Severity | OWASP | Location | Summary | Status |
|----|----------|-------|----------|---------|--------|
| SEC-T832-01 | SECURITY:LOW | A09 | `context_retriever.py:110-115`, `:197-198` | Query string and fragment were printed verbatim | **fixed** for the reported shapes by T834; one gap left, see SEC-T835-01 |
| SEC-T832-02 | SECURITY:LOW | A04 | `context_retriever.py:158-162` | `UnicodeDecodeError` was not caught | **fixed** by T834 |
| SEC-T835-01 | SECURITY:LOW | A09 | `context_retriever.py:114-115` | An `@` in the query or fragment makes step 1 remove the `?` or `#`; the rest of the query is printed | new, tracked-LOW. I recommend fixing it in this batch. |
| SEC-T835-02 | SECURITY:LOW (robustness) | A04 | `context_retriever.py:150` | `text=True` decodes in the locale's encoding, so behaviour and tests depend on the locale | new, tracked-LOW |

### SEC-T835-01: an `@` after a `?` or `#` defeats the query cut
- **What happens.** For `https://host/r?email=a@b&private_token=SECRET`, the message prints `'https://***@b&private_token=SECRET'`. It is printed by `build.py:77` and in the server's startup traceback.
- **Remediation (backend-developer).** When a `?` or `#` appears before the last `@`, the code cannot tell userinfo from query. In that case, show only the scheme:
  ```python
  # Before
  without_userinfo = _USERINFO_RE.sub(r"\1***@", remote_url, count=1)
  return _QUERY_OR_FRAGMENT_RE.split(without_userinfo, maxsplit=1)[0][:200]
  # After
  head, at, _ = remote_url.rpartition("@")
  if at and _QUERY_OR_FRAGMENT_RE.search(head):  # '?'/'#' before the last '@': userinfo or query, cannot tell
      return _USERINFO_RE.match(remote_url).group(1)[:200] + "***"
  without_userinfo = _USERINFO_RE.sub(r"\1***@", remote_url, count=1)
  return _QUERY_OR_FRAGMENT_RE.split(without_userinfo, maxsplit=1)[0][:200]
  ```
- **Tests to add:**
  - Both new test classes should cover these remotes:
    - `https://host/r?email=a@b&private_token=QSECRET`
    - `https://host/o/r#x@y&FSECRET`
    - `git@host:o/r?a=b@c&t=QSECRET`
  - The existing `https://bob:p?w@host/...` case should also assert that the message contains no `bob` and no `p?w`.
- **Trade-off.** Messages for remotes that have a `?` or `#` in their userinfo lose detail. No secret is exposed.

### SEC-T835-02: decoding depends on the locale
- **Remediation.** Pass `encoding="utf-8"` (strict) to `subprocess.run`. The existing `except UnicodeDecodeError` keeps it failing closed.
- **What this gains.**
  - The same result in every locale.
  - The `_LOCALE_DECODES_UTF8` skips can be removed from both test files.
- **What changes for users.** A remote that is not UTF-8 under a Latin-1 locale is now refused as "not valid text" instead of as an unrecognized shape. It is still a refusal. A valid id is ASCII-only, so no working setup breaks.

## 6. Statuses
| ID | Status after T834 merges |
|----|--------------------------|
| SEC-T832-01 | **fixed** for the reported shapes; the remaining case is tracked as SEC-T835-01 |
| SEC-T832-02 | **fixed** |
| SEC-T832-03 | not in T834's scope; not reviewed here |
| SEC-T835-01, SEC-T835-02 | new, `SECURITY:LOW`, tracked as technical debt; owner backend-developer through the orchestrator. SEC-T835-01 should be fixed in this batch. |

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 2 prior (SEC-T832-01, -02) and 2 new (SEC-T835-01, -02) | 2 (SEC-T832-01 for its reported shapes, SEC-T832-02) | 2, tracked as technical debt |

### Justification
- SEC-T832-02 is closed. All decode paths around the git call, including `stderr`, now fail closed with a message that carries no remote content.
- SEC-T832-01 is closed for every shape it reported, including scp-like remotes and a `?` inside the userinfo. The order (userinfo first, then the query cut, then truncation) is correct in those cases.
- The one gap left, an `@` inside the query (SEC-T835-01), is LOW for the same reasons as SEC-T832-01: it is the local user's own configuration printed to their own stderr.
- No required control is removed or weakened, and no Immutable Security Constraint is breached.
- Under the user's policy, LOW findings are tracked as debt, so the verdict is PASS (§ Security Gate Protocol, item 3).
- The test runs are the developer's and are **unverified** by me. The orchestrator's merge-time suite covers them.

### Conditions (if CONDITIONAL_PASS)
- None. Recommendation, not a condition: fix SEC-T835-01 in this batch. It is a few lines and three test cases.

### Blockers (if FAIL)
- None.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (the id still comes only from the remote; it fails closed) | 0 |
| A02: Cryptographic Failures | N/A | 0 |
| A03: Injection | Yes (`repr` in messages; the regex runs in linear time) | 0 |
| A04: Insecure Design | Yes | 1 (SEC-T835-02) |
| A05: Security Misconfiguration | Yes | 0 |
| A06: Vulnerable Components | No (no dependency changed) | 0 |
| A07: Auth Failures | N/A | 0 |
| A08: Data Integrity Failures | N/A | 0 |
| A09: Logging & Monitoring | Yes (redaction) | 1 (SEC-T835-01) |
| A10: SSRF | N/A | 0 |

## Gate Verdict
**Gate:** security
**Verdict:** PASS
