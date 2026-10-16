# Artifact: mcp-agent-denials-v1-addendum-t667.md

> Immutable once produced; revisions bump `<N>`. This addendum supersedes statements of `mcp-agent-denials-v1.md` (itself immutable) and does not replace it.

## Metadata

- **Task**: T667 (SEC-T660-04, SEC-T667-02). **Owner**: devops-engineer. **Date**: 2026-10-16.
- Based on: mcp-agent-denials-v1.md
- **Also consumed**: `docs/tasks/task-T667.md`, `docs/plans/plan-123-post-release-follow-ups.md` (items T666 and T667), the T666 and T667 security review of 2026-10-16 (CONDITIONAL_PASS).
- **Prior version**: `mcp-agent-denials-v1.md` (unchanged). **Rollback**: restore the whole-server `mcp__gitlab` token in the three agent sources and regenerate; this addendum then no longer applies.

## 1. What changed

After T666 (orchestrator, poc-orchestrator) and T667 (devops-engineer, release-manager, poc-devops-engineer) **no agent holds the whole `gitlab` server**. Seven agents hold named GitLab tools only: qa-engineer (20), scrum-master (24), orchestrator (16), poc-orchestrator (8), devops-engineer (11), release-manager (17), poc-devops-engineer (6). The Opencode named-subset rule therefore applies to all seven: each file starts its GitLab block with `gitlab_*: false` and the named `gitlab_<tool>: true` entries follow. The generator is unchanged; only the agent sources changed.

## 2. Statements of `mcp-agent-denials-v1.md` that are superseded

| v1 location | v1 statement | Now |
|---|---|---|
| Section 3a, holder pinning | `gitlab (whole: 5, named: qa-engineer, scrum-master)` | gitlab: whole 0, named: the seven roles above (`EXPECTED_HOLDERS` in `tests/functional/test_mcp_agent_denials.py`) |
| Section 4, table row "Whole-server GitLab holder" | orchestrator, poc-orchestrator, devops-engineer, poc-devops-engineer, release-manager get no `gitlab_*` deny | No such class exists for `gitlab`. The class still exists for `memory` (orchestrator, poc-orchestrator) and `sequential-thinking` (orchestrator, poc-orchestrator, solution-architect) |
| Section 4a, example "qa-engineer and scrum-master for gitlab" | two named-subset GitLab holders | seven |
| Section 5, SEC-T657-04 example | a global `ask` or `deny` on `gitlab_merge_merge_request` is silently overridden "for the five whole-server GitLab holders" | No agent holds that tool. The example is `gitlab_create_merge_request`, overridden for orchestrator, poc-orchestrator and release-manager. `gitlab_merge_merge_request` stays denied in every generated agent file, whatever a user's global rule says (tested) |

Everything else in v1 (the mechanism, the evidence, the residuals for built-in agents and user-owned agent files, the install behaviour) is unchanged.

## 3. Limits stated for the record

- The narrowing is a tool-list narrowing and a policy, not an enforcement: six of the seven roles hold `execute`, and the setup instructions export `GITLAB_PERSONAL_ACCESS_TOKEN` into the environment that starts the assistant, so a shell in those roles can merge, tag, release or push with that token. Reconciling the token scopes in the setup instructions with this is left to T665.
- `create_merge_request` (orchestrator, poc-orchestrator, release-manager) can target any project and branch the token reaches and can start merge request pipelines.
- The CI lint tools (`validate_ci_lint`, `validate_project_ci_lint`) with `dry_run` resolve `include:` entries server-side.
- Not observed in a live run of any assistant.
