# Artifact: brave-audit-acceptance-v3.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: devops-engineer (T676 for v1; T685 for v2; T712 for v3). **Date**: 2026-11-01. **Owner**: devops-engineer.
- **Revision**: v3 renews the acceptance with the user and widens it from five to **seven** advisories. T702 (`docs/artifacts/mcp-pin-audit-v9-v1.md`, section 3.1) found two further advisories on the same pin, `GHSA-f897-62hf-6gxq` (`@modelcontextprotocol/sdk`) and `GHSA-mrhx-c7xc-m3w5` (`zod`), so the v2 gate command no longer passes. v3 also forces the stdio transport in the shipped launch arguments (SEC-T702-07). v2 stays as the record of the decision of 2026-10-22 (`brave-audit-acceptance-v2.md`; its command no longer passes and its expiry, 2026-11-21, is replaced by the one below).
- **Decision**: the user, 2026-11-01, AskUserQuestion after the Security Engineer grading of T702. The option label and its description, verbatim (quoted from `docs/tasks/task-T712.md`, section 1): "Renew + force stdio (Recommended)" — "Accept as stated AND add '--transport stdio' to the shipped brave launch args (with its test) in v9.0.0, so no env var or .env file can switch it to HTTP. Changes the generated configs (one more root refresh before the release branch)." The question stated the scope: "all 7 advisories of @brave/brave-search-mcp-server@2.1.4 (6qxp, 22jm, 6prh, 46jr, rvq5, f897, mrhx), none reachable harmfully in stdio mode (Security Engineer). Expiry: the first Brave release above 2.1.4 or 2027-01-30, whichever is first (the script allows at most 90 days). Condition: stdio only, never the HTTP transport." The earlier answer of the same day was "Grade, then renew (Recommended)" (`docs/plans/plan-124-release-v9.md`, Addendum of 2026-11-01).
- **Based on**: `brave-audit-acceptance-v2.md`; `docs/artifacts/mcp-pin-audit-v9-v1.md` (T702, section 3.1); the Security Engineer grading of 2026-11-01, `docs/artifacts/security-review-t702-brave-reachability-v1.md` (SEC-T702-01 to SEC-T702-09); `docs/tasks/task-T712.md`; `docs/plans/plan-124-release-v9.md` (task T712 and the Addendum of 2026-11-01); `implementation/knowledge/mcp/servers.yaml` (`brave`); the `dist/config.js` and `dist/index.js` of the `@brave/brave-search-mcp-server@2.1.4` tarball (read on 2026-11-01, not run).
- **Expires**: the earlier of (a) the first release of `@brave/brave-search-mcp-server` above 2.1.4 and (b) **2027-01-30**. After either, `python3 scripts/audit-mcp-pins.py audit --audit-level high` must pass without `--accept` for these ids, or a new version of this artifact must renew the decision with the user. `scripts/audit-mcp-pins.py` refuses an expiry more than 90 days from the day of the run (2027-01-30 is 90 days after 2026-11-01).

## What is accepted

`python3 scripts/audit-mcp-pins.py audit --audit-level high` without `--accept` (T702, 2026-11-01) fails, and every high finding comes from the pinned `@brave/brave-search-mcp-server@2.1.4`, still the newest release. It depends on `@modelcontextprotocol/sdk` at exactly `1.30.0` and on `zod` at exactly `4.3.6`; seven advisories apply to the pin:

| Advisory | Package | Title | Range | Fixed in | npm grade |
|---|---|---|---|---|---|
| GHSA-6qxp-vccf-f47h | `@modelcontextprotocol/sdk` | OAuth client could send credentials to an authorization server chosen by the MCP server | `>=1.12.0 <1.31.0` | 1.31.0 | high |
| GHSA-22jm-h49p-29qw | `@modelcontextprotocol/sdk` | Experimental tasks were not tied to the session that created them | `>=1.24.0 <1.32.0` | 1.32.0 | high |
| GHSA-6prh-2h8m-c8cw | `@modelcontextprotocol/sdk` | HTTP client transports and OAuth requests followed cross-origin redirects and re-sent custom headers and request bodies | `<1.32.0` | 1.32.0 | moderate |
| GHSA-46jr-4wx8-v453 | `@modelcontextprotocol/sdk` | One HTTP request within the default size limit could exhaust server memory during validation | `>=1.3.0 <1.32.0` | 1.32.0 | high |
| GHSA-rvq5-wwqv-78pq | `@modelcontextprotocol/sdk` | Server bearer authentication accepted tokens issued for another service | `>=1.6.0 <1.32.0` | 1.32.0 | moderate |
| GHSA-f897-62hf-6gxq | `@modelcontextprotocol/sdk` | HTTP server transports and handlers did not limit request body size or JSON-RPC batch length | `>=1.10.0 <1.30.1` | 1.30.1 | high |
| GHSA-mrhx-c7xc-m3w5 | `zod` | Zod can exhaust memory while validating oversized constrained collections | `<4.6.6` | 4.6.6 | high |

