# T654 — Evaluate Playwright MCP as the fetch replacement (hands-on)

**ID:** T654
**Owner:** devops-engineer
**Status:** pending
**Priority:** P0
**Tier:** judgment
**Depends on:** T653
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Addendum 2: T654, T655)
- `docs/artifacts/fetch-ssrf-test-t653-v1.md`, `docs/artifacts/security-review-t646-dependency-audit-v1.md` (SEC-T646-01), `implementation/knowledge/mcp/servers.yaml`
- The user's decision of 2026-10-15 (AskUserQuestion, free-text answer to the fetch-fix question, quoted): "Remove the fetch server and replace it by an alternative (i.e Playwright MCP Server (microsoft/playwright-mcp)) which you evaluate first. Replace it before Release"

## 1. What and why

Evaluate `@playwright/mcp` (microsoft/playwright-mcp) as the replacement for the removed `fetch` server, hands-on, before any file of the install changes. Produce `docs/artifacts/fetch-replacement-evaluation-v1.md` (Based on: security-review-t646-dependency-audit-v1.md, fetch-ssrf-test-t653-v1.md) covering: (1) **Coverage**: which agents (the 11 whose frontmatter lists `mcp__fetch`: solution-architect, devops-engineer, tech-lead, frontend-developer, security-engineer, poc-security-engineer, feasibility-agent, technology-scout, poc-orchestrator, integration-agent, backend-developer) use which fetch tools (`fetch_html`, `fetch_json`, `fetch_markdown`, `fetch_readable`, `fetch_txt`, `fetch_youtube_transcript`) and what the Playwright tools (`browser_navigate`, `browser_snapshot`, `browser_evaluate`, `browser_network_request`, others) can do for each use; list honest gaps (raw JSON or API responses, readable-markdown extraction, YouTube transcripts, binary downloads) and the extra prerequisite that Playwright needs a browser (how it is installed and sized, headless, `--isolated`). (2) **Flags in the pinned version 0.0.83** (`npx -y @playwright/mcp@0.0.83 --help` locally): confirm `--blocked-origins`, `--allowed-origins`, `--isolated`, `--headless`, `--block-service-workers`, and the glob syntax accepted for origins (ports, wildcards, IPv6, ranges such as `10.*`, `192.168.*`, `169.254.*`). (3) **Hands-on SSRF test with the pinned 0.0.83 on loopback only**: listener A on a hostname that the browser will accept answers 302 to listener B on another loopback port, B logs every request. Cases: no flags (baseline: expected that B sees a request; Playwright MCP is already installed in every install with NO origin restrictions, so state plainly what it can reach today); with `--blocked-origins` listing loopback and the private/link-local forms; a redirect from an allowed origin to a blocked one; a direct navigation to a blocked origin; `localhost` and IPv6 `[::1]`. Report whether B saw a request in each case and the tool's returned text. Nothing is aimed at a real internal or link-local address: the blocked-origin patterns for those are verified only by pattern matching on loopback stand-ins and by reading the source, and marked as such. (4) **Recommendation** with the exact `args` for the `playwright` entry of `servers.yaml` (pinned version kept unless a change is justified), whether `fetch` can be removed without a gap, the residual risks (a browser is a larger attack surface than a fetch tool; prompt-injected pages), and, if the flags are insufficient or the browser prerequisite is a problem, the alternatives for the user to choose from. Do not change `servers.yaml` or any projection (T655 does).

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; run `python3 -m unittest tests.functional.test_golden_held_out_isolation` before the commit. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`.
- Loopback-only tests; the only other network use is the npm registry and the browser download CDN. Mark anything you did not re-run **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
