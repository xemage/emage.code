# Artifact: security-review-t835-batch-i-addendum-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Review T835, addendum: T834 follow-up (SEC-T835-01, SEC-T835-02)

## Metadata
- **Date:** 2026-11-14
- **Reviewer:** security-engineer. Read-only: I changed no files and ran no tests or code. Every behaviour claim below comes from reading the code.
- **Gate:** security, for T834 (plan-167).
- **Based on:**
  - `security-review-t835-batch-i-v1.md` § 5.
  - The diff `t835b-diff.patch`: commit `0487febd` on `a4143f81`, worktree `agent-backend-developer-T834`. It touches `context_retriever.py` and both functional test files.
- **Developer's report (theirs, unverified by me):**
  - The fail-first run gave 9 failures under UTF-8 and 2 under a simulated Latin-1 locale (`locale.getencoding` patched). After the fix, 20 tests are OK in both.
  - 246 related tests OK.
  - Drift `[]`.

## 1. SEC-T835-01: fixed

**New check in `_redacted`.** If the original string has a `?` or `#` before its last `@`, the function returns only the scheme followed by `***`.
- The scheme is `_USERINFO_RE`'s group 1. That pattern always matches here, because an `@` is present.
- An scp-like remote has no scheme, so it gives just `***`.

**Why this covers every case.** Every remote now falls into one of three cases:
- **A `?` or `#` before the last `@`.** This covers an `@` inside a query or fragment, and a `?` or `#` inside the userinfo. Nothing after the scheme is shown.
- **The last `@` before every `?` or `#`.** The substitution removes the userinfo. The query or fragment starts after it, and the cut at the first `?` or `#` removes it.
- **No `@` at all.** There is no userinfo, and the query cut applies.

**Other checks.**
- `[?#]` matches across newlines, so the new check needs no `DOTALL` flag.
- The scheme class cannot contain `?`, `#` or `@`.
- I traced all three new remotes and the `bob:p?w` remote through the `@` refusal and the shape errors. Each one shows `https://***` or `***`.
- Tests:
  - New tests cover the library, the server's `default_index_dir` and the build CLI.
  - The existing tests now also assert that the message contains no `bob` and no `p?w`.

**Trade-off (accepted).** For these remotes the message loses all detail after the scheme. No secret is exposed.

**Result.** With this fix, **SEC-T832-01 is fully fixed.**

## 2. SEC-T835-02: fixed

- **The change.** The call now passes `encoding="utf-8"`. The default error handling is strict, so the result no longer depends on the locale.
- **Undecodable output is refused.** The existing `except UnicodeDecodeError` turns it into `RemoteResolutionError from exc`. The message names only the workspace path.
- **Test skips removed.** The two `_LOCALE_DECODES_UTF8` skips are gone from both test files, so the undecodable-remote tests now run everywhere.
- **No working setup breaks.** A valid id is ASCII-only.
- **One side effect:** see SEC-T835-03.

## 3. New finding

| ID | Severity | OWASP | Location | Summary | Status |
|----|----------|-------|----------|---------|--------|
| SEC-T835-03 | SECURITY:LOW (accuracy of a message; no security impact) | A09 | `context_retriever.py:155-168` | Strict UTF-8 decoding also applies to git's `stderr`, so the "not valid UTF-8 text" message can blame the remote when git actually failed | new, tracked-LOW |

### SEC-T835-03

**What happens.**
- Setting `encoding=` on the call applies to `stdout` and `stderr` alike.
- If git fails (for example, there is no `origin`) and writes a translated message in a non-UTF-8 locale, decoding `stderr` raises `UnicodeDecodeError`. That locale is for example `de_DE.ISO-8859-1`; git's translated messages are **(unverified)**.
- The user then sees "the git remote … is not valid UTF-8 text" instead of "could not resolve a git remote".
- It still fails closed. The build CLI shows no detail either way, because the error has a chained cause.

**Remediation (backend-developer).**
- Option 1: drop `text=True` and `encoding=` from the call, and decode only `result.stdout.decode("utf-8")` inside the same `try`. The `stderr` bytes are then never decoded.
- Option 2: pass `env={**os.environ, "LC_ALL": "C"}` to the git call.

## 4. Statuses

| ID | Status |
|----|--------|
| SEC-T832-01 | **fixed**, fully (T834, including `0487febd`) |
| SEC-T832-02 | **fixed** |
| SEC-T835-01 | **fixed** by `0487febd` |
| SEC-T835-02 | **fixed** by `0487febd` |
| SEC-T835-03 | new, `SECURITY:LOW`, tracked as technical debt; owner backend-developer through the orchestrator |

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 4 reviewed (SEC-T832-01, -02, SEC-T835-01, -02) and 1 new (SEC-T835-03) | 4 | 1, tracked as technical debt |

### Justification
- Every finding that this batch and its v1 review set out to close is closed (§ 1-2).
- Query and fragment redaction now covers every case, as shown in § 1.
- Decoding no longer depends on the locale, and the undecodable-remote tests now run in every locale.
- The only open item is SEC-T835-03, a LOW finding with no security impact, which is tracked as debt.
- No required control is removed or weakened, and no Immutable Security Constraint is breached.
- The test results are the developer's and are **unverified** by me. The orchestrator's merge-time suite covers them.

### Conditions
- None.

### Blockers
- None.

### OWASP Coverage
A01, A03, A04, A05 and A09 were reviewed. A09 has 1 finding (SEC-T835-03). A02, A07, A08 and A10 are N/A. A06 was not reviewed: no dependency changed.

## Gate Verdict
**Gate:** security
**Verdict:** PASS
