# Artifact: brave-upstream-report-draft-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: devops-engineer (T849, plan-172). **Date**: 2026-11-19. **Owner**: devops-engineer.
- **Finding**: SEC-T702-08 (`SECURITY:LOW`, "track; report upstream").
- **Based on**: `docs/plans/plan-172-batch-p-brave-upstream-report.md`, `docs/tasks/task-T849.md`, `docs/artifacts/security-review-t702-brave-reachability-v1.md` (SEC-T702-08 row), `docs/artifacts/brave-audit-acceptance-v4.md`, `implementation/knowledge/mcp/servers.yaml` (brave entry, pin `@brave/brave-search-mcp-server@2.1.4`).
- **User decision** (2026-11-19, verbatim): "P go".
- **Nothing was posted.** Every upstream check below is a read-only, unauthenticated GET (npm registry, GitHub REST API, raw.githubusercontent.com) with a generic User-Agent. The package was packed and extracted only; it was not installed, built or run. No Brave API key was used and the Brave Search API was not called.

## § 1 Checks

### 1.1 Shipped version 2.1.4 (the pin)

| Item | Value |
|------|-------|
| Tarball | `brave-brave-search-mcp-server-2.1.4.tgz` (`npm pack`, `--ignore-scripts`) |
| sha256 | `5770f091fc15d7a49f9f44004e39793fd8126a4684138be662ae68f4a10dff27` |
| npm integrity | `sha512-a34HBs6os4Ilp0yHPV/j3UrgBQH1uTDLsNA9y5IlO30RCYUFm9QPfC0coh2c7WEDxKcHuWjVsrfuXIJNheu9YA==` |
| Published | 2026-09-17T14:48:15Z |
| Contents | `dist/` only (compiled JavaScript) plus `package.json`, `README.md`, `LICENSE`. There is no `src/`, so the compiled `dist/BraveAPI/index.js` was read in place of `src/BraveAPI/index.ts`. |

`dist/BraveAPI/index.js` (123 lines), function `issueRequest`:

- **Line 103**: `const response = await fetch(urlWithParams, { headers });`. This is the only `fetch(` call in the non-test `dist/` tree, so every tool (web, local, place search, images, videos, news, summarizer, LLM context) goes through it. The init object has only `headers`: no `signal`, no `AbortController`, no `AbortSignal.timeout`.
- **Line 118**: success path, `await response.json()`. The whole body is buffered and parsed, with no `content-length` check and no read limit.
- **Lines 108 and 112**: error path, `await response.json()` and then, if that throws, `await response.text()`. Again no limit.
- No `setTimeout`, `signal` or size check anywhere in the file. The only `setTimeout` in non-test `dist/` is the 50 ms sleep between retries in `dist/tools/summarizer/index.js` (`pollForSummary`, 20 attempts). It does not bound a single request.
- The request header is `Accept-Encoding: gzip` (`getDefaultRequestHeaders`), so a size limit must count decoded bytes, not the `content-length` header alone.

**Result: SEC-T702-08 is confirmed in 2.1.4.**