The first five titles and ranges are those of v2; the last two are those reported by npm on 2026-11-01 (`mcp-pin-audit-v9-v1.md`, section 3.1). Brave 2.1.4 is the only pin that pulls these versions; the other pins resolve sdk 1.32.2 and zod 4.6.7.

## Reasoning

The Security Engineer graded each advisory against the shipped stdio launch (2026-11-01). Overall finding **SEC-T702-09 (MEDIUM)**: the pin ships known advisories and no newer release exists. Per advisory:

| Advisory | Reachable in the shipped stdio mode | Security Engineer grade |
|---|---|---|
| GHSA-6qxp-vccf-f47h | No: the package contains no OAuth client code | LOW |
| GHSA-22jm-h49p-29qw | No: the package does not use the tasks API | LOW |
| GHSA-6prh-2h8m-c8cw | No: the package contains no SDK HTTP client and no OAuth code | LOW |
| GHSA-46jr-4wx8-v453 | No: the advisory says stdio-only servers are not affected | LOW |
| GHSA-rvq5-wwqv-78pq | No: the package contains no bearer authentication | LOW |
| GHSA-f897-62hf-6gxq | No: the advisory says stdio-only servers are not affected; it concerns the HTTP body and batch limits | LOW |
| GHSA-mrhx-c7xc-m3w5 | The tool-input code path is reachable, but only input from the local client reaches zod (tool arguments that prompt injection can shape, bounded by the model's output size), and Brave API responses are not zod-validated; the impact is at most a crash of the local helper process | LOW |

1. **The transport is now stdio by argument, not by default.** v2 relied on the package default (`--transport` defaults to stdio). The 2.1.4 `dist/config.js` (read, not run) defines the option as `.option('--transport <stdio|http>', 'transport type', process.env.BRAVE_MCP_TRANSPORT ?? 'stdio')` and calls `dotenv.config()` at load, so `BRAVE_MCP_TRANSPORT` in the environment or in a `.env` file of the launch directory sets the **default** of that option, and `dist/index.js` starts `httpServer` when the resolved value is `http` (SEC-T702-07). With `--transport stdio` on the command line the parsed option is `stdio` whatever the environment says (read, not run; L-3; a live check is a release-time user action), so the HTTP transport (and with it GHSA-46jr, GHSA-f897 and the HTTP path of GHSA-mrhx) stays off. The shipped arguments are therefore `["-y", "@brave/brave-search-mcp-server@2.1.4", "--transport", "stdio"]` (`implementation/knowledge/mcp/servers.yaml`, T712).
2. **Five of the sdk advisories need code the package does not contain or a transport it does not run.** The v2 tarball read stands: outside its test files 2.1.4 has no tasks API use, no bearer authentication, no SDK client transport and no `client/auth` OAuth code.
3. **The zod advisory is bounded to a local crash.** Only the client that launched the helper over stdio can send tool input (its arguments can be shaped by prompt injection, bounded by the model's output size); Brave API responses do not pass through zod (Security Engineer reading).
4. No newer brave release exists (2.1.4 is `latest`, 2026-11-01). The fixed sdk and zod versions are declared on Brave's upstream default branch, but no Brave release carries them **(unverified)**. Removing the server would drop web search for agents (exempt from the per-agent denial by the user decision of 2026-10-16).
5. Separate upstream finding, not accepted here and not changed by it: **SEC-T702-08 (LOW)**, the Brave API fetches have no timeout or size cap.

## Conditions

- **Stdio only.** The `brave` entry in `servers.yaml` launches exactly `npx -y @brave/brave-search-mcp-server@2.1.4 --transport stdio`: the one flag is `--transport stdio`; no `--host`, `--port` or other flag and no `BRAVE_MCP_*` variable in `servers.yaml`. `tests/functional/test_mcp_package_pins.py` (`test_brave_entry_is_a_forced_stdio_launch` and its mutation test) enforces this form.
- **Operators must not set `BRAVE_MCP_TRANSPORT` or `BRAVE_MCP_HOST`** in the environment or in a `.env` file of the launch directory. The explicit argument should override them, but that was read, not run (L-3); an operator who sets `BRAVE_MCP_TRANSPORT=http` and edits the launch arguments of an installed config reopens GHSA-46jr-4wx8-v453, GHSA-f897-62hf-6gxq and the HTTP path of GHSA-mrhx-c7xc-m3w5.
- **The release gate command lists exactly these seven acceptances, and nothing broader**: `python3 scripts/audit-mcp-pins.py audit --audit-level high --accept GHSA-6qxp-vccf-f47h:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-22jm-h49p-29qw:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-6prh-2h8m-c8cw:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-46jr-4wx8-v453:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-rvq5-wwqv-78pq:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-f897-62hf-6gxq:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-mrhx-c7xc-m3w5:2027-01-30:@brave/brave-search-mcp-server@2.1.4`. An accepted id is still printed as ACCEPTED; an expired acceptance fails the audit; each acceptance counts only when brave 2.1.4 is the only pinned package the vulnerable entry puts at risk, and a bump of the brave pin voids all seven (SEC-T676-11).
- **Re-audit** at any `@brave/brave-search-mcp-server` release above 2.1.4, at any new advisory on `@modelcontextprotocol/sdk@1.30.0` or `zod@4.3.6` that affects the stdio transport or tool-input validation, at any change to the `brave` entry of `servers.yaml`, and at the expiry.
- **Only the user can renew** this acceptance, in a new version of this artifact.

## Run of 2026-11-01 (T712)

`python3 scripts/audit-mcp-pins.py audit --audit-level high` with exactly the seven `--accept` entries above (npm 11.17.0, public registry, empty user configuration), in the T712 worktree:

- **Exit 0**, `result: no finding at or above the audit level`. Printed as `ACCEPTED high`: `@brave/brave-search-mcp-server`, `@modelcontextprotocol/sdk` (the six sdk advisories) and `zod` (GHSA-mrhx-c7xc-m3w5). All seven acceptances printed as `accepted ... until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4`.
- Below the audit level and not accepted: `moderate` for `@modelcontextprotocol/server-filesystem` through `glob` (GHSA-3g3m-2fjr-6pw4) and `minimatch` (GHSA-g3hv-75wg-m249). They are not part of this decision.
- Negative control: the same command with six entries (without GHSA-f897-62hf-6gxq) exits 1 (`result: FINDINGS`; the sdk and brave stay `high`).
- **Script change needed for the pass (T712).** The first run with the seven entries exited 1: in the audit of the whole pin set npm 11.17.0 returned an empty `effects` list for `@modelcontextprotocol/sdk`, while `@brave/brave-search-mcp-server` named the sdk in its `via` and `zod` listed brave in its `effects` (in a brave-only audit it was the other way round). The scoping rule of SEC-T676-11 then found no pinned package for the sdk and refused the acceptance (fail closed). T712 changed `direct_roots` in `scripts/audit-mcp-pins.py` to follow the reverse `via` links as well as `effects`. This can only add pinned packages to the set that an acceptance must cover, never remove one; an entry that reaches no pinned package is still never accepted. Tests: `tests/functional/test_audit_mcp_pins_hardening.py`.

## Limits

L-1 The seven advisories were read from their titles and ranges in the npm advisory feed, not from the upstream patches; the reachability grades are the Security Engineer's, relayed by the orchestrator, not re-derived here. L-2 The v2 tarball reading (no tasks API, bearer, client transport or `client/auth` outside tests) was a text and import search, not a call-graph analysis. L-3 Nothing in the package was run: that a command-line `--transport stdio` overrides `BRAVE_MCP_TRANSPORT` from the environment or from `.env` was read from `dist/config.js` (the variable is only the option's default value in commander 14.0.3) and is **(unverified)** by a run. L-4 That the fixed sdk and zod versions exist on upstream `main` but are unpublished was read once through a web fetch **(unverified)**. L-5 The `effects` asymmetry in npm 11.17.0 was observed on two trees (the whole pin set and brave alone, four runs each, the same result every time); the cause in npm was not analysed. L-6 `npx` resolves the package again at launch; the exact `1.30.0` and `4.3.6` pins of brave 2.1.4 keep the vulnerable versions fixed, and any other transitive can float.
