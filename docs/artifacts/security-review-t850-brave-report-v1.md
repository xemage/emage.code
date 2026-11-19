# Security Review T850: draft upstream report to Brave (SEC-T702-08)

## Metadata

- **Date:** 2026-11-19
- **Task:** T850 (plan-172). The user's decision: "P go". LOW policy, the user's words: "Track LOW items as debt, stop chasing (Recommended)". Record (plan-126): "The orchestrator offers the user a draft of the report; the user files it, or decides not to."
- **Reviewer:** security-engineer (read-only; no shell; no file edited; nothing posted; no login).
- **Based on:** worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T849`, branch `agent/devops-engineer/T849`, commit `919fad8c`; `docs/artifacts/brave-upstream-report-draft-v1.md` (T849); `docs/tasks/task-T850.md`; the orchestrator's brief for T850, which reports its `npm view` results; the extracted 2.1.5 tarball file `dist/BraveAPI/index.js`, read as text only; upstream `src/BraveAPI/index.ts` at `e08f5af01fffb0d208995f052239d024a3721212` (GitHub blob page and raw.githubusercontent.com, unauthenticated GET); undici `docs/docs/api/Client.md` on `main` (GitHub).
- **Method limits:**
  - I read 2.1.5's `dist/BraveAPI/index.js` lines 85-123. I did not read 2.1.4's copy. The claim that it is identical comes from T849's `diff -r` and the orchestrator's check **(not re-checked by me)**.
  - For upstream `index.ts` I read the file through a summarising fetch tool. GitHub's page reports "141 lines (121 loc)", which matches the draft. The tool gave the absolute line numbers as 114/121/124/132, which disagree with the 141-line total it also reported. The gaps between the relevant lines are the same as in the draft's 116/123/126/134 (+7, +3, +8). I therefore treat the draft's absolute line numbers as **plausible but unverified by me**. § 5 step 2 of the draft already asks the user to re-check them before filing.
  - I did not open plan-172 or the SEC-T702-08 row in `security-review-t702-brave-reachability-v1.md` (token budget). I took the finding's wording from the draft's Metadata.
  - I did not re-run T849's issue search (§ 1.4) or its `SECURITY.md` checks (§ 1.5) **(unverified by me)**.
  - I did not run the "Body is unusable" behaviour.

## Scope

1. Accuracy of the finding (draft § 1 and the § 4 paste text).
2. Disclosure: whether the § 4 text reveals anything about the user, the project, the harness, the repository, the GitLab instance, any host, path, IP, token, email, username or the agent setup.
3. Channel: public issue or private advisory.
4. Factual claims in § 4: undici's 300 s defaults, and the "Body is unusable" side note.

Out of scope: SEC-T702-09 (dependency advisories, 2.1.5 bump); whether this repository is in scope for Brave's HackerOne programme.

## Assessment

### 1. Accuracy: confirmed

- 2.1.5 `dist/BraveAPI/index.js` line 103 is `const response = await fetch(urlWithParams, { headers });`, with no `signal`. The error path is `response.json()` at line 108 and `response.text()` inside `catch` at line 112. The success path is `response.json()` at line 118. Nothing in lines 85-123 limits size or time. This matches the draft exactly.
- Upstream `main` at `e08f5af0`: the same code, and neither `signal` nor `AbortSignal` appears anywhere in the file. The finding is present on `main`.
- "Buffered and parsed in full (after gzip decoding)" is accurate: undici's fetch decodes `Content-Encoding: gzip` transparently, and `json()`/`text()` consume the whole stream.
- "The MCP client may time out its own request, but the server-side fetch keeps running" is accurate, because no signal reaches `fetch`.
- "Only `fetch` to the Brave API, so all tools share it" comes from T849's grep of `dist/` **(not re-checked by me)**.
- The suggested-fix sketch is sound:
  - an `AbortSignal.timeout` passed to `fetch` also aborts reading the body, so it bounds the whole request, not only the headers;
  - `AbortSignal.any` exists in Node 20.3+;
  - reading the body once as text and then calling `JSON.parse` removes the double-read.
  The sketch is labelled a sketch, with placeholder values, which is appropriate.

### 2. Disclosure: clean

I checked the § 4 text, lines 100-157 of the draft, between the two `---` lines, line by line. It contains only:
- public upstream identifiers: versions, the public commit hash, public file paths inside the upstream package, and public PR #315;
- generic technical description and code.

It contains no user name, project name, harness or agent term, repository or GitLab reference, host, IP, local path, token, email, username, internal finding ID (no `SEC-T702-08`, no `T849`), date tied to internal work, or the word "audit". The phrase "over stdio" describes a generic deployment mode of the package, not this setup.

The only identity exposure is inherent to the channel: the issue is linked to the user's GitHub account. The draft says so (§ 2, last paragraph; § 5 step 2).

Note for the user: the last sentence, "I'm happy to test a fix or a pre-release build…", is a commitment in the user's name. It discloses nothing, but the user may delete it if they do not want to make that offer (optional; not a finding).

### 3. Channel: an ordinary public issue is right

I agree with § 3:
- the impact is availability-only and LOW, and it needs the vendor's own fixed endpoint, or a proxy the operator configured, to misbehave;
- the code is public, so the issue reveals nothing that is not already visible;
- T849 found no `SECURITY.md` or private reporting instruction **(unverified by me)**;
- upstream already handles comparable robustness topics in public (#277, #321).

A private advisory would add friction and protect nothing.

### 4. Factual claims in § 4

- **undici 300 s.** Partly confirmed, but imprecise. undici's `Client.md` gives `headersTimeout` default `300e3` ms, described as "the timeout … the parser waits to receive the complete HTTP headers". It gives `bodyTimeout` default `300e3` ms, described as one that "monitors the time between consecutive body chunks". So the number is correct, but:
  - only `bodyTimeout` is an inactivity timer;
  - a response whose headers never complete is cut off at about 300 s, not left pending "indefinitely";
  - the indefinite case is a body that keeps sending bytes more often than every 300 s.

  The draft's sentence calls both timers "inactivity timeouts" and attributes the indefinite hang to "a response that keeps trickling bytes" in general. That overstates the headers case (SEC-T850-01). That Node's built-in `fetch` uses undici's global dispatcher with these defaults is my reading of undici and Node; I did not trace it in Node's source **(unverified)**.
- **"Body is unusable" side note.** The reasoning is correct under the Fetch standard. `json()` consumes the body, so the body is then "disturbed", and a second consume (`text()`) rejects with a `TypeError`. Here that rejection is thrown from inside `catch`, so it replaces the intended message. The draft words it as "should reject", which is hedged. The exact undici message text is not verified, and its wording varies between undici versions **(unverified)**. Quoting the type is safer than quoting a string (SEC-T850-02).

## Findings

| ID | Severity | Category | Location | Description | Remediation |
|----|----------|----------|----------|-------------|-------------|
| SEC-T850-01 | SECURITY:LOW | Accuracy of the report (no OWASP category) | `brave-upstream-report-draft-v1.md` line 111 (§ 4, "What happens") | It calls both undici timers "inactivity timeouts" and implies that any trickle hangs indefinitely. `headersTimeout` is a total wait for complete headers, so a stall before or during the headers ends after about 300 s; only a body trickle evades `bodyTimeout`. | Replace the paragraph with the text below before filing. |
| SEC-T850-02 | SECURITY:LOW | Accuracy of the report (no OWASP category) | Same file, line 155 (§ 4, "Side note") | It quotes the exact error string "Body is unusable", which is not verified and varies by undici version. | Replace the side note with the text below before filing. |

**Replacement for line 111 (the "What happens" paragraph), exact text:**

> **What happens:** the request has no timeout of its own. Node's built-in fetch (undici) applies only its defaults: `headersTimeout` (300 s to receive the complete response headers) and `bodyTimeout` (300 s between consecutive body chunks), per the undici documentation. So a stalled endpoint, or a proxy in front of it, holds the tool call for up to about 5 minutes. A response body that keeps sending a few bytes more often than every 300 s never trips either timer, so the call can stay pending indefinitely. If the endpoint returns an unexpectedly large body, it is buffered and parsed in full (after gzip decoding), which can grow the process's memory without bound.

**Replacement for line 155 (the side note), exact text:**

> **Side note, same lines:** on the error path, `response.json()` consumes the body. When the body is not JSON, the following `response.text()` should therefore reject with a `TypeError` (the body has already been read), and that error replaces the intended `status statusText` message. Reading the body once as text and then trying `JSON.parse`, as in the sketch, avoids that.

## OWASP

| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | No (not applicable to a report text) | 0 |
| A02: Cryptographic Failures | Yes (no secret or token in § 4) | 0 |
| A03: Injection | No (not applicable) | 0 |
| A04: Insecure Design | Yes (the reported finding: no timeout or size limit; the fix sketch) | 0 new |
| A05: Security Misconfiguration | Yes (undici default timeouts) | 0 |
| A06: Vulnerable Components | Yes (2.1.4/2.1.5 code checked; SEC-T702-09 out of scope) | 0 |
| A07: Auth Failures | No (not applicable) | 0 |
| A08: Data Integrity Failures | No (not applicable) | 0 |
| A09: Logging & Monitoring | Yes (disclosure of internal identifiers: none) | 0 |
| A10: SSRF | Yes (the endpoint is a fixed HTTPS host; no user-controlled URL) | 0 |

SEC-T850-01 and SEC-T850-02 concern the accuracy of the report text and fall under no OWASP category.

## Verdict

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 2 | 0 | 2 |

### Justification

- **Accuracy:** the finding is accurate in 2.1.5 and on `main` `e08f5af0`.
- **Disclosure:** the § 4 paste text is clean.
- **Channel:** a public issue is the right channel.
- Two LOW wording inaccuracies in § 4 (SEC-T850-01, SEC-T850-02) should be corrected before the user files. Nothing blocks.

### Conditions
- SEC-T850-01 and SEC-T850-02: owner=@devops-engineer (draft v2) or the orchestrator, applying the replacement text in what it offers the user; remediation=replace § 4 lines 111 and 155 with the exact text above; deadline=before the draft is offered to the user to file. If the user declines to file, both close with the draft as moot; otherwise they are tracked LOW per policy.

### Blockers
None.
