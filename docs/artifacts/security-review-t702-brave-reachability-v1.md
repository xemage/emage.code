# Artifact: security-review-t702-brave-reachability-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer. Read-only; no shell, so the reachability was judged from the upstream source at tag v2.1.4 (GitHub) and the advisories, not by running the server. Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-11-01.
- **Target**: `@brave/brave-search-mcp-server@2.1.4` as shipped (`implementation/knowledge/mcp/servers.yaml:147-149`: `npx -y @brave/brave-search-mcp-server@2.1.4`, only `BRAVE_API_KEY` in its environment), for the user's decision on renewing the acceptance SEC-T676-02 (task T702, plan-124).
- **Based on**: `docs/artifacts/mcp-pin-audit-v9-v1.md` (T702, §3.1); `brave-audit-acceptance-v2.md`; `security-review-t676-supply-chain-v1.md`; `scripts/audit-mcp-pins.py`; `tests/functional/test_mcp_package_pins.py`; the advisories GHSA-f897-62hf-6gxq, GHSA-mrhx-c7xc-m3w5, GHSA-46jr-4wx8-v453; the Brave server source at tag v2.1.4 (`src/config.ts`, `src/BraveAPI/index.ts`, `src/protocols/http.ts`).

## Verdict: CONDITIONAL_PASS

No `CRITICAL` or `HIGH` finding remains in the shipped mode. No Immutable Security Constraint is breached (dependency findings are not one). Renewing the acceptance is defensible with the conditions below; removal is not needed on security grounds.

The attacker inputs considered: tool arguments, written by the user's own assistant over stdio (shapeable by prompt injection, bounded by the model's output size), and Brave API responses (`await response.json()` cast without zod validation, so a malicious search result reaches neither zod nor the SDK schema checks).

## Grades

| Id | Advisory | Package@version (fixed in) | Reachable as shipped (stdio) | Grade |
|---|---|---|---|---|
| SEC-T702-01 | GHSA-f897-62hf-6gxq: HTTP transports put no limit on body size or batch length | `@modelcontextprotocol/sdk@1.30.0` (1.30.1) | No: "Servers that only use stdio are not affected"; HTTP path only with `--transport http` or `BRAVE_MCP_TRANSPORT=http` | LOW |
| SEC-T702-02 | GHSA-mrhx-c7xc-m3w5: zod keeps every issue per failing array element (memory) | `zod@4.3.6` (4.6.6) | Code path yes (unbounded tool-input arrays: web `result_filter`, `goggles`, local `ids`), harmful use no: only trusted client input; impact at most a crash of the local helper | LOW |
| SEC-T702-03 | GHSA-46jr-4wx8-v453: one HTTP request exhausts memory during validation | sdk@1.30.0 (1.32.0) | No: "stdio-only servers are not affected" | LOW |
| SEC-T702-04 | GHSA-6qxp-vccf-f47h: OAuth client sends credentials to a server-chosen authorization server | sdk@1.30.0 (1.31.0) | No: no `client/auth` code outside tests | LOW |
| SEC-T702-05 | GHSA-22jm-h49p-29qw: experimental tasks not tied to their session | sdk@1.30.0 (1.32.0) | No: no tasks API outside tests | LOW |
| SEC-T702-06 | GHSA-6prh-2h8m-c8cw (npm: moderate) and GHSA-rvq5-wwqv-78pq (npm: moderate) | sdk@1.30.0 (1.32.0) | No: no SDK HTTP client, OAuth or bearer auth; Brave calls use Node's `fetch` | LOW |
| SEC-T702-07 | An environment variable (`BRAVE_MCP_TRANSPORT`) or a `.env` file in the launch directory (`dotenv.config()`) can switch the server to an unauthenticated HTTP listener, reopening SEC-T702-01/-02/-03 over HTTP; with `BRAVE_MCP_HOST=0.0.0.0` it would expose a search proxy spending the user's Brave key | servers.yaml entry | Fix: launch with `--transport stdio` (a CLI flag overrides the env default, read from `config.ts`, unverified) and require that form in the pin test | LOW |
| SEC-T702-08 | Brave API fetches have no timeout or response size cap (upstream code) | `src/BraveAPI/index.ts` | Fixed, trusted HTTPS endpoint; hang or memory risk only if it misbehaves | LOW (track; report upstream) |
| SEC-T702-09 | The pin ships seven known advisories with no newer release; the fix exists on upstream `main` (sdk 1.32.2, zod 4.6.7), unpublished (unverified) | the pin | Remediation plan: the v3 acceptance with its re-audit triggers | MEDIUM (as SEC-T676-02) |

## Recommended conditions for a renewal (v3)

1. Scope: all seven ids, each scoped to `@brave/brave-search-mcp-server@2.1.4`.
2. Expiry: the earlier of the first Brave release above 2.1.4 and a date at most 90 days from the gate run (`scripts/audit-mcp-pins.py:257` refuses more).
3. Stdio only: no `--host`, `--port` or `BRAVE_MCP_*` in `servers.yaml`, the shell environment or a `.env` file of a launch directory; preferably the explicit `--transport stdio` (SEC-T702-07) with its test.
4. Re-audit at any Brave release above 2.1.4, any new advisory on sdk 1.30.0 or zod 4.3.6 affecting stdio or tool-input validation, any change to the `brave` entry, and the expiry; the gate passes `--accept` only for these seven ids.
5. Only the user can renew.

**Outcome.** The user, 2026-11-01 (AskUserQuestion, verbatim option label): "Renew + force stdio (Recommended)": the renewal with the expiry 2027-01-30 or the first Brave release above 2.1.4, and SEC-T702-07 fixed in v9.0.0 (task T712).

## Unverified

- The GitHub tag source is assumed identical to the npm tarball (the earlier tarball read for SEC-T676-02 supports it for imports).
- The zod schemas of the images, news, videos, summarizer, llm_context and place_search tools were not checked; the same reasoning applies to any unbounded array there.
- The output-size limits and memory estimate behind SEC-T702-02 are reasoning, not measured.
- Express's default body limit in Brave's HTTP mode; the DNS-rebinding guard with an empty `BRAVE_MCP_ALLOWED_ORIGINS`.
- That `--transport stdio` overrides the environment and the `.env` file; which directory clients launch stdio servers from; whether a server switched to HTTP keeps running after the stdio connection fails.
- That upstream `main` carries the fixed library versions without a release.