Side observation (traced from the Fetch standard, not observed at run time, **(unverified)**): on the error path, when `response.json()` fails because the body is not JSON, the body has already been consumed, so the `response.text()` at line 112 rejects with a `TypeError` (in Node's undici, "Body is unusable"). The caller then gets that `TypeError` instead of the intended `"<status> <statusText>\n<body>"` message. It is not a security issue. It is mentioned in the upstream text as an optional note because the suggested fix touches the same lines.

### 1.2 Newest npm version 2.1.5

`npm view @brave/brave-search-mcp-server` on 2026-11-19: `version` and `dist-tags.latest` are **2.1.5**, published **2026-11-17T15:31:58Z**. `gitHead` is `e08f5af01fffb0d208995f052239d024a3721212`. `repository` is `git+https://github.com/brave/brave-search-mcp-server.git`.

| Item | Value |
|------|-------|
| sha256 | `e46e9930db44a225ff45abda56f4987c6c3eec9ace860d8e8a3cebf408a329d5` |
| npm integrity | `sha512-9bvwMfEQmEPQWQElUpBlRaxPHvsfgFpnalt5PoPATstus2Da/V1yz/eb0+x41nblxJDHcadWTCjf9iPSq6za4w==` |

`diff -r` of `dist/BraveAPI/` between 2.1.4 and 2.1.5 shows **no difference**. The same `fetch(urlWithParams, { headers })` is at line 103 and is still the only non-test `fetch(` call. Other files changed between the two versions (tools, HTTP transport, tests); none of the changes adds a signal or a size limit to the Brave API request. **The finding is still present in 2.1.5.**

2.1.5 is newer than the pin. Whether it clears SEC-T702-09 (the advisories in the dependency tree) was **not** checked here; that is outside T849 and belongs to the pin-bump work (SEC-T702-09 keeps its own date).

### 1.3 Upstream default branch

- Repository `brave/brave-search-mcp-server` (GitHub), not archived, issues enabled, default branch **`main`**.
- Head of `main` on 2026-11-19: **`e08f5af01fffb0d208995f052239d024a3721212`** (2026-11-17, "ci: update build assets (v2.1.5)"), the same commit as the npm `gitHead` of 2.1.5.
- Last commit that touched `src/BraveAPI/index.ts`: `50cb919200b24622662c62e197362fe3652cb004` (2026-09-17, "chore: remove dead code and fix HTTP port-conflict startup (#351)").
- `src/BraveAPI/index.ts` at `e08f5af0` (141 lines, sha256 `db577e10330c9b85cf844cd9ded55ea4ec77c41b2787d24952e1586c5486dfd7`): function `issueRequest` starts at line 44; **line 116** `const response = await fetch(urlWithParams, { headers });`; error path `response.json()` line 123, `response.text()` line 126; success path `response.json()` line 134. No `signal`, no timeout, no size check.

**The finding is still present on upstream `main`.**

### 1.4 Existing upstream reports

GitHub issue search (`repo:brave/brave-search-mcp-server`, issues and PRs, open and closed) for `timeout`, `AbortSignal`, `AbortController`, `hang`, `hangs`, `response size`, `body size`, `stuck`. Nothing reports or fixes the missing timeout or size limit on `issueRequest`. The closest hits:

| # | Type, state | What it does | Covers SEC-T702-08? |
|---|-------------|--------------|---------------------|
| [#315](https://github.com/brave/brave-search-mcp-server/pull/315) "feat: answers endpoint" | PR, open (updated 2026-11-18, head `7ce68c80`) | Adds a new streamed chat-completions client with `AbortSignal.timeout(timeoutMs)` combined with the client signal through `AbortSignal.any`. Its hunk in `src/BraveAPI/index.ts` only refactors headers and error handling; the `issueRequest` fetch still gets no `signal`. | No, but it shows that upstream already uses the suggested pattern elsewhere. |
| [#321](https://github.com/brave/brave-search-mcp-server/pull/321) "Bound JSON-RPC batch fan-out and stop retrying permanent Summarizer failures" | PR, open (updated 2026-07-24) | Makes the summarizer's retry sleep abortable through the MCP request signal. Does not pass a signal to `fetch`. | No. |
| [#352](https://github.com/brave/brave-search-mcp-server/pull/352) "chore: bug hunt and simplifications" | PR, open | Renames the URL variable in the `fetch` call; no signal. | No. |
| [#37](https://github.com/brave/brave-search-mcp-server/pull/37) "add HTTP(S) proxy support via undici ProxyAgent" | PR, open (2025-08-09) | Adds an `agent` option to the same `fetch`; no signal. | No. |
| [#277](https://github.com/brave/brave-search-mcp-server/issues/277) "JSON-RPC Batch Amplification can lead to financial loss." | Issue, open | Request amplification on the HTTP transport. | No. |

Search coverage is GitHub's issue search index at the time of the query; a report worded without these terms could be missed **(unverified beyond these terms)**.

### 1.5 Security policy

- No `SECURITY.md` in the repository at `e08f5af0` (HTTP 404), and none in the organisation's `.github` repository (404 for `main` and `master`). The GitHub community profile reports no security policy file.
- The package `README.md` of 2.1.5 has no security-reporting section.
- Brave's general bug bounty programme on HackerOne exists; whether this repository is in its scope was **not** checked **(unverified)**.

## § 2 Recommendation

**File it as an issue.** The finding is present in the pin (2.1.4), in the newest release (2.1.5) and on `main` (`e08f5af0`), and no existing issue or PR covers it (§ 1.4). The fix is small and upstream already uses the same pattern in open PR #315, so a short issue that points to that pattern has a fair chance of being taken up. A +1 or comment on #315 is not enough on its own: #315 does not touch the `issueRequest` fetch, and it may be merged or closed for unrelated reasons.

Declining is a reasonable alternative if the user prefers not to open an account-linked public issue: the impact stays LOW and the finding stays tracked.

## § 3 Channel

**An ordinary public GitHub issue**, not a private security advisory and not the bug bounty programme:

1. Upstream publishes no `SECURITY.md` and no private reporting instructions for this repository (§ 1.5), so there is no stated rule that requires a private channel.
2. The impact is availability-only and LOW. The only endpoint is the fixed HTTPS host `api.search.brave.com`, run by the same vendor. A third party can trigger the hang or the memory growth only by making that endpoint, or a TLS-terminating proxy the operator configured, misbehave. There is no secret, no integrity issue and no remotely triggerable exploit to protect while a fix is prepared.
3. The behaviour is visible to anyone reading the public source; a public issue discloses nothing new.
4. Upstream treats comparable robustness topics in public (issue #277, PR #321).

## § 4 Ready-to-paste text

Everything between the two lines below is the text for upstream. It names no user, project, host, path or setup.

---

**Title:** `issueRequest`: Brave API fetch has no timeout and no response size limit

**Affected versions:** 2.1.4 and 2.1.5 (latest on npm); `main` at `e08f5af01fffb0d208995f052239d024a3721212`.

**Where:** `src/BraveAPI/index.ts`, function `issueRequest`:

- line 116: `const response = await fetch(urlWithParams, { headers });` (no `signal`);
- line 134 (success) and lines 123 and 126 (error path): `response.json()` / `response.text()` read the whole body with no size limit.

In the published package this is `dist/BraveAPI/index.js` line 103 (and 108, 112, 118). It is the only `fetch` to the Brave API, so all tools share it.

**What happens:** if the API endpoint, or a proxy in front of it, accepts the connection but stops sending, the request has no timeout of its own. Node's built-in fetch (undici) only has its default inactivity timeouts for headers and body (300 s each, per the undici documentation), and a response that keeps trickling bytes never trips them, so the tool call can stay pending indefinitely. If the endpoint returns an unexpectedly large body, it is buffered and parsed in full (after gzip decoding), which can grow the process's memory without bound.

**Impact:** low, and conditional. The endpoint is Brave's own fixed HTTPS API, so this only matters when that endpoint or the network path misbehaves. The effect is limited to availability of the server process: a hung tool call, or memory growth. When the server is used as an MCP server over stdio, the MCP client may time out its own request, but the server-side fetch keeps running.

**Suggested fix:** add a timeout to each request, combined with the MCP request's abort signal where one is available, and read the body with a byte limit. The streaming client in PR #315 already uses `AbortSignal.timeout` and `AbortSignal.any`; the same pattern fits here. A sketch:

```ts
const REQUEST_TIMEOUT_MS = 30_000;          // or configurable
const MAX_RESPONSE_BYTES = 10 * 1024 * 1024; // decoded bytes

async function readTextCapped(response: Response, maxBytes: number): Promise<string> {
  if (!response.body) return '';
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > maxBytes) {
      await reader.cancel();
      throw new Error(`Brave API response exceeded ${maxBytes} bytes`);
    }
    chunks.push(value);
  }
  return Buffer.concat(chunks).toString('utf8');
}

// in issueRequest(...), optionally taking a caller signal:
const timeout = AbortSignal.timeout(REQUEST_TIMEOUT_MS);
const signal = callerSignal ? AbortSignal.any([timeout, callerSignal]) : timeout;
const response = await fetch(urlWithParams, { headers, signal });

const bodyText = await readTextCapped(response, MAX_RESPONSE_BYTES);
if (!response.ok) {
  let detail = bodyText;
  try { detail = stringify(JSON.parse(bodyText), true); } catch { /* keep raw text */ }
  throw new Error(`${response.status} ${response.statusText}\n${detail}`);
}
return JSON.parse(bodyText) as Endpoints[T]['response'];
```

The limit and the timeout are placeholders; the right values depend on the largest legitimate responses (for example LLM context results).

**Side note, same lines:** on the error path, `response.json()` consumes the body, so when the body is not JSON the following `response.text()` should reject ("Body is unusable") and hide the real error message. Reading the body once as text and then trying `JSON.parse`, as in the sketch, avoids that.

I'm happy to test a fix or a pre-release build against these cases (a stalled response and an oversized response).

---

## § 5 What the user does

1. **Decide**: file, or decline. Nothing has been posted by any agent.
2. **To file**: open a new issue at https://github.com/brave/brave-search-mcp-server/issues/new with your own GitHub account. Paste the title and the body from § 4 (everything between the two horizontal lines, the title in the title field). Optionally re-check first that no new issue on the same topic has appeared since 2026-11-19, and that the line numbers still match `main` if it has moved past `e08f5af0`.
3. **Tell the orchestrator** one of:
   - "filed: <issue URL>". SEC-T702-08 is then recorded as reported upstream at the next tracked-debt register, and stays tracked LOW until a release with the fix is pinned, when it closes.
   - "declined". SEC-T702-08 then stays tracked LOW at the next register, with the decline recorded.
4. **Unrelated to this report, for the record**: 2.1.5 (2026-11-17) is now newer than the pin 2.1.4. Whether it resolves SEC-T702-09 is a separate check for the pin-bump work.
