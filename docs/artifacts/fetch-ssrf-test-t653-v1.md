# Artifact: fetch-ssrf-test-t653-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T653 (evidence for the re-grade of SEC-T646-01). **Owner**: devops-engineer. **Date**: 2026-10-15.
- **Based on**: `security-review-t646-dependency-audit-v1.md`
- **Decision input**: the user's decision of 2026-10-15, "Test first, then decide (Recommended)".
- **Scope**: loopback only (127.0.0.1, `localhost`) plus the npm registry for the install. No external host, no link-local or internal address was contacted. Nothing written to the repository except this file.

## Result

**B saw a request after a redirect: yes.**

When the first URL passes the guard, `mcp-fetch-server@1.1.2` follows a `302` to a loopback target and sends the GET before it checks the final URL. The tool then returns an error, and the body of B is not returned. The pre-request guard blocks every loopback URL given directly, including `localhost`. Per the T646 disposition, this means SEC-T646-01 stays at MEDIUM and the fix options (move to extended, remove, replace) go to the user.

One caveat shapes how to read this. A plain loopback server A cannot be the first URL, because the first-URL guard blocks it before any request (case 1 below). So the redirect cases that reach B use a stub (the "s" cases, described in "Method"). The stub stands in for a public origin, which the test may not contact.

## Versions

| Item | Version |
|---|---|
| Node.js | v24.19.0 |
| npm | 11.17.0 |
| `mcp-fetch-server` | 1.1.2 (exact, `npm install --save-exact`) |
| `private-ip` | 3.0.2 (with `ip-regex@5.0.0`, `netmask@2.1.1`) |
| `@modelcontextprotocol/sdk` (client used to drive it) | 1.32.1 |

The package's own entry point was run with the local `node` (not docker, not the remote daemon): `node node_modules/mcp-fetch-server/dist/index.js`, driven over stdio MCP. The tool used was `fetch_txt`; the same `Fetcher._fetch` serves `fetch_html`, `fetch_json`, `fetch_markdown` and `fetch_readable`. Tools listed: `fetch_html, fetch_markdown, fetch_txt, fetch_json, fetch_readable, fetch_youtube_transcript`.

## Method

Commands (scratch directory outside the repository, scripts kept in a separate directory):

```
npm init -y && npm install --save-exact mcp-fetch-server@1.1.2
node run.mjs plain     # no resolver stub
node run.mjs stub      # resolver stub preloaded into the package process
```

The driver process starts three HTTP listeners on 127.0.0.1 with ephemeral ports. Each logs every request it receives.
- **A**: answers `302` with a `Location` header. `/to-b` goes to `http://127.0.0.1:PB/redirected`, `/to-b2` to `http://127.0.0.1:PB2/redirected2`, `/to-localhost` to `http://localhost:PB/redirected-localhost`.
- **B** and **B2**: answer 200 with a fixed body.

The package source (`dist/index.js`, `Fetcher._fetch`) works in this order:
1. `validateUrl(url)` checks the protocol and tests `localhost` or `private-ip(hostname)` on the hostname string.
2. `validateResolvedIp(url)` does a `dns.promises.lookup` and tests `private-ip(address)`.
3. `fetch(url)` with the default redirect mode `follow`.
4. Only after the response: if `response.url !== url`, it runs `validateUrl` and `validateResolvedIp` on the final URL.

So any loopback URL passed directly is blocked at step 1, and A on a literal loopback address cannot be the first URL.

The "s" cases (stub mode) use hostname `a.test` for A, through a test-only preload (`node --import preload.mjs`). The preload does two things:
- It makes the guard's `dns.promises.lookup("a.test")` answer `8.8.8.8` (a value only; never connected to). This makes A look like a public origin to the guard.
- It makes the connect-time `dns.lookup("a.test")` answer `127.0.0.1`, so the traffic goes to the local A.

A safety net in the preload refuses any socket connect whose host is not `127.0.0.1`, `localhost`, `::1` or `a.test` (it never fired). The stub is the only deviation from a real attack, where A would be a genuine public attacker URL (or an attacker-controlled page the model is induced to fetch).

