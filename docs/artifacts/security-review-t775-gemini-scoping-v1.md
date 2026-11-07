# Artifact: security-review-t775-gemini-scoping-v1.md

# Security Review T775: Gemini CLI scoping for the SEC-T657-01/SEC-T658-01 remainder

**Based on:** `docs/artifacts/security-review-t756-accepted-mediums-v1.md` (Part 1 row, Q4), `docs/decisions/ADR-013-drop-pi-platform-support.md`, `docs/artifacts/security-review-t773-pi-removal-v1.md`, `docs/artifacts/mcp-server-denials-v1.md`, develop `22bb4c74`.
**Reviewer:** security-engineer (read-only; vendor docs and source read 2026-11-07; no live Gemini run). Recorded by the orchestrator from the reviewer's final message, condensed. The orchestrator re-checked on 2026-11-07: `implementation/platforms/gemini.json` `"tools": "drop"` and `keepKeys` with `agents`; `implementation/.gemini/agents/orchestrator.md` `name: "Orchestrator"` and `agents: [...]`; Gemini CLI v0.67.0 `agentLoader.ts:50-52` `nameSchema` `/^[a-z0-9-_]+$/`, `.strict()` at 116 and 221; `local-executor.ts:205-206` "We do not allow agents to call other agents", `getToolsByServer` at 241.

## Summary
Gemini CLI now has per-subagent tool scoping that covers MCP tools: a `tools:` list in `.gemini/agents/*.md` is enforced; an MCP tool reaches a subagent only when listed exactly (`mcp_gitlab_get_issue`) or by wildcard (`mcp_gitlab_*`, `mcp_*`, `*`); without `tools:` a subagent inherits every parent tool. The gap is now in our generator: (1) `gemini.json:14` `"tools": "drop"`; (2) the 28 generated agent files probably do not load (non-slug `name:`, and `agents:` rejected by the strict schema), so all Gemini work runs in the top-level session with every tool (SEC-T775-01); (3) Gemini subagents cannot call agents, so the orchestrator role runs only as the main session, which per-agent scoping does not narrow; only server-level `includeTools`/`excludeTools` limit it. Re-grade: remainder stays **SECURITY:MEDIUM** today; **LOW** after options 1 + 2 (+ 4).

