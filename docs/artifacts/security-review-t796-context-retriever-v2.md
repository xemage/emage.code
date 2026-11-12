# Security review — T796 v2: re-review of the SEC-T796-01 fix (T797)

## Metadata
- **Date:** 2026-11-12
- **Reviewer:** security-engineer (read-only; no file modified, no command run)
- **Tasks:** T796 (review), T797 (fix), plan-153
- **Based on:** `docs/artifacts/security-review-t796-context-retriever-v1.md` (040d193a; verdict FAIL on SEC-T796-01); `docs/plans/plan-153-context-retriever-low-residue.md`; `docs/tasks/task-T796.md`. Code read in worktree `agent-backend-developer-T795`: fix commit `47e56c56`, branch tip `a5da3106` (the orchestrator says it adds only docs; not checked here). The user's instruction of 2026-11-12, verbatim: "O go".

Committed by the orchestrator from the Security Engineer's report; the text is the report's. v1 stands as recorded; this version supersedes its verdict only.

## Verdict
**PASS**

SEC-T796-01 is fixed. No CRITICAL, HIGH or MEDIUM finding. No Immutable Security Constraint is breached, and no required control is missing from the code under review. The v1 results for SEC-T791-02, SEC-T791-03 and QA-T792-1 are unchanged: T797 touches only the three message lines and adds the helper.

## Status of the reviewed ids

| ID | Status | Evidence |
|---|---|---|
| SEC-T796-01 (SECURITY:LOW, blocking in v1 under § Security Gate Protocol item 2) | **fixed** | `context_retriever.py:94` `_USERINFO_RE`, `:97-99` `_redacted` (redacts first, then cuts to 200 characters), used by all three messages at `:112`, `:116` and `:119`. Tests at `test_context_retriever.py:299-329`. |
| SEC-T791-02 | **fixed** (v1, unchanged) | v1 table |
| SEC-T791-03 | **fixed** (v1, unchanged) | v1 table |
| QA-T792-1 | **fixed** on review (v1); the orchestrator's re-run (plan item 3) still applies | v1 table |

## Answers

### 1. Can userinfo reach any message now?

**No, for any userinfo the parser accepts.**

- **The three `RemoteResolutionError` messages:** each passes `remote_url` through `_redacted` (`:112`, `:116`, `:119`). The input is the stripped URL from `:109`. Redaction happens before the cut, so the cut can never remove the `@` and leave the secret in place (`:99`).
- **`derive_project_id` (`:134-138`):** its message holds only `workspace_root`. The chained `CalledProcessError` holds the argv `git -C <root> remote get-url origin` and an exit status. Its text does not include `stderr`, and git's error for a missing remote names the remote (`origin`), not its URL.
- **`default_index_dir` (`:172`):** prints `slug[:80]`. The slug is built from `org` and `repo`. The parser has already removed any userinfo it matched, so the slug holds none. The only remaining case is a malformed URL; see observation O-1.
- **Elsewhere:** `build.py` prints paths and the validated `--project-id` (v1, point 2). `server.py` builds no message of its own.

### 2. Is the greedy regex safe?

**Yes. It removes at least what `_REMOTE_RE` treats as userinfo, and the over-redaction stays before the first `/`.**

**Coverage.** `_REMOTE_RE` (`:81-82`) accepts userinfo `[^@/]+@` either at position 0 or right after an optional scheme `[a-zA-Z][\w+.-]*://`. `_USERINFO_RE` (`:94`) uses the same scheme pattern and then `[^/]*@`:
- **With a scheme:** there is only one possible scheme match, because `[\w+.-]*` can contain neither `:` nor `/`. The parser's userinfo runs from the end of the scheme to the first `@`, with no `/` in between. The greedy `[^/]*@` runs from the same point to the last `@` before the first `/`, so it always includes the parser's userinfo.
- **Without a scheme:** if the scheme branch finds no `@`, the regex backtracks to an empty group and matches from position 0. That covers scp-like `user:tok@host:org/repo`.
- **A parser match at position 0 when the string starts with a scheme** is not possible, because `[^@/]+` cannot cross `://`.

So no input exists where the parser accepts userinfo and the redaction leaves any of it. The tests check five forms, including a secret that contains `@` and an `ssh://` remote (`:301-308`).

