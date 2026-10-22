# T683 — Anchored documentation assertion for the Developer-level exposure sentence and the Reporter profile (T681 option A)

**ID:** T683
**Owner:** qa-engineer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Depends on:** T674
**Affects:** —
**Created:** 2026-10-22
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-22: T683)
- `docs/artifacts/gitlab-per-role-token-design-v1.md` (section 8 and the work item), the user's decision of 2026-10-22 (AskUserQuestion, verbatim option labels): "A: status quo + exposure sentence (Recommended)" and "Yes, document it (Recommended)"

## 1. What and why

T681 option A: after T674 has written the Developer-level exposure sentence and the 'Reporter profile' section in `implementation/PREREQUISITES.md` (and the pointer in the wiki), add the anchored documentation assertions that pin them: the exposure sentence lives in the 'Scope and role' rules of the 'GitLab token' section and names push to unprotected branches, tags and pipelines at Developer level; the Reporter profile section names the three roles that hold `create_merge_request` (derived from the agent sources, not hard-coded) and says a Reporter/Planner token cannot create merge requests. Anchor each assertion to its section (no whole-file regex), add in-memory mutation tests that delete the sentence and the section, and keep the existing pins of `tests/functional/test_gitlab_token_handling.py`. *Acceptance:* the assertions and their mutation tests; all gates and the suite pass. Test files only.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; do not modify `tests/golden/**`. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`; never use or print a real token. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
