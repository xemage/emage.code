# T653 — Loopback redirect test for mcp-fetch-server@1.1.2 (SEC-T646-01)

**ID:** T653
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** T646
**Affects:** —
**Created:** 2026-10-15
**Completed:** 2026-10-15
**Based on:**
- `docs/artifacts/security-review-t646-dependency-audit-v1.md` (SEC-T646-01, option (d)), `docs/plans/plan-122-release-v8-wave-3.md` (T646, T650)
- The user's decision of 2026-10-15 (AskUserQuestion, verbatim option label): "Test first, then decide (Recommended)"

## 1. What and why

Evidence for the re-grade of SEC-T646-01. In a scratch directory outside the repository, install `mcp-fetch-server@1.1.2` (exact pin; `npm install` into the scratch directory or `npx -y mcp-fetch-server@1.1.2`) and exercise its fetch tool over stdio MCP (or import its fetcher) against local servers only: server A on 127.0.0.1 answers `302` to server B on another loopback port; server B records whether it receives any request. Ask the server to fetch A's URL. Cases: (1) A redirects to B on loopback; (2) A redirects to a link-local style target is NOT tested against any real address: use B on 127.0.0.1 only; (3) a direct fetch of B's URL (does the guard block loopback directly?); (4) a hostname that resolves to loopback (for example `localhost`). Report for each: whether B saw a request, the tool's returned error text, and the package and Node versions. Also record `private-ip` version used. No network target other than loopback and the npm registry; no GitLab calls; nothing written to the repository except one short artifact `docs/artifacts/fetch-ssrf-test-t653-v1.md` (Based on: security-review-t646-dependency-audit-v1.md) with commands, versions and results. Do not modify `servers.yaml` or any projection.

## 2. Output

The artifact and one local commit.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit ledgers or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out id; run `python3 -m unittest tests.functional.test_golden_held_out_isolation` before the commit. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`.
- Mark anything you did not re-run **(unverified)**.

## 4. Acceptance criteria

1. Results for all four cases with B's request log.
2. A clear statement: "B saw a request after a redirect: yes/no".

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
