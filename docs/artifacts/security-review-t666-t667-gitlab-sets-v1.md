# Artifact: security-review-t666-t667-gitlab-sets-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell: no test, drift gate or full suite run; the final tree was read, not the commit diffs; `grep_content` failed on the worktree, so full reads were used; only 8 of 28 agent sources were read directly; `@zereight/mcp-gitlab@2.2.5` was read from unpkg through a summarising fetch tool, handlers inspected for 7 of the 24 names). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-16.
- **Target**: T666 (`98f594b2`: named GitLab tools for orchestrator and poc-orchestrator) and T667 (`8bba5e5e`: devops-engineer, release-manager, poc-devops-engineer) reviewed; then `fff383b8` (the review's conditions) on `agent/devops-engineer/T667` (from develop `17fe179`).
- **Based on**: `docs/tasks/task-T666.md`, `docs/tasks/task-T667.md`, `security-review-t660-gitlab-grants-v1.md`, `mcp-agent-denials-v1.md`.
- **Orchestrator checks**: the developer reports 1348 tests OK (skipped 23) and all gates after the last commit; the root drift baseline equals `--print-drift` (57 paths).

## Verdict: CONDITIONAL_PASS (conditions met in `fff383b8`, except SEC-T660-01)

0 critical, 0 high, 1 new medium (SEC-T667-01), 6 new low; SEC-T660-01 (medium) carried and still open (accepted by the user on 2026-10-15, plan: T665). No Immutable Security Constraint is breached; no required control is omitted or weakened; the change is strictly narrower than before on every platform. SEC-T660-04 is closed for the MCP tool surface (no agent holds the whole `gitlab` server any more: seven named holders with 24, 20, 16, 8, 11, 17 and 6 tools); it is not closed as a credential boundary because six of the seven holders hold `execute`.

## What the review verified

- All 24 distinct names in the five new lists exist in the pinned `@zereight/mcp-gitlab@2.2.5` registry (toolsets: core, `merge_requests`, `pipelines`, `ci`, `tags`, `releases`; `discover_tools` is a meta tool). Every tool is read-only except `create_merge_request` (orchestrator, poc-orchestrator, release-manager). Its schema has no `auto_merge` or `merge_when_pipeline_succeeds` (those exist only in the ungranted `merge_merge_request`), so it cannot merge, auto-merge or approve; `squash` and `remove_source_branch` are only stored on the MR.
- Read-looking tools that were checked: `validate_ci_lint` (POST `/ci/lint`, creates nothing; with `dry_run` GitLab resolves `include:` entries server-side), `validate_project_ci_lint` (GET), `get_pipeline_test_report_summary` (counts only), `get_pipeline_job` (metadata, not the trace), `get_merge_request_approval_state` (GET).
- Non-grants agreed: `merge_merge_request`, `create_tag`/`create_release`/`create_branch` for release-manager, `get_pipeline_job_output` for devops-engineer (the non-grant costing the most availability; `glab ci trace` stays reachable through the shell), pipeline control (`play_pipeline_job` could start a manual production deploy job), variables, environments/deployments/runners.
- Projections: named forms only on Claude Code, Cursor (before its removal), Copilot (`gitlab/<tool>`, no `gitlab/*`), Pi and Opencode (`gitlab_*: false` first, then named allows); the Opencode live resolver evidence was run for qa-engineer and scrum-master and the pre-T666 orchestrator, not for the five new named holders (same shape, model and source reading).
- Tests pin exact sets for all seven roles, the subset relations, a widened forbidden-name regex, a writes map, an allowlist rule (every non-write tool starts with `get_`/`list_` or is a named read), per-platform equality and the Opencode wildcard-first order.

## Findings and dispositions

| ID | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T667-01 | SECURITY:MEDIUM (A04, A01) | The release-manager body, description, checklist and the `release-workflow` skill still told the role to merge, tag and publish, while the docs and the MCP list say it does none of these; with `execute` and the token the narrowing was nominal for exactly the actions the policy forbids | Fixed in `fff383b8`: the body, checklist and skill say the release manager prepares and verifies and the top-level session merges, tags and publishes with the user's approval; a Constraints line forbids merging, tagging and releasing; three further sentences changed (announced, branch deleted, failure mode); the B1 release order is kept |
| SEC-T666-01 | LOW (A04) | The orchestrator body instructed `glab release create` and "cutting any release tag" while holding a shell and reading untrusted issue and MR text | Fixed in `fff383b8`: the top-level session or the user runs `glab release create ... -F docs/releases/vX.Y.Z.md` after the orchestrator verified the document exists and `verify-release-docs.py --tag vX.Y.Z` passes |
| SEC-T667-02 | LOW (A05, A04) | Stale "whole server" statements in the three docs' "Used by" rows, wiki lines 91 and 108-111, and the immutable `mcp-agent-denials-v1.md` | Fixed in `fff383b8`; the immutable artifact is superseded by `docs/artifacts/mcp-agent-denials-v1-addendum-t667.md` |
| SEC-T667-03 | LOW (A01, A04) | `create_merge_request` can target any project, branch, assignee and reviewer the token reaches (no `GITLAB_ALLOWED_PROJECT_IDS`) and can start merge-request pipelines (an indirect CI trigger) | Accepted residual; one sentence added to the docs |
| SEC-T667-04 | LOW (A08) | Docs and counts not pinned; tool names not checked against the registry; vacuous whole-server branches in the tests; Gemini agents' missing `tools:` line not asserted | Fixed in `fff383b8` (documentation tests, a checked-in snapshot of the 275 tool names of the pinned version `tests/_baselines/gitlab-mcp-tool-names.json` with a version and membership test, vacuous branches removed, a Gemini no-tools-line test) |
| SEC-T667-05 | LOW (A02, A04) | Over-claim "No subagent merges, tags or releases"; the residual was hedged ("if it is exported") although the setup docs tell users to export the token; PAT scope guidance inconsistent between the wiki and PREREQUISITES | Wording fixed in `fff383b8` ("a tool-list narrowing and a policy, not an enforcement"); the PAT scope reconciliation moves to T665 |
| SEC-T667-06 | LOW (A10, A01) | CI lint with `dry_run` resolves `include:` remote/project/template entries server-side (a server-side outbound request to a model-chosen URL on self-managed instances); `get_merge_request(include_summaries)` returns deployment and approval summaries | Accepted residual; one sentence added to the docs |
| SEC-T660-01 (carried) | SECURITY:MEDIUM (A01, A04, A02) | Not a credential boundary: six of the seven holders hold `execute` (scrum-master does not); the orchestrators also hold `agent`; `edit` and `execute` also let a role change its own agent file | Accepted by the user on 2026-10-15 ("Accept the risk, plan after the release (Recommended)"); mitigation in T665 |

## Conditions and residuals

- D-1: this repository's own installed agents (the root `.claude/agents` and the other root trees) keep the old grants until the next user-approved `--projections-only` refresh (T679).
- Availability, unverified: most lists sit in non-default toolsets (devops-engineer 8 of 11, poc-devops-engineer 5 of 6, release-manager 8 of 17, orchestrator 4 of 16, poc-orchestrator 3 of 8); a client that ignores a listed tool until `discover_tools` has run loses pipeline, tag and release reads (fails closed); route to QA.
- Tracked debt: SEC-T667-03, -06, SEC-T660-02, -03, -05, -07, SEC-T660-06 (partly closed).

## Limits

L-1 no shell (no tests, drift gates, registry check or full suite run); L-2 the final tree was read, not the commit diffs, no repository-wide search was possible, other docs (README, other wiki pages) may still say "whole server"; L-3 8 of 28 agent sources read; L-4 package source through a summarising fetch tool, integrity hash not compared to the pin; L-5 no live run of Claude Code, Copilot, Opencode or Pi; L-6 no held-out, `.env*` or credential file opened.
