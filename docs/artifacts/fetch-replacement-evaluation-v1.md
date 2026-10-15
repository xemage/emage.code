# Artifact: fetch-replacement-evaluation-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T654 (hands-on evaluation of `@playwright/mcp` as the replacement for the removed `fetch` server). **Owner**: devops-engineer. **Date**: 2026-10-15.
- **Based on**: `security-review-t646-dependency-audit-v1.md` (SEC-T646-01), `fetch-ssrf-test-t653-v1.md`
- **Also read**: `implementation/knowledge/mcp/servers.yaml`, `implementation/PREREQUISITES.md`, the tool lines of the agents in `implementation/knowledge/agents/`.
- **Decision input**: the user's decision of 2026-10-15, "Remove the fetch server and replace it by an alternative (i.e Playwright MCP Server (microsoft/playwright-mcp)) which you evaluate first."
- **Scope**: loopback only for every request (127.0.0.1, 127.0.0.2, `localhost`, `[::1]`, `[::]`, `0.0.0.0`, `*.localhost`), plus the npm registry and the browser CDN for installs. Nothing in the repository changed except this file. `servers.yaml` and all projections are untouched (T655 does that).
- **Versions tested**: `@playwright/mcp@0.0.83` (npm `latest`, published 2026-09-28; depends on exact `playwright` and `playwright-core` `1.64.0-alpha-1790635538000`), Chrome for Testing 155.0.8059.12 (Playwright `chromium` revision 1247), Node v24.19.0, npm 11.17.0, MCP SDK client 1.32.1 as the driver, Linux 6.8 x86_64, no `DISPLAY`. The server was started with the local `node` from the installed package (`node_modules/@playwright/mcp/cli.js`), driven over stdio. `--help` was also read through `npx -y @playwright/mcp@0.0.83 --help`.

## Verdict

**Playwright MCP is suitable as a page-reading tool and unsuitable as a drop-in SSRF-safe replacement for `fetch` when only its own flags are used.**

- `--blocked-origins` stops a direct navigation or sub-request to a blocked origin. It does **not** stop a redirect: an allowed page that answers `302` to a blocked loopback target reaches it, and the page content is then returned to the model. The 0.0.83 `--help` text says so ("does not serve as a security boundary and does not affect redirects"); the test confirms it for navigations and for sub-resources. This is worse than the removed server: `mcp-fetch-server@1.1.2` sent a blind GET after a redirect and never returned the body (T653). Playwright returns the body.
- A network-level egress filter (a proxy that checks the destination address at every hop) closes the redirect hole. Tested on loopback with a stand-in filter: no request reached any target in any case except one tool (see "unsafe tool" below).
- Playwright MCP is already in every install with no restriction (section 3, N). That exposure exists with or without the `fetch` decision.
- One tool, `browser_run_code_unsafe`, is on by default and cannot be switched off by any 0.0.83 flag. It runs in the server process and reaches Node's `process` (verified, section 3). Granting `mcp__playwright` as a whole server to more agents grants that.

Recommended path and alternatives are in section 5.

## 1. Coverage: who uses `fetch`, and what replaces it

### 1.1 Agents

The brief lists 11 agents. The knowledge-base frontmatter lists `mcp__fetch` for **10**: solution-architect, devops-engineer, tech-lead, frontend-developer, security-engineer, feasibility-agent, technology-scout, poc-orchestrator, integration-agent, backend-developer. `poc-security-engineer` does **not** list it (`tools: [read, search, mcp__security-audit__grep_content, mcp__poc-security-audit__scan_secrets, mcp__poc-security-audit__ref_containment, web]`). `grep` of the sources, tests and docs for the six tool names finds them only in `servers.yaml`, the 10 tool lines, their projections, and prose in old artifacts. **No agent body names a particular fetch tool**: every agent holds the whole server (all six tools). The per-agent use below is therefore inferred from the role, not read from an instruction **(inference)**.

