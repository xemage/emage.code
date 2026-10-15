# T652 — Publish v8.0.0 (release MRs, main merge, tag)

**ID:** T652
**Owner:** orchestrator
**Status:** pending
**Priority:** P0
**Tier:** judgment
**Depends on:** T651
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Task Decomposition item for T652)
- `docs/artifacts/release-v8-audit-v2.md`, `docs/artifacts/release-documents-ruling-v1.md`
- The user's approval of plan-122 on 2026-10-15 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"; the decisions quoted in the plan's header.

## 1. What and why

Each step needs the user's explicit approval at that moment: MR `release/v8.0.0` to `develop`; MR `develop` to `main` with merge commits, no squash; tag `v8.0.0` on the verified `main` tip; watch the three tag jobs; write `docs/checkpoints/checkpoint-038-release-v8.0.0.md`. Subagents never merge or tag. The post-release step (G-2 and baseline v22 for the `orchestrator` promotion and the `/skillify` golden case) is a separate plan. Acceptance: the GitLab Release exists with the release document as its body and `CHANGELOG.md` is generated.

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
