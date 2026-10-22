# T681 — Decision: a per-role GitLab token option (SEC-T665-07)

**ID:** T681
**Owner:** solution-architect
**Status:** pending
**Priority:** P2
**Tier:** standard
**Depends on:** T665
**Affects:** —
**Created:** 2026-10-22
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-22: T681)
- `docs/artifacts/security-review-t665-token-handling-v1.md` (SEC-T665-07), `docs/artifacts/gitlab-token-handling-design-v1.md`

## 1. What and why

With one shared `gitlab` entry, every shell-holding GitLab role (qa-engineer, scrum-master, devops-engineer) inherits the Developer-level `api` token that the three merge-request roles (orchestrator, poc-orchestrator, release-manager, which hold `create_merge_request`) need. A Developer `api` token can push to unprotected branches, create tags and trigger pipelines (runner code execution, unprotected CI variables). Produce a decision artifact with options and a recommendation: two entries (a Planner or Reporter token for the read and issue roles, a separate Developer token for the three MR roles), the generator capability needed (the generator emits one `gitlab` entry today), what each client supports, the cost for adopters, and whether the Developer-level CI/runner exposure sentence belongs in the docs now (it does: say so in the scope table either way). *Acceptance:* the artifact (`docs/artifacts/gitlab-per-role-token-design-v1.md`) with options, a recommendation and a question for the user. **Decision only; the user decides.**

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
