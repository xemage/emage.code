# T799 — Scout a replacement for the Brave MCP server

**ID:** T799
**Owner:** technology-scout
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-155-v11-release-decisions.md` (task T799, User decisions 2)
- The user's answer of 2026-11-12 on SEC-T702-09, verbatim: "If there is an easy and good replacement for it, replace it, otherwise Accept for v11.0.0"
- `docs/artifacts/brave-audit-acceptance-v3.md`; `docs/artifacts/security-review-t712-brave-stdio-v1.md`; `implementation/knowledge/mcp/servers.yaml` (the `brave` entry)

## 1. What and why

The `brave` entry pins `@brave/brave-search-mcp-server@2.1.4`, which ships seven known advisories (SEC-T702-09, SECURITY:MEDIUM, accepted for v10.0.0 only). No release above 2.1.4 exists. The user wants it replaced if an easy and good replacement exists, and accepts it for v11.0.0 otherwise. Find out whether one exists. You do not decide; you report candidates and a recommendation for the user.

## 2. Output

Return, as your final message, the full text of `docs/artifacts/brave-replacement-scouting-v1.md` (the orchestrator commits it; you have no write tool). It contains:
- what the harness uses `brave` for (from `servers.yaml`, `AGENTS.md` § MCP Servers and the agent files; no agent lists its tools, it is available to the session);
- the candidates you looked at, at least: another web-search MCP server with an official or widely used package (for example Tavily, Exa, Kagi, SearXNG, DuckDuckGo-based servers, Perplexity), a newer or forked build of the Brave server, and "no search server at all" (the platform's own web search tool);
- for each candidate, with a source URL and the date you read it: package name and newest version; maintainer (official vendor or third party); licence; transport (stdio available?); credentials it needs and whether a free tier exists; known advisories of the package and of its dependency tree, as far as you can find them without running a tool (say **(unverified)** where you could not); release activity; how its tool set compares with Brave's;
- "easy": what would change in the harness (the `servers.yaml` entry, the env-var contract, `PREREQUISITES.md`, the wiki, tests that pin the Brave package and args, the migration note for users with a `BRAVE_API_KEY`);
- "good": whether the candidate would end SEC-T702-09 or only move the risk (a third-party package with no audit is not better than a known, accepted one);
- your recommendation: one candidate, or "no easy and good replacement; keep the acceptance", with the reasons.

## 3. Constraints

- Read-only. No command is run; you have no shell. Do not ask anyone to run `docker`.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never open `tests/golden/held-out/`.
- Do not send any project content, key or email address to a web service. Search queries carry only public package names.
- Mark every claim you did not verify at its source **(unverified)**. Do not grade the finding; grading is the Security Engineer's.
- Token budget: 60k, counting context.

## 4. Acceptance criteria

- Each candidate row has a source URL and a read date, or is marked **(unverified)**.
- The recommendation is one of the two forms in § 2 and follows from the rows.
- The text is valid Markdown without relative links that do not resolve from `docs/artifacts/`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