All 10 also list `web` (the platform's built-in web tool). Four other agents already list the whole `mcp__playwright` server: qa-engineer, demo-agent, poc-qa-engineer, frontend-developer.

| Agent | Likely `fetch` use (inferred) | Tools most likely used |
|---|---|---|
| solution-architect | vendor and standards documents for ADRs | `fetch_readable`, `fetch_markdown` |
| tech-lead | library docs while reviewing | `fetch_markdown`, `fetch_readable` |
| devops-engineer | release pages, registry metadata, tool docs | `fetch_markdown`, `fetch_json` |
| frontend-developer | framework docs (also has Playwright) | `fetch_markdown` |
| backend-developer | API and library docs, schemas | `fetch_markdown`, `fetch_json` |
| integration-agent | third-party API docs, OpenAPI documents | `fetch_json`, `fetch_markdown` |
| security-engineer | advisory-database and registry JSON (T646 used the GitHub advisory REST API and `registry.npmjs.org/<pkg>/<version>`) | `fetch_json`, `fetch_txt` |
| feasibility-agent | docs and READMEs | `fetch_markdown`, `fetch_readable` |
| technology-scout | project pages, READMEs, release notes, possibly talks | `fetch_readable`, `fetch_markdown`, `fetch_youtube_transcript` |
| poc-orchestrator | incidental docs | `fetch_markdown` |

### 1.2 Tool by tool

"Verified" means seen in the loopback run (set C, no origin flags, `--headless --isolated --browser chromium`).

| `fetch_*` tool | Playwright equivalent | Gap |
|---|---|---|
| `fetch_html` | `browser_navigate`, then `browser_network_request` (index 1, `part: response-body`) for the original bytes, or `browser_evaluate` of `document.documentElement.outerHTML` for the rendered DOM | Verified that `response-body` returns the exact body. The rendered DOM differs from the source. No gap in capability. |
| `fetch_json` | `browser_navigate` to the URL. A JSON response is shown as text in the snapshot; `browser_network_request` `response-body` returns the exact bytes. The navigate result carries `HTTP status: 404 Not Found` for non-2xx (verified). | **Request headers and methods**: navigation sends a GET with browser headers only (`user-agent: ...HeadlessChrome/155...`). A custom header or POST works only through `browser_evaluate` (page `fetch`, same-origin or CORS-permitted; verified for a same-origin header) or the unsafe tool. Authenticated API calls are not practical, and that is acceptable. |
| `fetch_txt` | navigate; snapshot or `response-body` | The snapshot collapses newlines (`line one line two`); use `response-body` for exact text (verified). |
| `fetch_markdown` | none | **Gap.** No HTML-to-markdown. The model gets an accessibility-tree YAML (headings, links with `/url:`, lists; verified). Navigation and footer text are kept. More tokens, more steps, no `max_length`/`start_index` paging (`browser_find` searches the snapshot). |
| `fetch_readable` | none | **Gap.** No readability extraction. Boilerplate (`navigation`, `contentinfo`) stays in the snapshot (verified). |
| `fetch_youtube_transcript` | none | **Gap.** Not reproducible without scraping YouTube's UI, which is brittle and hits consent pages. Not tested **(unverified)**. |
| binary download | navigating to a `content-disposition: attachment` URL saves the file into the output directory and reports `Downloading file file.bin` (verified); the bytes are not returned to the model | Same as before: `fetch` returned text only. |
| JavaScript-rendered pages | yes | **Better than fetch**: a page whose script appended text had it in the snapshot (verified). |

Two usability points, both verified:
- `browser_navigate` does not return the page content inline. It returns a link to a snapshot file (`.playwright-mcp/page-<time>.yml`). The agent must `Read` that file, or call `browser_snapshot`, which returns the YAML inline. That is two steps per page instead of one.
- Output files land in `.playwright-mcp/` under the working directory (the repository), and `.playwright-mcp/` is **not** in the root `.gitignore` (checked). Page content could be committed by accident. T655 should add the ignore line (or set `--output-dir`).

### 1.3 Gaps that remain if `fetch` is removed

1. Markdown or readable extraction with paging (partly covered by the platform `web` tool where it exists; the `web` tool is platform-specific and was **not** exercised here **(unverified)**).
2. Raw JSON/API lookups with headers (Playwright covers plain GETs; the `web` tool may summarise instead of returning raw JSON **(unverified)**).
3. YouTube transcripts: no replacement.

### 1.4 Extra prerequisite: a browser

`@playwright/mcp` does not bundle a browser and does not install one on first use.

- **Default channel is Google Chrome**, not Playwright's Chromium. With the current entry (`args: ["-y", "@playwright/mcp@0.0.83"]`) on a machine without `/opt/google/chrome/chrome`, the first tool call fails: `Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome Run "npx playwright install chrome"` (verified; this machine has no Chrome). Installing Chrome needs the OS package and normally root.
- `--browser chromium` is accepted by 0.0.83 (source: `resolveBrowserParam` maps it to the `chrome-for-testing` channel) but is **not listed** in `--help` (which names chrome, firefox, webkit, msedge). It works (verified in every run here). The error it produces without the browser names the installer: ``Run `npx @playwright/mcp install-browser chrome-for-testing` ``.
- **Size.** Download from `cdn.playwright.dev`: Chrome for Testing 155.0.8059.12 zip 198,335,306 bytes (about 189 MiB); headless-shell zip 124,403,925 bytes; ffmpeg about 2.3 MiB. On disk: `chromium-1247` 399 MB, `chromium_headless_shell-1247` 270 MB, `ffmpeg-1011` 4.9 MB. `install-browser chrome-for-testing` fetched all three (about 674 MB, 19 s here, verified). `npx playwright install chromium --no-shell` (needs the `playwright` CLI) fetched only chromium plus ffmpeg (about 404 MB, 11 s, verified). Headless runs worked with the full chromium alone, so the headless shell is not needed.
- The npm side is small: 19 MB in `node_modules` (verified).
- **The revision follows the pin.** 0.0.83 needs `chromium-1247`. This machine's `~/.cache/ms-playwright` already holds `chromium-1169` and `chromium-1228`; neither is usable. Each pin bump can force a new 400-675 MB download.
- Headless: the default is **headed**. With no `DISPLAY` the run still worked (verified), but `--headless` should be explicit.
- `--isolated`: without it the profile is persistent, under `~/.cache/ms-playwright-mcp/mcp-chrome-for-testing-<hash>` (verified), and cookies and local storage carry across sessions and agents. `--isolated` keeps it in memory.
- **Sandbox**: with no flag the browser started with `--no-sandbox` (verified in the process arguments). `--sandbox` removes that argument and worked on this host (verified). It may fail in containers or hosts that block unprivileged user namespaces **(unverified there)**.
- Not covered in `PREREQUISITES.md` today: it lists Node and `npx`, no browser.

## 2. Flags in 0.0.83

Read from `npx -y @playwright/mcp@0.0.83 --help` and from the bundled source (`playwright-core/lib/coreBundle.js`).

| Flag | In 0.0.83 | Behaviour (tested unless noted) |
|---|---|---|
| `--blocked-origins <origins>` | yes, semicolon-separated | Applied as a browser-context route per entry that aborts with `blockedbyclient` (`net::ERR_BLOCKED_BY_CLIENT`). Registered after the allowlist routes, so it runs first. Help: "does not serve as a security boundary and does not affect redirects". |
| `--allowed-origins <origins>` | yes, semicolon-separated | Registers `**` as abort, then one continue route per entry. Same "not a security boundary, does not affect redirects" note. Default is allow all. |
| `--isolated` | yes | In-memory profile. |
| `--headless` | yes | Default is headed. |
| `--block-service-workers` | yes | Accepted. A service-worker page fetching a loopback target produced no request under `--blocked-origins` with or without the flag, and a request without any flags, so the origin routes cover worker requests and this flag added nothing observable here. It is cheap defence in depth. |
| `--no-sandbox` / `--sandbox` | yes | Default behaves as `--no-sandbox` (see 1.4). |
| `--no-webmcp` | yes | "do not collect or expose the tools that a page registers through the WebMCP API". Accepted and the server ran. Without it, a visited page can register tools that are exposed to the model (read from the help text; the exposure was not exercised **(unverified)**). |
| `--allow-unrestricted-file-access` | yes, off by default | `file:///etc/hostname` was refused: `Access to "file:" protocol is blocked` (verified, with and without other flags). |
| `--proxy-server`, `--proxy-bypass` | yes | See 3.5. Playwright adds `<-loopback>` so loopback also goes through the proxy (source line 40315; verified, the proxy saw loopback destinations). |
| `--browser`, `--executable-path`, `--output-dir`, `--caps`, `--config`, `--init-page`, `--init-script` | yes | `--caps` adds vision, pdf, devtools tools; not enabled here. No flag removes or excludes a tool. |

### Origin pattern syntax (from the source, then confirmed)

Each entry goes through `originOrHostGlob`:
1. `http(s)://host:*` becomes `scheme://host:*/**` (any port).
2. A string that parses as a URL with a non-null origin becomes `<origin>/**` (exact scheme, host and port; the default port is normalised away).
3. Anything else becomes `*://<entry>/**`.

Glob rules (`globToRegexPattern`): `*` matches any run of characters except `/` (so it also matches `.` and `:`), `**` matches anything, `{a,b}` is alternation (no nesting), `\` escapes; `[`, `]`, `.`, `?` are literal. There is no CIDR, no regex, no character class. Consequences:
- A bare host (`localhost`) matches only the default port. Add `localhost:*` for other ports.
- Ranges are written by brace alternation: `172.{16,17,...,31}.*`. `172.1[6-9].*` does not work (the brackets are literal).
- `10.*` matches `10.0.0.5:8080` and also `10.example.com` (harmless over-blocking).
- IPv6 is literal text: `[::1]`, `[::1]:*`, prefixes `[fe80:*`, `[fc*`, `[fd*`, `[::ffff:*`.

**Matching against the request URL as Chromium reports it.** Chromium canonicalises the host first, so `2130706433`, `0177.0.0.1`, `0x7f.1`, `127.1`, `LOCALHOST`, `127.0.0.1.`, `[0:0:0:0:0:0:0:1]` and `[::ffff:127.0.0.1]` all arrive as `127.0.0.1`, `localhost`, `[::1]` or `[::ffff:7f00:1]` and are blocked by the normal entries (verified). Two forms are **not** normalised and bypassed `127.*` and `localhost` (verified, set E): a URL with user information (`http://x@127.0.0.1:PORT/`, `http://u:pw@localhost:PORT/`) and a trailing-dot name (`http://localhost.:PORT/`). Adding `*@*`, `localhost.` and `localhost.:*` closed both (set E2). `[::]` (the unspecified IPv6 address) reaches a loopback listener with no flags (set E3) and was blocked after adding `[::]` and `[::]:*`.

### Patterns for private and link-local ranges: marked as matching-logic verification

No request was aimed at `10.*`, `192.168.*`, `169.254.*` or any real address. For those the real functions `originOrHostGlob` and `globToRegexPattern` were extracted from the pinned bundle and run on URL strings (no network). Results: `10.*` blocks `http://10.0.0.5/` and `https://10.255.255.255/x`; `192.168.*` blocks `192.168.1.1`; `169.254.*` blocks `http://169.254.169.254/latest/meta-data/` and with port 80; `172.{16..31}.*` blocks `172.16.0.1` and `172.31.255.1:81` and lets `172.15.0.1` and `172.32.0.1` through; `100.{64..127}.*` blocks `100.64.0.1` and `100.127.255.1` and lets `100.63.0.1`, `100.128.0.1` through; `0.*` blocks `0.0.0.0` and `0.1.2.3`; `[fe80:*`, `[fc*`, `[fd*` block link-local and unique-local IPv6 (including `[fd12:3456::1]`); `ws://10.0.0.1:81/` is matched (the scheme is a wildcard). `8.8.8.8`, `1.1.1.1`, `example.com` and `github.com` are not matched. The live browser behaviour of the same mechanism was tested on loopback stand-ins (`127.*`, `127.0.0.2`, `0.0.0.0`).

## 3. Hands-on SSRF test (loopback only)

### Method

Driver: a Node script (kept in the scratch directory, not in the repository) starts HTTP listeners and an MCP client over stdio against the pinned server.
- **A** on 127.0.0.1, reached as `http://a.localhost:PA`. Chromium resolves any `*.localhost` name to loopback itself, so no resolver stub is needed; `a.localhost` stands in for a public attacker origin and is left unblocked. A answers `302` per path to: `127.0.0.1:PB`, `localhost:PB`, `[::1]:PB6`, `2130706433:PB`, `0.0.0.0:PB`, `[::ffff:127.0.0.1]:PB`, `127.1:PB`, `b.localhost:PB`, `127.0.0.2:PB2`. It also serves a sub-resource page (img, script, stylesheet, iframe, `fetch`, XHR, `sendBeacon`, WebSocket), a service-worker page, a sub-resource-redirect page, JSON, text, binary and article pages.
- **B** (127.0.0.1), **B2** (127.0.0.2), **B6** (`::1`) are the targets. Each logs every request; the "B saw" column is that log.
- Every set starts a fresh server with the stated flags. Common flags: `--headless --isolated --browser chromium`. Browser: Chrome for Testing from a scratch `PLAYWRIGHT_BROWSERS_PATH`.
- Shorthand: **BL_CORE** = `localhost;localhost:*;127.*;[::1];[::1]:*;[::ffff:*;0.0.0.0;0.0.0.0:*;10.*;192.168.*;169.254.*;172.{16,...,31}.*`. **BL_REC** = BL_CORE plus `localhost.;localhost.:*;[::];[::]:*;[fc*;[fd*;[fe80:*;*@*`. `*.localhost` is left out of the live sets because it would block A itself; it was shown to work in a first run (everything under `*.localhost`, including A, returned `ERR_BLOCKED_BY_CLIENT`).

### 3.1 What Playwright MCP can reach today (no origin flags; set N, 22 cases)

The shipped entry has no restriction. With the same flags as the baseline (the real default also needs a browser, see 1.4), **B saw a request in all 22 cases**: all 9 redirects (to `127.0.0.1`, `localhost`, `[::1]`, decimal, `0.0.0.0`, IPv4-mapped IPv6, `127.1`, `b.localhost`, `127.0.0.2`), all 7 direct navigations, every sub-resource type including the WebSocket upgrade, a `browser_evaluate` `fetch`, a service worker, and the three unsafe-tool calls. For navigations the tool result names the page title and links the snapshot file, and that file contains the target's body (`SECRET-B-BODY`, seen in 17 snapshot files). So today the model can read any loopback or internal HTTP service its host can reach, and that includes cloud metadata services (by inference from the same mechanism; no such address was contacted **(unverified)**). Agents with `mcp__playwright` today are qa-engineer, demo-agent, poc-qa-engineer and frontend-developer, plus any top-level session that has all tools.

### 3.2 Results with `--blocked-origins` (sets K, U, E, E2, E3, R, F)

"Reached" = B (or B2/B6) logged a request. "Blocked" = the tool returned `net::ERR_BLOCKED_BY_CLIENT` and no request arrived.

| Case | BL_CORE (K) | BL_REC (E2/R) | Tool text on block / note |
|---|---|---|---|
| direct `127.0.0.1`, `localhost`, `[::1]`, `127.0.0.2`, decimal `2130706433`, `0.0.0.0` | blocked | blocked | `ERR_BLOCKED_BY_CLIENT at http://...` |
| direct `b.localhost` (a name that resolves to loopback) | **reached** | not run (not listed, so it would be reached) | name-based blocking cannot see what a name resolves to; with `b.localhost;b.localhost:*` added (U) it was blocked |
| direct octal `0177.0.0.1`, hex `0x7f.1`, `[0:0:0:0:0:0:0:1]`, `[::ffff:127.0.0.1]`, `127.0.0.1.`, `LOCALHOST` | blocked (E) | blocked | canonicalised by Chromium |
| direct `http://x@127.0.0.1`, `http://u:pw@localhost` (user information) | **reached** | blocked (`*@*`) | not normalised |
| direct `http://localhost.` (trailing dot) | **reached** | blocked (`localhost.`) | not normalised |
| direct `[::]` | reached (E3 control, no flags) | blocked | |
| **redirect from allowed A to any of the 9 targets** | **reached, body readable (9/9)** | **reached** | `Page URL: http://127.0.0.1:PB/r-b`, `Page Title: B-TITLE`, snapshot file holds the body |
| redirect from A to a user-information URL | not run | **reached** | |
| sub-resources of an allowed page, direct (img, script, css, iframe, fetch, XHR, beacon) | blocked | blocked | `fetch` showed `Failed to fetch` |
| **sub-resource redirects** (an `<img>` and a `fetch` on an allowed page, each redirecting to B) | not run | **reached (2 requests)** | blind, no body to the model |
| **WebSocket** `ws://127.0.0.1:PB/` from an allowed page | **reached (upgrade logged)** | reached | context routes do not cover WebSockets |
| service worker fetching B | not reached | not run | also not reached in set SWB (`--block-service-workers`) |
| `browser_run_code_unsafe`: Node `fetch()` to B | **reached, body returned** | reached | server-side, not browser traffic |
| `browser_run_code_unsafe`: `page.request.get` to B | **reached, body returned** | reached | `APIRequestContext` ignores context routes |
| `browser_run_code_unsafe`: `page.goto` to B | blocked | blocked | the page route applies |
| `file:///etc/hostname` | blocked by the file policy | blocked | independent of origins |

**Final candidate flags, set F** (BL_REC plus `100.{64..127}.*` and `0.*`, `--sandbox --block-service-workers --no-webmcp`, A unblocked): allowed article page loaded; direct `127.0.0.1`, `localhost`, `[::1]` and a user-information URL blocked, B saw nothing; redirect A to B reached (known gap).

### 3.3 `--allowed-origins` (sets W, X)

Allowlist `http://a.localhost:PA` only: A loaded; a direct navigation to B was blocked; **the redirect from A to B reached B**, page readable; of the sub-resources only the WebSocket upgrade reached B. Allowlist plus BL_CORE (X): the redirect reached B. So an allowlist alone is no better against redirects, as the help text says.

### 3.4 The unsafe tool

`browser_run_code_unsafe` is exposed by default (capability `core`; no flag removes it). Its own description says "executes arbitrary JavaScript in the Playwright server process and is RCE-equivalent". It runs in a `vm` context with `fetch`, `Buffer`, `URL` and timers exposed, and the page object. A read-only check showed that `page.constructor.constructor('return process')()` returns the real Node process (`node 24.19.0`, `pid` a number, `mainModule` an object), so the sandbox is escapable. Nothing beyond reading the version was executed. This bypasses every origin flag and every proxy setting, apart from `page.request` which does follow `--proxy-server` (see 3.5).

### 3.5 Network-level filtering through `--proxy-server` (sets P, P2, P3)

A loopback proxy was used as the egress filter. Test-only simplification: `a.localhost` is mapped to the loopback listener A and allowed (the stand-in for a public host); every other destination is checked as an IP literal and refused if loopback, private, link-local, unspecified, mapped or unique-local; any `localhost`/`*.localhost` name is refused without a lookup; all other names are refused without a DNS lookup (so no external name was resolved by the proxy). The proxy never connected to anything but A.

Result with no origin flags, only `--proxy-server http://127.0.0.1:PP`:
- A loaded through the proxy (`ALLOW`).
- **All 9 redirect targets, all 7 direct navigations, all sub-resources of an allowed page (including the WebSocket upgrade), the sub-resource redirects (P3), a `browser_evaluate` `fetch`, the service worker, and the unsafe tool's `page.request.get` and `page.goto` (P2): B saw no request.** The browser showed `HTTP status: 403 Forbidden` from the proxy, and the proxy log shows every hop, including the redirected ones, with `BLOCK`.
- Still reached: only the unsafe tool's Node `fetch()` (not browser traffic, so it does not use the proxy).

This is the control that works at every redirect hop because it acts on connections, not on URLs. A production filter must resolve the name itself and connect to the address it vetted (otherwise DNS rebinding remains); that was **not** built or tested **(unverified)**.

### 3.6 Observation: background browser traffic

In the proxy runs, Chrome for Testing sent `CONNECT` requests to `update.googleapis.com:443`, `accounts.google.com:443`, `www.google.com:443` and `android.clients.google.com:443`. The test proxy refused all of them. In the runs without a proxy the browser presumably made the same connections; they were not visible and not blocked **(unverified)**. The task's loopback-only rule applied to the requests this evaluation made; these are the browser's own background connections. Installs behind a strict egress policy should expect them.

## 4. Answers to the four questions, in brief

1. **Coverage.** 10 agents (not 11) hold `mcp__fetch`; none of their instructions names a particular fetch tool. Playwright can navigate, snapshot, find text, list and read network responses (exact bytes), and evaluate page script. Gaps: markdown and readable extraction, YouTube transcripts, custom request headers or methods (only through `browser_evaluate` or the unsafe tool), and one extra step per page to read the snapshot file. Extra prerequisite: a browser (Chrome for Testing, 189 MiB download, 404-674 MB on disk, revision tied to the pin), headless and isolated set explicitly.
2. **Flags.** All five confirmed in 0.0.83, plus `--no-webmcp`, `--sandbox`, `--proxy-server`. Origins are context routes with the glob rules in section 2. They apply to navigations and sub-requests, not to redirects, WebSockets or the unsafe tool, and they miss user-information and trailing-dot forms unless listed.
3. **SSRF.** Section 3. Without flags every target is reachable with body. With `--blocked-origins` direct access is blocked, redirect access is not. A proxy egress filter blocked everything except the unsafe tool's Node `fetch()`.
4. **Recommendation.** Section 5.

## 5. Recommendation

### 5.1 Can `fetch` be removed without a gap?

For reading HTML documentation, nearly: Playwright (or the platform `web` tool, listed by all 10 agents) covers it. **Not without a gap** for (a) markdown/readable extraction with paging, (b) raw JSON calls with request headers (security-engineer's advisory and registry lookups), (c) YouTube transcripts. These are capability losses, not security issues.

### 5.2 Exact `args` for the `playwright` entry (flags-only hardening)

Pinned version kept (0.0.83 is the npm `latest`). Apply this to the existing entry whatever else is decided, because it strictly narrows what the entry reaches today:

```yaml
args:
  - "-y"
  - "@playwright/mcp@0.0.83"
  - "--headless"
  - "--isolated"
  - "--browser"
  - "chromium"
  - "--sandbox"
  - "--block-service-workers"
  - "--no-webmcp"
  - "--blocked-origins"
  - "localhost;localhost:*;localhost.;localhost.:*;*.localhost;*.localhost:*;127.*;0.*;10.*;100.{64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127}.*;169.254.*;172.{16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31}.*;192.168.*;[::];[::]:*;[::1];[::1]:*;[::ffff:*;[fc*;[fd*;[fe80:*;*@*"
```

Tested pieces: every flag except the full string as one unit. The live runs used BL_REC plus `--sandbox --block-service-workers --no-webmcp` (set F) with `*.localhost` omitted (it would block the test origin); `*.localhost` was verified separately; `100.{64..127}.*` and `0.*` were verified by matching logic only. The string is one argument with semicolons; it was passed without a shell. Clients that route `args` through a shell, and Windows, were not tested **(unverified)**; `PLAYWRIGHT_MCP_BLOCKED_ORIGINS` or `--config` (`network.blockedOrigins`) are alternatives that avoid quoting.

What this does **not** do: stop redirects, WebSockets, DNS names that resolve to internal addresses (`b.localhost` was the stand-in), or the unsafe tool.

### 5.3 Per-tool grants, not the whole server

Do not give the 10 agents `mcp__playwright` (the whole server): it includes `browser_run_code_unsafe` (host-level code execution), and the project classifies tech-lead (during review) and security-engineer (during audit) as read-only; security-engineer has no `execute` tool at all. Granting it the server would give it more than `execute`. If any agent gets Playwright, list tools by name, in the form the security-engineer line already uses (`mcp__security-audit__run_npm_audit`): `mcp__playwright__browser_navigate`, `browser_snapshot`, `browser_find`, `browser_wait_for`, `browser_network_requests`, `browser_network_request`, `browser_close`. Whether each of the seven platform projections honours per-tool names for this server was not checked **(unverified)**. Also add `.playwright-mcp/` to the root `.gitignore`.

### 5.4 Options for the user

| # | Option | Closes SEC-T646-01? | Cost and limits |
|---|---|---|---|
| **A (recommended)** | Remove `fetch`. Do **not** add `mcp__playwright` to the 10 agents. Agents use the platform `web` tool (already listed). Apply the 5.2 flags to the existing `playwright` entry, add `.playwright-mcp/` to `.gitignore`, and add a browser step to `PREREQUISITES.md`. | Yes, by removal. No new redirect exposure. | Loses raw JSON with headers, markdown paging and YouTube transcripts; the `web` tool's own SSRF behaviour is platform-dependent and was not tested **(unverified)**. The four agents that have the whole `mcp__playwright` server keep the unsafe tool; narrowing them is a follow-up. |
| B | Replace `fetch` by `playwright` for the 10 agents with the 5.2 flags and per-tool grants (the literal request). | **No.** An attacker page redirects to loopback/internal/metadata and the content is returned to the model (worse than the removed server's blind GET). Grade at least MEDIUM, likely HIGH, with a documented residual. Not recommended as the only control. | Works for reading pages; gaps in 1.3; browser prerequisite. |
| C | B plus an egress-filtering proxy through `--proxy-server` (a small loopback proxy, or squid with a destination-IP deny list). Tested design in 3.5. | Yes for all browser traffic; the unsafe tool stays out of the agents' lists. | Needs a component that is not in the install today (the entry cannot start it; a wrapper command or a documented service is required), real DNS handling (resolve and connect to the vetted address), and its own test. New task; would delay the release unless A ships first. |
| D | Replace with the official `mcp-server-fetch` (Python, `uvx`; `uvx` is already a prerequisite for `mcp-server-git`). Its README now states a private-IP guard (`--allow-private-ips` disables it) and says it "does not protect against DNS rebinding between that check and the connection". | Unknown | One tool only (markdown, `raw` option), no JSON or YouTube tools. Redirect behaviour not tested **(unverified)**; needs a T653-style test first. |
| E | Keep `mcp-fetch-server@1.1.2` but move it to `extended` (opt-in) with the T653 result documented. | Reduced exposure (opt-in), not closed. | Leaves the blind-GET behaviour for those who opt in. |

Recommendation: **A now, C as the follow-up if the user wants Playwright-based reading for the 10 agents.** The user's decision named Playwright as the replacement; the evaluation finds it unsuitable for that role on flags alone, so this is the plain statement the brief asked for.

### 5.5 Residual risks of any Playwright configuration

- A browser is a larger attack surface than a fetch tool: a full renderer with JavaScript, WebSockets, downloads and the Chromium CVE stream. The version is tied to the Playwright pin, so browser patches arrive only at pin bumps. The `playwright` alpha builds have no npm provenance coverage (SEC-T646-03).
- Prompt-injected pages: any page the agent opens can contain instructions. Playwright snapshots feed page text straight to the model, `--no-webmcp` removes one channel, and nothing here filters page text.
- The unsafe tool remains in the server for any caller that is allowed it.
- Downloads from visited pages land in `.playwright-mcp/`.
- Chrome for Testing background connections to Google hosts (3.6).
- `--sandbox` depends on the host; falling back to the default means no browser sandbox.

## 6. Limits

- L-1: Chromium (Chrome for Testing) only; Firefox and WebKit were not tested. One run per set on one platform (Linux, Node v24.19.0). Windows, macOS, containers and clients that spawn through a shell are untested.
- L-2: `a.localhost` stands in for a public origin; DNS names that really resolve to internal addresses and DNS rebinding were not tested. The `b.localhost` cases show the class, not a rebinding attack.
- L-3: The egress-filter proxy is a test stand-in; it does not resolve names. A production filter was not built.
- L-4: The ranges `10.*`, `192.168.*`, `169.254.*`, `172.16-31`, `100.64/10`, `0.*` and the IPv6 prefixes are verified by matching logic only; the in-browser behaviour was shown with `127.*`, `127.0.0.2`, `0.0.0.0`, `[::1]`, `[::]` and `[::ffff:*`.
- L-5: The `web` tool of each platform, per-tool grants across the seven projections, YouTube transcripts, PDF and `--caps` tools, token cost of large pages, and the WebMCP exposure were not exercised.
- L-6: The server was run from the installed package with `node`, as `npx -y` would run the same files; the real client path (a coding agent spawning `npx`) was not used.
- L-7: `npm audit` for the 3 packages reported 0 vulnerabilities at install; no provenance check was repeated (T646 covers it).
- L-8: The browsers were installed into a scratch directory (not `~/.cache/ms-playwright`) and deleted afterwards. Other `@playwright/mcp@latest` servers on this machine belong to other sessions and were not touched.

## 7. Cleanup

Listeners lived inside the driver and closed on exit; each MCP server was closed by its client; a process listing after the last run showed no `chrome-linux64` and no test server left. Scratch directory: `/tmp/claude-1000/-home-emage-Code-emage-emage-code/00f8372f-6371-46d2-9fa7-bac00c806f40/scratchpad/t654` (outside the repository; the scripts and run logs stay there, the downloaded browsers were removed).

## 8. Notes for T655 (if option A or B is chosen)

- Tool lines of the 10 agents: solution-architect, devops-engineer, tech-lead, frontend-developer, security-engineer, feasibility-agent, technology-scout, poc-orchestrator, integration-agent, backend-developer. `poc-security-engineer` needs no change. The count in T655's brief should read 10.
- Files that name the server: `servers.yaml`, `tests/functional/test_mcp_package_pins.py`, `tests/functional/test_cross_references.py`, `tests/functional/test_placeholder_flag_text.py`, `tests/functional/test_audit_server.py`, the agent projections under `implementation/.*/`, and the generated `.mcp.json` files.
- `APPROVED_NPX_PINS` and the policy text in `PREREQUISITES.md` are touched by any change of the `playwright` args or the removal of `fetch`.