**Over-redaction.** It hides only text before the first `/`. For URL-form remotes it reaches no further than the host and port; the path, which the messages are about, stays visible. Each message still states its reason. The scp-like case keeps the host and path (`:310-314`: `***@gitlab.com:acme/..`). It hides more only when an `@` follows the userinfo before the first `/`; see limit (b).

**Not affected by the redaction.** The derived id. Redaction runs only on the error paths, and `:320` uses the parser's groups. The test at `:321-329` shows that remotes with userinfo still normalise as before.

### 3. Are the stated limits acceptable?

**(a) A remote with no `@` at all (`oauth2:tok`) is shown, truncated.**
- **Acceptable, no finding.** By RFC 3986 and by git's scp syntax, a string with no `@` has no userinfo; `oauth2:tok` is host `oauth2` plus path `tok`.
- A credential can appear there only through a misconfiguration that git itself could not use for authentication. The § Logging control covers credentials the code handles as credentials, and the code handles none here.
- **Grade:** none (observation).

**(b) For scp-like `git@host:org@x/repo`, more than the userinfo is hidden.**
- **Acceptable, no finding.** The greedy match runs to the `@` before `x`, so the message shows `***@x/repo`.
- The cost is diagnosability only: the host and org are hidden, the reason text stays. Nothing is exposed.
- The deviation from the v1 sketch is an improvement: v1's `[^@/]+@` would leave the part of a password after a raw `@`.
- **Grade:** none (observation).

### 4. Final status
- **SEC-T796-01:** fixed.
- **Verdict on T795 plus T797:** PASS.

## Findings
None new.

## Observations (no grade, no action required)
- **O-1, malformed URLs.** A password with a raw `/` (for example `https://u:ab/cd@host/repo`) is not valid URL syntax. `_USERINFO_RE` stops at the `/` and does not match. `_REMOTE_RE` then reads part of the password as path, so part of it could appear in the slug message at `:172` (cut to 80 characters).
  - Git and curl cannot authenticate with such a URL either.
  - Before T795 and T797 the same text could already appear there, so this is not a regression.
  - If it is ever wanted, one hardening covers it: show only the refusal reason at `:172`, without the slug.
- **O-2, query strings.** A remote with a query string (`…/repo.git?token=x`) gives a slug that fails `:171`, and the query text appears at `:172`.
  - Git builds `<url>/info/refs?service=…` from the remote, so such a remote does not work over HTTP, and a token there is not realistic.
  - O-1's hardening would cover this as well.

## Method and limits
- **Read:** `context_retriever.py:76-173`; `test_context_retriever.py:286-329`.
- **(unverified):**
  - the full diff of `47e56c56`, and that `a5da3106` adds only docs;
  - that the T797 tests, the suite, the drift gates and the pipeline pass;
  - how the `mcp` SDK shows a tool exception (carried over from v1; it no longer matters for credentials, since the message holds none).
- `tests/golden/held-out/`, `.env*`, credential files, `.claude/settings*.json` and `.vscode/*.json` were not opened. No secret is printed.

## OWASP coverage
| Category | Reviewed | Findings |
|---|---|---|
| A01 Broken Access Control | Yes (v1; T797 does not touch it) | 0 |
| A02 Cryptographic Failures | Yes (not touched) | 0 |
| A03 Injection | Yes (regex reviewed; no path or shell use) | 0 |
| A04 Insecure Design | Yes | 0 |
| A05 Security Misconfiguration | Yes | 0 |
| A06 Vulnerable Components | Yes (no dependency changed) | 0 |
| A07 Auth Failures | Yes (not touched) | 0 |
| A08 Data Integrity Failures | Yes | 0 |
| A09 Logging & Monitoring | Yes | 0 open (SEC-T796-01 fixed) |
| A10 SSRF | Yes (no network request added) | 0 |

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 1 (SEC-T796-01) | 1 | 0 |

### Justification
- **SEC-T796-01:** fixed. Its redaction removes at least the userinfo the parser accepts, in all three messages, and it redacts before it cuts.
- **The batch-O fixes:** still fail closed (v1).
- **Item 2 of § Security Gate Protocol:** does not apply.
- **Medium and low findings:** none remain.

## Gate Verdict
**Gate:** security
**Verdict:** PASS
