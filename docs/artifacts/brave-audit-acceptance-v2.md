# Artifact: brave-audit-acceptance-v2.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: devops-engineer (T676 for v1; T685 for v2). **Date**: 2026-10-22. **Owner**: devops-engineer.
- **Revision**: v2 changes the SYNTAX of the gate command only, for review finding SEC-T676-11 (T685): `--accept` now takes `GHSA-...:YYYY-MM-DD:<package>@<version>` and the script refuses an expiry more than 90 days from the day of the run, a package@version that is not a current pin and a duplicate. The decision, the advisories, the reasoning, the conditions and the expiry are unchanged and still the user's of 2026-10-22; v1 stays as the original record (`brave-audit-acceptance-v1.md`, whose command no longer runs).
- **Decision**: the user, 2026-10-22, AskUserQuestion on the T676 security-review finding SEC-T676-02, answer: "Accept with conditions (Recommended)".
- **Based on**: `brave-audit-acceptance-v1.md`, `docs/artifacts/security-review-t676-supply-chain-v1.md` (SEC-T676-11), the T676 security review of 2026-10-22 (CONDITIONAL_PASS, finding SEC-T676-02; the review text is recorded by the orchestrator), `docs/wiki/mcp-pin-bump-checklist.md` (section 5, run of 2026-10-22), `implementation/knowledge/mcp/servers.yaml` (`brave`), and the five advisories below.
- **Expires**: the earlier of (a) the first release of `@brave/brave-search-mcp-server` above 2.1.4 and (b) **2026-11-21** (30 days). After either, `python3 scripts/audit-mcp-pins.py audit --audit-level high` must pass without `--accept` for these ids, or a new version of this artifact must renew the decision with the user.

## What is accepted

`python3 scripts/audit-mcp-pins.py audit` (2026-10-22) reports two `high` findings for the pinned `@brave/brave-search-mcp-server@2.1.4` (the latest release): the package depends on `@modelcontextprotocol/sdk` at exactly `1.30.0`, which five advisories mark vulnerable (fixed in 1.31 or 1.32):

| Advisory | Title | Range |
|---|---|---|
| GHSA-6qxp-vccf-f47h | OAuth client could send credentials to an authorization server chosen by the MCP server | `>=1.12.0 <1.31.0` |
| GHSA-22jm-h49p-29qw | Experimental tasks were not tied to the session that created them | `>=1.24.0 <1.32.0` |
| GHSA-6prh-2h8m-c8cw | HTTP client transports and OAuth requests followed cross-origin redirects and re-sent custom headers and request bodies | `<1.32.0` |
| GHSA-46jr-4wx8-v453 | One HTTP request within the default size limit could exhaust server memory during validation | `>=1.3.0 <1.32.0` |
| GHSA-rvq5-wwqv-78pq | Server bearer authentication accepted tokens issued for another service | `>=1.6.0 <1.32.0` |

## Reasoning

1. The shipped entry launches the server over **stdio** (`npx -y @brave/brave-search-mcp-server@2.1.4`, no transport flag, only `BRAVE_API_KEY` in the environment). The package defaults to `--transport stdio` (`dist/config.js`).
2. **Four of the five need code the package does not contain.** The 2.1.4 tarball was unpacked into an empty directory and read, never executed (`npm pack`, then `tar`): outside its test files it has no use of `taskStore` or the experimental tasks API (GHSA-22jm), no `requireBearerAuth`, `verifyBearerToken` or any bearer or Authorization handling (GHSA-rvq5), no SDK client transport (`StreamableHTTPClientTransport`, `SSEClientTransport`) and no `client/auth` OAuth code (GHSA-6qxp, GHSA-6prh). The SDK client is imported only by `dist/testUtils/mcpTestHarness.js` and `dist/protocols/stdio.test.js`. The server imports `server/mcp.js`, `server/stdio.js` and `server/streamableHttp.js`.
3. **GHSA-46jr (memory exhaustion by one HTTP request) applies only when the HTTP transport runs.** It is reachable only with `--transport http` or the environment variable `BRAVE_MCP_TRANSPORT=http` (the package also reads `BRAVE_MCP_PORT`, `BRAVE_MCP_HOST`, `BRAVE_MCP_ALLOWED_ORIGINS`, `BRAVE_MCP_ALLOWED_HOSTS`, `BRAVE_MCP_STATELESS`, and loads a `.env` file from the launch directory through `dotenv`). The default HTTP bind is `127.0.0.1`.
4. No newer brave release exists to move to (2.1.4 is `latest`), and removing the server would drop web search for agents (the server is exempt from the per-agent denial by the user decision of 2026-10-16).

## Conditions

- The `brave` entry keeps the stdio form: no `--transport`, `--host`, `--port` argument and no `BRAVE_MCP_*` variable in `servers.yaml` (pinned by `tests/functional/test_mcp_package_pins.py`).
- **An operator who sets `BRAVE_MCP_TRANSPORT=http` in the environment or in a `.env` file of the launch directory reopens GHSA-46jr-4wx8-v453** for as long as the pin is 2.1.4. Do not set it.
- The release gate command uses the acceptance list and nothing broader: `python3 scripts/audit-mcp-pins.py audit --audit-level high --accept GHSA-6qxp-vccf-f47h:2026-11-21:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-22jm-h49p-29qw:2026-11-21:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-6prh-2h8m-c8cw:2026-11-21:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-46jr-4wx8-v453:2026-11-21:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-rvq5-wwqv-78pq:2026-11-21:@brave/brave-search-mcp-server@2.1.4`. An accepted id is still printed as ACCEPTED; an expired acceptance fails the audit. Each acceptance is scoped to the pinned package it was reviewed for (SEC-T676-11): it counts only when that package is the only pinned package the vulnerable `@modelcontextprotocol/sdk` entry puts at risk, so a second pin that pulls the same library stays a finding; a bump of the brave pin voids all five (the script refuses a package@version that is not a current pin), and an expiry more than 90 days from the day of the run is refused (the 30-day expiry here is within it).
- Re-read this decision at every `brave` release and at the expiry.

## Limits

L-1 the five advisories were read from their titles and ranges in the npm advisory feed, not from the upstream patches. L-2 the tarball was searched by text and import list (`grep`), not by a call-graph analysis; minified or dynamically built names would be missed (the files are unminified TypeScript output). L-3 nothing was run, so the stdio default was read from `dist/config.js`, not observed.
