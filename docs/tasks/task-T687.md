# T687 — Tracked-debt register v2

**ID:** T687
**Owner:** tech-lead
**Status:** done
**Priority:** P2
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-23
**Completed:** 2026-10-23
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-23: the policy for LOW findings)
- `docs/artifacts/tracked-debt-register-v1.md` (204 ids), `docs/tasks/completed-tasks.md` (rows T661 to T685), the review artifacts of T662 to T685, `docs/artifacts/brave-audit-acceptance-v1.md` and `-v2.md`, `docs/artifacts/gitlab-token-handling-design-v1.md`, `docs/artifacts/gitlab-per-role-token-design-v1.md`
- The user's decision of 2026-10-23 (AskUserQuestion, label verbatim): "Track LOW items as debt, stop chasing (Recommended)"

## 1. What and why

Tracked-debt register v2 (tech-lead): walk all 204 ids of v1 and give each its status now with closing evidence; record the new ids introduced by the reviews of T662 to T685 (one row each); group the open items by theme with the LOW policy applied (MEDIUM and higher closed or accepted by the user; LOW items stay as debt with an owner; no new task per round); update the list of user actions and decisions that have no task; list the accepted risks with the user's words and dates. T677 and T686 are in flight and are treated as open. *Acceptance:* `docs/artifacts/tracked-debt-register-v2.md` exists; every v1 row is accounted for; every status claim is traceable to a row or artifact, or marked (unverified); no credential-like value; `python3 docs/tasks/validate-tasks.py` and `python3 -m unittest tests.functional.test_link_integrity tests.performance.test_team_health` pass.

## 2. Output

`docs/artifacts/tracked-debt-register-v2.md`.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any other brief's Status line.
- Documentation artifact only: no code, test, knowledge or generated file changes.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
