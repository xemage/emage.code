# Brave MCP server: replacement scouting v1

**Task:** T799
**Based on:** `docs/tasks/task-T799.md`; `docs/artifacts/brave-audit-acceptance-v3.md`; `docs/artifacts/security-review-t712-brave-stdio-v1.md`; `implementation/knowledge/mcp/servers.yaml` (header comments, pin policy, the `brave` entry); `AGENTS.md` § MCP Servers (the `brave` row)
**Date:** 2026-11-12
**Author:** technology-scout (read-only; no command was run, no package was installed or audited)

> Immutable once produced; revisions bump `<N>`.

## 1. Summary

No candidate is both easy and good. Recommendation: **no easy and good replacement; keep the acceptance** (§ 6).

- Every other search server either carries the same advisories (Tavily), would probably trade them for a new unfixable one (Exa, Perplexity), or is an unaudited package that adds a page-fetching tool or a self-hosted service (SearXNG, DuckDuckGo, Kagi).
- The fix already exists upstream: Brave's `main` branch declares `@modelcontextprotocol/sdk` 1.32.2 and `zod` 4.6.7, but is still versioned 2.1.4 and unpublished. A Brave release would end the finding with a one-line pin bump.
- Removing the server ends SEC-T702-09 outright, but it is a removal, not a replacement, and it reverses the user decision of 2026-10-16 to keep search for generated agents.

## 2. What the harness uses `brave` for

- `servers.yaml` ships `brave` as a `core` server (every platform): `npx -y @brave/brave-search-mcp-server@2.1.4 --transport stdio`, with `BRAVE_API_KEY` as a secret env reference.
- It is exempt from the per-agent denial (`denyUnlessGranted: false`, user decision 2026-10-16), so generated agents keep it.
- `AGENTS.md` gives its purpose as "Technology discovery". No agent lists its tools (Technology Scout and Feasibility hold no token); it is available to the session.
- The agent files were not read for this report; the statement that no agent lists a `brave` tool is taken from `AGENTS.md`.
- Upstream exposes eight tools: `brave_web_search`, `brave_local_search`, `brave_video_search`, `brave_image_search`, `brave_news_search`, `brave_summarizer`, `brave_place_search`, `brave_llm_context` (repository README, read 2026-11-12). Whether 2.1.4 as published has exactly these is **(unverified)**.

## 3. Candidates

All sources were read on 2026-11-12 through a web fetch summarised by a small model. No `npm audit`, OSV query or install was run, so every advisory statement below is derived from declared dependency ranges, not from an audit.

| # | Candidate | Package and newest version | Maintainer | Licence | Stdio | Credential and free tier | Source |
|---|---|---|---|---|---|---|---|
| A | Brave, current pin | `@brave/brave-search-mcp-server` 2.1.4 (only dist-tag: `latest`) | Brave (official) | MIT | Yes (and HTTP) | `BRAVE_API_KEY`; the README lists "Search" and "Answers" plans and names no free tier | `https://registry.npmjs.org/@brave/brave-search-mcp-server`, `https://github.com/brave/brave-search-mcp-server` |
| B | Brave, unreleased `main` or a fork | none published; `main` `package.json` says 2.1.4 with sdk 1.32.2, zod 4.6.7, express 5.2.1, commander 14.0.3, dotenv 17.3.1 | Brave (official) or whoever forks | MIT | Yes | as A | `https://raw.githubusercontent.com/brave/brave-search-mcp-server/main/package.json` |
| C | Tavily | `tavily-mcp` 0.2.22 | Tavily (official) | MIT | Yes **(unverified)** | `TAVILY_API_KEY`, free tier exists **(both unverified)** | `https://registry.npmjs.org/tavily-mcp/latest` |
| D | Exa | `exa-mcp-server` 3.4.3 | Exa Labs (official) | MIT | Yes (bin is `dist/stdio.cjs`) | `EXA_API_KEY`, free credits **(both unverified)** | `https://registry.npmjs.org/exa-mcp-server/latest` |
| E | Perplexity | `@perplexity-ai/mcp-server` 1.3.0 | Perplexity (official) | MIT | Yes **(unverified)** | `PERPLEXITY_API_KEY`, paid API, no free tier **(all unverified)** | `https://registry.npmjs.org/@perplexity-ai/mcp-server/latest` |
| F | Kagi | `kagimcp` 1.1.0 on PyPI (uploaded 2026-10-28) | Kagi (repository `kagisearch/kagi-mcp`) | no licence field in the PyPI metadata; a `LICENSE` file exists | Yes **(unverified)** | `KAGI_API_KEY`; paid, API access by invitation **(all unverified)** | `https://pypi.org/pypi/kagimcp/json` |
| G | SearXNG | `mcp-searxng` 2.10.1 | third party, one maintainer (ihor-sokoliuk) | MIT | Yes **(unverified)** | no key, but needs the URL of a SearXNG instance the user runs or trusts **(unverified)** | `https://registry.npmjs.org/mcp-searxng/latest` |
| H | DuckDuckGo | `duckduckgo-mcp-server` 0.7.0 on PyPI (uploaded 2026-09-04) | third party, one maintainer (nickclyde) | MIT (classifier) | Yes **(unverified)** | none; scrapes result pages, no vendor API **(unverified)** | `https://pypi.org/pypi/duckduckgo-mcp-server/json` |
| I | No search server | none | the platform vendors | n/a | n/a | none | `servers.yaml` (the `playwright` comment: agents use the platform `web` tool); the Claude Code session of this run has a built-in web search and fetch tool |

