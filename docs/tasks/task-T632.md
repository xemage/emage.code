# T632 — Rule the release documents that disagree and the tag / back-merge ordering (audit C-2, C-4)

**ID:** T632
**Owner:** solution-architect
**Status:** done
**Priority:** P1
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T632)
- `docs/artifacts/release-v8-audit-v1.md` C-2, C-3 and C-4; `scripts/verify-release-docs.py`, `scripts/check-main-develop-drift.py`, `scripts/publish-release.py`, `.gitlab-ci.yml`, `CONTRIBUTING.md` (Releasing), `docs/releases/_template.md`, `docs/releases/v7.0.0.md`, `v7.0.1.md`
- `implementation/knowledge/skills/release-workflow/SKILL.md`, `commands/prepare-release.md`, `agents/orchestrator.md` § Release Workflow Preflights
- `docs/decisions/ADR-007-command-contract-authority.md`, `ADR-008-knowledge-document-authority.md`; precedent: the user's decision of one release document at `docs/releases/v<VERSION>.md`
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

Give each disagreement a disposition and the exact held amendment: (a) what `docs/releases/v8.0.0.md` must contain, given `verify-release-docs.py` (requires `## Install`, `## Highlights`, `## RELEASE VERDICT`, `Latest release: v8.0.0`), `release-workflow` § 4 (Summary, Changelog, Migration Guide, Known Issues, Gate Verdicts, Rollback Plan), `/prepare-release`, the orchestrator preflight and `_template.md` (which omits Claude Code and Cline, `.mcp.json`); which of these is the authority per ADR-007/008, and what each other document must say; (b) the tag and back-merge ordering: `CONTRIBUTING.md` step 7 tags on `main` first and back-merges later, the drift gate fails when `main` is ahead of `develop`, and the orchestrator preflight says the tag is created after the MR merges to develop; decide one ordering that the gates accept; (c) how the GitLab Release body should be built now that the CI embeds the whole release document plus a commit-subject changelog (201 of 411 subjects in the range are merge commits): keep, or specify a filter (this is a design question, not an edit: hold it for the user). Re-read the live lines first. Decision only: nothing is applied. A conflict inside tier 1 escalates under P5. ONE consolidated user question (grouped, at most 4 options per group, a recommendation each), a handoff package and a summary table; report hit counts, projected paths and root-drift paths, golden and test coupling (open cases only; held-out coupling is unknown and not checked) and whether a grant or baseline would be needed.

## 2. Output

`docs/artifacts/release-documents-ruling-v1.md`.

## 3. Constraints

- You have no shell (or only read-only commands where the brief says so). Do not commit, push or merge; the orchestrator does. Do not edit `.claude/`, `.github/` or other derived platform folders.
- **Write access:** your artifact(s) named in §2, plus this brief's `**Status:**` line (set it to `in_review`).
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file with `Based on:`; every disagreement has a disposition.
2. No amendment is applied; the user question is answerable in one round.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
