# T646 — Dependency audit of the pinned MCP set and mcp==2.2.0

**ID:** T646
**Owner:** security-engineer
**Status:** pending
**Priority:** P1
**Tier:** judgment
**Depends on:** T641
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Task Decomposition item for T646)
- `docs/artifacts/release-v8-audit-v2.md`, `docs/artifacts/release-documents-ruling-v1.md`
- The user's approval of plan-122 on 2026-10-15 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"; the decisions quoted in the plan's header.

## 1. What and why

Read-only dependency audit (audit D-7): the pinned `npx`/`uvx` MCP packages of `implementation/knowledge/mcp/servers.yaml` and the `mcp==2.2.0` requirement of the PoC scanner server, using the available audit tools (`run_pip_audit`, `run_npm_audit`) where they apply and web sources for advisories otherwise. Record per package a result or an explicit `not covered`, and never claim a clean result for something not run. Grade findings (`SECURITY:*`); `CRITICAL`/`HIGH` blocks. Output: a review text for the orchestrator to record as `docs/artifacts/security-review-t646-dependency-audit-v1.md` (the Security Engineer has no write tool).

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or a release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
