# T647 — Rehearse the release job's git commands in the CI image

**ID:** T647
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T641
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Task Decomposition item for T647)
- `docs/artifacts/release-v8-audit-v2.md`, `docs/artifacts/release-documents-ruling-v1.md`
- The user's approval of plan-122 on 2026-10-15 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"; the decisions quoted in the plan's header.

## 1. What and why

Per audit D-5 (the user chose "Image run, no publish"): in a scratch clone, run the release job's git commands in `python:3.12-alpine` with `apk add git` via local docker: `scripts/publish-release.py --skip-api` against a fake tag in a scratch repository, confirming `git log --no-merges --end-of-options <rev> --`, tag listing and the generated `CHANGELOG.md`. No GitLab writes, no tag, no release, no `WIKI_TOKEN`. Acceptance: output recorded (git version in the image, the command lines, the CHANGELOG section); limits stated (API calls are covered by the offline dry run); a short artifact text for the orchestrator to record.

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