### 3.1 Advisories, release activity and tool set per candidate

| # | Declared dependencies that matter | Advisory position (derived, not audited) | Release activity | Tool set against Brave |
|---|---|---|---|---|
| A | sdk exactly 1.30.0, zod exactly 4.3.6 (acceptance v3) | The seven accepted advisories | 2.1.4 is still `latest`; publish date not re-read (the brief states 2026-09-17) | baseline |
| B | sdk 1.32.2, zod 4.6.7 | All seven fixed versions are met on `main`. This confirms L-4 of acceptance v3 by a second read; that the build works is **(unverified)** | 611 commits; no GitHub release listed; last commit date not shown | identical |
| C | sdk exactly **1.26.0**, axios `^1.6.7`, yargs, dotenv | sdk 1.26.0 lies inside the affected range of all six sdk advisories of acceptance v3 (`<1.30.1`, `<1.31.0`, `<1.32.0`). The zod advisory depends on what the sdk pulls **(unverified)** | not read | search, extract, crawl, map **(unverified)**; extract and crawl fetch pages |
| D | sdk `^1.12.1`, zod `^3.22.4`, jose, `exa-js`, `mcp-handler`, `agnost` | The sdk range floats and should resolve to a fixed version at install **(unverified)**. zod stays on 3.x: GHSA-mrhx-c7xc-m3w5 lists `< 4.6.6` with 4.6.6 as the only patched version, so an audit would probably flag it with no fix inside 3.x **(unverified)**; the advisory text itself names only 4.x code. `agnost` looks like a usage-analytics client **(unverified)** | not read | web search, code context, crawling, research tools **(unverified)**; no local, image, video or news search |
| E | sdk `^1.29.0`, zod `^3.25.46`, express `^4.21.2`, cors, undici | Same zod 3.x position as D **(unverified)**. Ships an HTTP server path (express, cors); whether stdio can be forced by argument is **(unverified)** | not read | answer, research and reasoning tools backed by an LLM, plus a search tool **(unverified)**; not a like-for-like raw search |
| F | `fastmcp~=3.2`, `pydantic~=2.12.5`, urllib3 | Python tree, never audited by the harness; `scripts/audit-mcp-pins.py` covers npm pins, and whether it covers `uvx` pins is **(unverified)** | 1.1.0 uploaded 2026-10-28 | search and summarizer **(unverified)** |
| G | zod 4.6.7, `@modelcontextprotocol/server` 2.4.0, `core` 2.4.0, `node` 2.1.2, express 5.3.0, undici, `unpdf`, `node-html-parser`, `node-html-markdown`, `express-rate-limit` | zod is at a fixed version; it uses the v2 SDK packages, whose advisory state is **(unverified)**. Larger tree than Brave's, including HTML and PDF parsers | not read | web search plus a URL-reading tool (inferred from the parser dependencies, **(unverified)**) |
| H | `mcp[cli]>=2.1.1,<3`, httpx, beautifulsoup4 | Python tree, never audited by the harness | 0.7.0 uploaded 2026-09-04 | search plus a fetch-content tool **(unverified)** |
| I | none | Ends SEC-T702-09: the package leaves the pin set | n/a | web search only, per platform. Claude Code has one built in (US-only, per its tool description). Cline, Opencode and GitHub Copilot equivalents are **(unverified)**. No local, image, video or news search |

## 4. "Easy": what changes in the harness

Derived from the brief, acceptance v3 and `servers.yaml`. `PREREQUISITES.md`, the wiki and the test files were not opened, so the list of affected places is **(unverified)** in detail.

