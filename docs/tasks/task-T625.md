# T625 — A full /code-review of the T619 MR by the Tech Lead, as an immutable artifact (S2 of the promotion plan)

**ID:** T625
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T625)
- `implementation/knowledge/commands/code-review.md` (the public command text, your only guide) and skill `code-review`
- The T619 change: merge `3771781` (`git diff 5e07a6b..3771781`): `scripts/publish-release.py`, `scripts/dry-run-publish-release.py`, `.gitlab-ci.yml`, `tests/functional/test_publish_release.py`; `docs/artifacts/security-review-t619-release-job-v1.md`; `docs/tasks/task-T619.md`
- `docs/artifacts/promotion-and-golden-realignment-plan-v1.md` §6.2 (S2)
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

Perform a genuine `/code-review` of the T619 change, in review mode (you must not modify code or any file except your artifact and this brief's Status line). Follow the public command text: the review checklist, artifact versions reviewed and the plan artifact it is meant to match (`plan-120`, `task-T619.md`), severity levels (Must Fix / Should Fix / Nice to Have), remediation suggestions, and the structured `## VERDICT` block with every field the command lists (`Status`, `Reviewed artifacts`, `Must Fix count`, `Should Fix count`, `Nice to Have count`, `Blocker IDs`, `Reviewer`, `Timestamp`), with owner and due point for each condition if `CONDITIONAL_PASS`. Review the actual diff and cite file:line; do not copy the Security Engineer's review. You are the agent being considered for promotion: you are given no information about any golden or held-out check of this command, and you must not look for any.

## 2. Output

`docs/artifacts/code-review-t619-v1.md`, with `Based on:`, the review body and the `## VERDICT` block. One file.

## 3. Constraints

- You have no shell (or only read-only commands where the brief says so). Do not commit, push or merge; the orchestrator does. Do not edit `.claude/`, `.github/` or other derived platform folders.
- **Write access:** your artifact(s) named in §2, plus this brief's `**Status:**` line (set it to `in_review`).
- You may use read-only shell commands (`git show`, `git diff`, `grep`, `ls`).
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one artifact is written (plus the brief's Status line); every field of the command's VERDICT block is present with valid values.
2. Every finding cites a file and line in the T619 diff.
3. No file other than the artifact and the brief is modified.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
