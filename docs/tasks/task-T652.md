# T652 — Publish v8.0.0 (release MRs, main merge, tag)

**ID:** T652
**Owner:** orchestrator
**Status:** done
**Priority:** P0
**Tier:** judgment
**Depends on:** T651
**Affects:** —
**Created:** 2026-10-15
**Completed:** 2026-10-16
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Task Decomposition item for T652)
- `docs/artifacts/release-v8-audit-v2.md`, `docs/artifacts/release-documents-ruling-v1.md`
- The user's approval of plan-122 on 2026-10-15 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"; the decisions quoted in the plan's header.

## 1. What and why

Publish v8.0.0 in the order the user chose ("B1: develop, then main, then tag (Recommended)", 2026-10-15; `docs/artifacts/release-documents-ruling-v1.md` § 5.3; `CONTRIBUTING.md` steps 5-7). **Each outward step needs the user's explicit approval at that moment.** Subagents never merge or tag.

Procedure (corrects the earlier wording "MR develop to main" / "tag on the verified main tip", per the Tech Lead's finding TL-T649-11):
1. Pre-tag readiness checklist, all must hold on the final `release/v8.0.0` tree before the first MR: `docs/releases/v8.0.0.md` contains no `pending` and no `YYYY-MM-DD` (grep), the `Release` line under Gate Verdicts equals the `Status` of `## RELEASE VERDICT`; `python3 scripts/verify-release-docs.py --tag v8.0.0`, `python3 scripts/check-version-consistency.py`, `python3 docs/tasks/validate-tasks.py`, the held-out isolation test pass; the poc-security-audit `scan_secrets` and `ref_containment` tools (if callable) and `git ls-files '.env*'` on `release/v8.0.0`; the user has confirmed audit decision D-4 (`WIKI_TOKEN` Protected and Masked, `v*` tags protected with "Allowed to create" restricted); the user has recorded the risk acceptances named in the Gate Verdicts.
2. Push `release/v8.0.0` (Commits API fallback if `git push` fails; skill `gitlab-api-push-fallback`), verify the tree equals the local tree.
3. MR `release/v8.0.0` to `develop` (merge commit, no squash); merge only when `mergeable` with a green pipeline on the pinned sha, after the user approves.
4. MR `release/v8.0.0` to `main` (merge commit, no squash); after the user approves; merge only when `mergeable` with a green pipeline on the pinned sha.
5. Verify ancestry and tree equality: the release-branch tip is `origin/main^2`; the trees of `main` and the release branch are equal.
6. Tag `v8.0.0` on the release-branch tip (annotated, via the API `POST projects/:id/repository/tags` with `ref=<release tip sha>` if `git push` of the tag fails), after the user approves the tag. Never move or delete a tag. Note the drift gate has a one-release grace window and cannot enforce "main merged before the tag" (TL-T649-13); steps 3-5 are the control.
7. Watch the three tag jobs (`release-docs-gate`, `main-develop-drift-gate`, `release`); report the output, including the GitLab Release description rendering and size.
8. Write `docs/checkpoints/checkpoint-038-release-v8.0.0.md` (phase boundary); archive the release tasks on the release branch before step 3 (the ledger rows of T644-T651 and this task's own row after step 7 through a follow-up MR); the post-release items (G-2 and baseline v22 for the `orchestrator` promotion and the `/skillify` golden case; the Opencode per-agent denies and the Cursor CLI deny list; the tracked debt) are separate.

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