| Change | B (git build or fork) | C, D, E (npm, new vendor) | F, H (uvx) | G (SearXNG) | I (remove) |
|---|---|---|---|---|---|
| `servers.yaml` entry | new launch form (not an npm version pin; breaks the pin policy and the provenance check) | new package, args, env var; server name `brave` changes | as C, plus a `uvx` pin and hash lock | as C, plus an instance URL variable | entry deleted; `brave` leaves the exempt list in the header comment |
| Env-var contract | none | `BRAVE_API_KEY` replaced; every user gets a new account and key | as C (H: none) | user must run or choose an instance | `BRAVE_API_KEY` dropped |
| `PREREQUISITES.md`, wiki, `AGENTS.md` table and exemption text | small | rewrite of the Brave parts | rewrite | rewrite plus hosting guidance | rewrite; the user decision of 2026-10-16 needs a new ruling |
| Tests (`test_mcp_package_pins.py`: `APPROVED_NPX_PINS`, `test_brave_entry_is_a_forced_stdio_launch` and its mutation test; Opencode exemption tests) | rework | rework; a new forced-stdio check per package | rework | rework | delete and adjust |
| Security work | review of a self-built artifact | new tarball read, reachability grading, release-gate run, live denial checks | the same, on an ecosystem the gate may not cover | the same, plus SSRF review of the URL reader | none |
| Migration note | none | yes: key swap, breaking for every install | yes | yes | yes: search tools disappear from sessions |
| Root refresh of generated configs | yes | yes | yes | yes | yes |

Only A (no change) and a future upstream release (one pin bump under the existing checklist) are easy. Candidate I is moderate in files but needs a user ruling. C to H are each a full server swap plus a fresh security review.

## 5. "Good": does it end SEC-T702-09 or move the risk

| # | Ends the seven advisories | Assessment |
|---|---|---|
| A | No | The known, graded and accepted state. Acceptance v3 runs until 2027-01-30 or the first release above 2.1.4. |
| B | Yes on paper | Not a published, signed npm release. A git or fork launch gives up the exact-version pin and registry provenance, which is a larger risk than the one it removes. |
| C | **No** | Pins sdk 1.26.0, inside all six sdk ranges. Same finding under another vendor name, without a reachability grading. |
| D | Probably not | Likely trades seven graded advisories for one ungraded zod 3.x finding with no fix path, and adds an analytics dependency. **(unverified)** without an audit run. |
| E | Probably not | Same zod position as D; an HTTP path whose default is unreviewed; a different product (LLM answers), paid. |
| F | Unknown | Official, but unaudited and in an ecosystem the release gate was not shown to cover; gated paid API. |
| G | Unknown | Single-maintainer third party with a wider tree and a URL-reading tool. The harness removed its `fetch` server in v8.0.0 for following redirects blindly; this would bring a similar surface back. |
| H | Unknown | Single-maintainer third party, scraping without a vendor contract, plus a fetch tool. The same concern as G. |
| I | Yes | The only candidate that certainly ends the finding. It moves no risk to another package, but it is not a replacement. |

By the brief's own rule ("a third-party package with no audit is not better than a known, accepted one"), C to H are not good.

## 6. Recommendation

**No easy and good replacement; keep the acceptance.**

Reasons:

1. No other search server is both easy and good (§ 4, § 5). The best-known official alternative, Tavily, carries the same six sdk advisories; Exa and Perplexity would probably raise a new unfixable zod finding; the rest are unaudited and widen the attack surface.
2. All seven advisories were graded LOW for reachability in the forced-stdio launch, and that launch form is enforced by test. A swap would discard this known state for an ungraded one.
3. The real fix is a Brave release. Upstream `main` already declares the fixed versions, so the finding can end with a pin bump under the existing checklist. Acceptance v3 already names "first release above 2.1.4" as a re-audit trigger.
4. Removal (I) is the one option that ends the finding today. It is reported here as a separate choice for the user, not as a replacement: it reverses the decision of 2026-10-16, and non-Claude platforms' own web search tools are unverified.

Follow-ups for the orchestrator and the user (not decided here):

- The acceptance for v11.0.0 needs a new artifact version with the user's words; the current expiry is 2027-01-30.
- Asking Brave upstream to publish `main` is a user action; nothing was sent to any vendor.
- If the user prefers removal, a tech-lead inventory and an ADR in the style of ADR-013 and ADR-014 would be the route.

## 7. Limits

- L-1 Nothing was run. Advisory positions are read from declared dependency ranges on the registry, not from `npm audit`, OSV or the vendors' security advisory pages.
- L-2 Every web page was read through a summarising fetch; a summary can drop or misread a field. The Brave registry document was truncated before the 2.1.4 entry, so its dependencies and publish date were not re-read at the registry (they come from acceptance v3 and the brief).
- L-3 Tool sets, credentials, free tiers and stdio support of C to H are from general knowledge where marked **(unverified)**; the vendors' READMEs were not opened, to stay inside the token budget.
- L-4 Whether zod 3.x is really affected by GHSA-mrhx-c7xc-m3w5 is open: the advisory page lists `< 4.6.6` but describes 4.x code only (`https://github.com/advisories/GHSA-mrhx-c7xc-m3w5`, read 2026-11-12).
- L-5 `docs/plans/plan-155-v11-release-decisions.md`, `implementation/PREREQUISITES.md`, the wiki, the test files and the agent files were not read; § 2 and § 4 rely on the brief, acceptance v3, `servers.yaml` and `AGENTS.md`.