## Vendor facts (read 2026-11-07)
- V1 Latest stable v0.67.0 (04 Nov). https://github.com/google-gemini/gemini-cli/releases
- V2 Subagent frontmatter: `name` (required slug), `description`, `kind`, `tools` (optional; omitted = inherit all; wildcards `*`, `mcp_*`, `mcp_<server>_*`), inline `mcpServers`, `model`, `temperature`, `max_turns`, `timeout_mins`; agents enabled by default; loaded from `.gemini/agents/*.md` and `~/.gemini/agents/*.md`. https://geminicli.com/docs/core/subagents/
- V3 Enforcement at v0.67.0 `packages/core/src/agents/local-executor.ts`: with `tools` set, only listed names are registered (`*`, `mcp_*`, `mcp_<server>_*` via `getToolsByServer`, else exact `getTool`); unknown names skipped (fails closed); no list = all parent tools; `Kind.Agent` never registered.
- V4 Loader v0.67.0 `agentLoader.ts`: `nameSchema` `/^[a-z0-9-_]+$/`; tool entries must pass `isValidToolName(…, {allowWildcards:true})`; schema `.strict()`; invalid files skipped, error pushed to `result.errors` (whether shown to the user: unverified).
- V5 MCP tool names `mcp_<server>_<tool>`, sanitised, >63 chars truncated 30+`...`+30; parsing splits at the first underscore (hyphenated server names work). `main`, `mcp-tool.ts`.
- V6 Server-level `includeTools`/`excludeTools` (`mcp-client.ts` `isEnabled`, v0.67.0) match the server-reported name; `excludeTools` exact and takes precedence; `includeTools` also matches `name(...)`; re-applied on `tools/list_changed`, so tools activated later by GitLab's `discover_tools` are still filtered.
- V7 Policy engine rules can target a `subagent`, but the workspace tier (`.gemini/policies`) is "currently non-functional" (issue #18186); only user/admin tiers work. https://geminicli.com/docs/reference/policy-engine/
- V8 Doc banner: "Unpaid tier and Google One users: Gemini CLI was replaced by Antigravity CLI on June 18th, 2026".

## Current state in this repo
- `implementation/platforms/gemini.json:14-15` `"tools": "drop"`, `keepKeys: ["name","description","agents"]`.
- `implementation/.gemini/agents/*.md:2` non-slug names in all 28 files; `orchestrator.md:4`, `poc-orchestrator.md:4` carry `agents:`.
- `implementation/scripts/sync.mjs:736-756` (`emitMcpGemini`) writes `excludeTools` only from `denyTools`; no `includeTools`; `denyTools` exact names (`sync.mjs:186-193`).
- `servers.yaml`: `denyTools` only on `playwright`; `denyUnlessGranted` ignored for Gemini; `gitlab` sets `GITLAB_PERMISSION_MODE: modify` (refuses delete/teardown per README; unverified at 2.2.5).
- The seven GitLab holders' named tools: union of 44 tools (get_issue, list_issues, list_issue_discussions, create_issue, update_issue, create_issue_note, create_issue_link, list_issue_links, get_issue_link, list_labels, get_label, create_label, update_label, list_milestones, get_milestone, create_milestone, edit_milestone, get_milestone_issue, get_milestone_merge_requests, get_milestone_burndown_events, list_project_members, create_merge_request, get_merge_request, list_merge_requests, get_merge_request_approval_state, list_merge_request_changed_files, get_merge_request_file_diff, mr_discussions, list_merge_request_pipelines, list_pipelines, get_pipeline, list_pipeline_jobs, get_pipeline_job, get_pipeline_test_report, get_pipeline_test_report_summary, validate_ci_lint, validate_project_ci_lint, get_branch, list_branches, list_tags, get_tag, list_releases, get_release, discover_tools).
- Inaccurate docs: `AGENTS.md` § MCP Servers (GitLab grants and Playwright paragraphs), `implementation/PREREQUISITES.md:186`, `servers.yaml:115-116` say Gemini does not enforce tool lists; the generator drops them. Live checks `mcp-pin-bump-checklist.md:65,75` not run. K-23: align `PREREQUISITES.md:186` ("Opencode: generated agents get per-agent denies (T663); built-in agents and your own agent files do not (K-23). Gemini CLI: see the outcome of T775.").

## Options
1. **Per-agent scoping:** map `tools:` lists (slug `name` = file stem, drop `agents:`, `mcp__gitlab__x` → `mcp_gitlab_x`, `mcp__memory` → `mcp_memory_*`, built-in tokens to Gemini built-in names), with a schema test. Cost M (built-in mapping unverified). Main session unchanged. Fixes SEC-T775-01.
2. **Server-level `includeTools` on `gitlab` = the 44-tool union**, derived from the agent lists (new `allowTools` key, tested), generated list wins in the settings merge. Cost S-M. Removes merge, approve, push, file writes, branch/tag/release creation, pipeline trigger/retry, CI variables, raw API from every Gemini context, including the user's own session. Residual: the 44 low-impact tools; a shell with the token (SEC-T660-01); user-level entry merge (unverified).
3. **Server-level `excludeTools`** for unheld GitLab tools: fails open on pin bumps; covered by 2; not recommended.
4. **filesystem, git, supabase not emitted to Gemini** (no agent holds them); the held servers narrowed by option 1.
5. **Re-accept for v11.0.0:** MEDIUM stays, docs stay wrong, Gemini agents stay non-functional.
6. (Outside the brief) **Drop Gemini support** like ADR-013.

## Recommendation
Options 1 + 2 + 4; skip 3. Owner devops-engineer, review tech-lead and security-engineer; deadline 2027-01-31, before v11.0.0. Close only after extended § 6 live checks (`/agents` lists 28 agents without load errors; `/mcp` shows exactly the 44 GitLab tools; a non-holder subagent cannot see `mcp_gitlab_*`).

## Findings
| ID | Severity | Category | Location | Finding | Remediation |
|----|----------|----------|----------|---------|-------------|
| SEC-T657-01/SEC-T658-01 remainder | SECURITY:MEDIUM (today) | A01/A05 | `gemini.json:14`; `sync.mjs:736-756`; `servers.yaml:71-94` | Every Gemini agent and the main session can call every configured MCP tool but the six Playwright ones; cause is the generator. LOW after 1+2+4; MEDIUM after 2 only, 1 only, or 5. | Options 1+2+4 |
| SEC-T775-01 | SECURITY:LOW (functional major) | A05 | `.gemini/agents/*.md:2`; `orchestrator.md:4`, `poc-orchestrator.md:4`; `gemini.json:15` | Non-slug names and `agents:` fail the strict loader; agents skipped (source reading). | Emit file stem as `name`, drop `agents`, schema test |
| SEC-T775-02 | SECURITY:LOW | A05 (docs) | `AGENTS.md` § MCP Servers; `PREREQUISITES.md:186`; `servers.yaml:115-116` | Docs say Gemini does not enforce tool lists; line 186 also contradicts T663 (K-23). | Rewrite after the fix |
| SEC-T775-03 | SECURITY:LOW (info) | A04 | design | Gemini subagents cannot call agents; orchestration needs the main session, which per-agent scoping does not narrow. | Document; rely on option 2 |

## VERDICT: CONDITIONAL_PASS
Facts established well enough to decide; one MEDIUM (the remainder) open with a plan; no CRITICAL/HIGH; no constraint breach. Conditions: remainder fixed by options 1+2+4 and live checks before v11.0.0 (2027-01-31) or a new user acceptance under ADR-011; SEC-T775-01..-03 tracked as LOW debt.

## Not verified
No live Gemini run; whether load errors are shown; Gemini built-in tool names; `isValidToolName` on `mcp_gitlab_<tool>`; user/project `gitlab` entry merge; untrusted-workspace effect; `GITLAB_PERMISSION_MODE=modify` at 2.2.5; Antigravity implications; `docs/wiki/mcp-servers.md` not reread; vendor line numbers approximate. Blocker: none; external dependency (minor): someone with Gemini CLI v0.67.x must run the § 6 live checks.