## Results

B's request log is the log of the listener that the redirect targets (B, or B2 for case 4). A log is the log of A.

| Case | First URL | Tool result | A log | B log | B saw a request |
|---|---|---|---|---|---|
| 1 redirect to loopback, A on literal 127.0.0.1 | `http://127.0.0.1:PA/to-b` | `Fetcher blocked request to private address "127.0.0.1"` | empty | empty | no (blocked before any request) |
| 1s redirect to loopback, A passes the guard (stub) | `http://a.test:PA/to-b` | `Fetcher blocked request to private address "127.0.0.1"` | `GET /to-b host=a.test:PA` | `GET /redirected host=127.0.0.1:PB` | **yes** |
| 2 direct fetch of B | `http://127.0.0.1:PB/direct` | `Fetcher blocked request to private address "127.0.0.1"` | empty | empty | no |
| 3 hostname `localhost`, direct | `http://localhost:PB/via-localhost` | `Fetcher blocked request to private address "localhost"` | empty | empty | no |
| 3s redirect whose Location is `localhost` (stub) | `http://a.test:PA/to-localhost` | `Fetcher blocked request to private address "localhost"` | `GET /to-localhost host=a.test:PA` | `GET /redirected-localhost host=localhost:PB` | **yes** |
| 4 redirect to loopback on a different port, A literal | `http://127.0.0.1:PA/to-b2` | `Fetcher blocked request to private address "127.0.0.1"` | empty | B2 empty | no (blocked before any request) |
| 4s redirect to loopback on a different port B2 (stub) | `http://a.test:PA/to-b2` | `Fetcher blocked request to private address "127.0.0.1"` | `GET /to-b2 host=a.test:PA` | B2: `GET /redirected2 host=127.0.0.1:PB2`; B: empty | **yes** |

Ports differ per run (plain run: A 43305, B 35487, B2 36785; stub run: A 36829, B 39379, B2 39375). Every tool result was an MCP error (`isError`), and no body of B or B2 appeared in any result.

Observations:
- The guard blocks loopback URLs given directly, and it blocks the name `localhost`. It does not block a loopback target reached by redirect: the request is sent and the response is rejected afterwards. This matches the source reading in SEC-T646-01.
- The impact shown here is a blind GET to the redirect target with the caller's request headers (the default User-Agent, plus any `headers` the caller supplies). The response body is not returned to the caller. The redirected GET is also sent when the target is `localhost` by name.
- A different port on loopback is no obstacle (case 4s), since the guard never sees the redirect target before the request.

## Limits

- L-1: Only loopback was tested. A redirect to a link-local address (for example a cloud metadata address) was deliberately not tested against any real address. The same code path applies by reading `_fetch`, but that is inference, not a test **(unverified)**.
- L-2: The first URL passing the guard was simulated with the resolver stub; a real public origin was not used, by design. The result for "A passes the guard" rests on the stub's fidelity: the guard only checks `private-ip` of the resolved address, and the stub returns a public value for it.
- L-3: DNS rebinding (the resolve-then-fetch gap) was not tested as such. The stub in effect simulates a rebinding answer for A, which is not the same as a timed rebinding attack **(unverified)**.
- L-4: One run per mode, one platform (Linux, Node v24.19.0), the `fetch_txt` tool only. `proxy` and `headers` arguments were not exercised. The `private-ip` multicast advisory (GHSA-9h3q-32c7-r533) was not tested.
- L-5: The package was run with `node`, as the T646 entry does through `npx`; the README's Bun-specific `proxy` option has no effect on Node and was not tested.
- L-6: `npm install` reported dependency issues needing review ("Run `npm audit` for details"); `npm audit` was not run or evaluated here (out of scope).

## Cleanup

The three listeners lived inside the driver process and were closed on exit; the MCP child process was closed by the client; a process listing afterwards showed none left. The scratch directory is under the session scratchpad, outside the repository.
