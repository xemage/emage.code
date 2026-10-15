# T660 — Named GitLab tools for qa-engineer and scrum-master (SEC-T657-02)

**ID:** T660
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** T657
**Affects:** —
**Created:** 2026-10-15
**Completed:** 2026-10-15
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Addendum 6: T660)
- `docs/artifacts/security-review-t657-tool-name-mapping-v1.md` (SEC-T657-02), the T650 re-check (SEC-T657-02 stays MEDIUM; minimum fix: qa-engineer and scrum-master), `docs/artifacts/mcp-tool-name-mapping-v1.md`
- The user's decision of 2026-10-15 (AskUserQuestion, verbatim option label): "Fix now: named tools for qa-engineer and scrum-master (Recommended)"

## 1. What and why

On GitHub Copilot/VS Code the generator now renders `mcp__gitlab` as `gitlab/*`, so seven agents hold about 276 GitLab tools (merge, push, delete included), which qa-engineer and scrum-master do not need. Replace the bare `mcp__gitlab` in `implementation/knowledge/agents/qa-engineer.md` and `implementation/knowledge/agents/scrum-master.md` by named tools: read each agent's body, `AGENTS.md` role notes and commands it owns to establish what the role does with GitLab (scrum-master: create and update issues, notes, labels, milestones, list and read; qa-engineer: create issues and notes for bugs, read issues, merge requests, pipelines and jobs); take the exact tool names from the pinned `@zereight/mcp-gitlab@2.2.5` (its README at that tag or a live MCP `tools/list` through `npx -y @zereight/mcp-gitlab@2.2.5` with a dummy `GITLAB_PERSONAL_ACCESS_TOKEN` and no network call beyond what listing needs; if listing needs the network or the token, read the source at the tag instead and say so). Never grant merge, push, file-write, delete, branch/tag/release creation or any generic API-request tool to these two roles. The five other holders (devops-engineer, orchestrator, release-manager, poc-devops-engineer, poc-orchestrator) keep `mcp__gitlab`. Extend `PlaywrightGrantSetTests`-style tests in `tests/functional/test_mcp_package_pins.py` (or a new module) with a GitLab grant-set test: exactly the seven roles hold gitlab access; qa-engineer and scrum-master hold only the named tools, none of which is in a forbidden list (merge, push, delete, create_branch, create_tag, create_release, api request); the five keep the whole server. Regenerate (`node implementation/scripts/sync.mjs --root implementation`, `python3 implementation/scripts/generate-registry.py --root implementation`) and declare the root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths, one comment line starting `Declared 2026-10-15 by T660 (`); do NOT refresh the root install. Update the docs that say seven agents hold the whole GitLab server (`docs/wiki/mcp-servers.md`, `AGENTS.md`, `implementation/AGENTS.md`) to say five do and two hold named tools, on Claude Code and Copilot alike.

## 2. Output

The two edited agent files, regenerated projections, the test, doc edits, one local commit, and a report with both tool lists and how each was verified.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN` or a real GitLab token; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates: sync --check, generate-registry --check, check-maturity.py --root implementation, scorecard.py --check, validate-tasks.py, check_evaluator_hash, held-out isolation test, and the full suite `python3 tests/run.py > file` (summary lines).
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

1. qa-engineer and scrum-master hold named GitLab tools only, none destructive; the five others unchanged.
2. The test pins both lists and the five holders.
3. All gates and the suite pass; the root drift is declared.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
