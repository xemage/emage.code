# T627 — Run a real /skillify interview with the user (GitLab API fallback workflow) and apply the /skillify template fix

**ID:** T627
**Owner:** orchestrator
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T627)
- `implementation/knowledge/commands/skillify.md`, skill `skillify`, `implementation/knowledge/schemas/skill.schema.json`
- `docs/artifacts/promotion-and-golden-realignment-plan-v1.md` §6.2 (S3), §4 (F-2) and §13 Q2
- The user's answers of 2026-10-14: "Run it now, I'll supply the workflow (Recommended)", workflow "GitLab API fallback (Recommended)" (the branch and tag steps via the GitLab API when `git push` fails; never touch credential configuration without asking), and "Yes, amend (Recommended)" for the template's `maturity: experimental`.
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

A genuine `/skillify` run: the orchestrator runs the four-round interview with the user for the workflow "GitLab API fallback for the branch and tag steps when `git push` fails", produces one skill `implementation/knowledge/skills/<name>/SKILL.md` that passes `skill.schema.json` (with `maturity: experimental` in the frontmatter), regenerates the mirrors and registry, and the user approves the draft. Also apply the approved template fix to `skillify.md` (the frontmatter template gains `maturity: experimental`). This task is interactive: it cannot be dispatched to a subagent. The skill count goes from 26 to 27 (distribution snapshot in `tests/functional/test_check_maturity.py` updated if it asserts counts).

## 2. Output

The new skill, the amended command, regenerated mirrors and registry, the drift baseline, gate results.

## 3. Constraints

- The orchestrator executes this; the interview needs the user. Declare root drift; do NOT refresh the root install.
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. The user approved the draft in the interview.
2. The skill passes the schema and all gates; the template fix is applied exactly as decided.
3. The skill is a genuine output of the command (it is the exit artifact for the `/skillify` golden case in T628).

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
