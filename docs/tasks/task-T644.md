# T644 — Release branch, version markers and stale claims

**ID:** T644
**Owner:** release-manager
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T643
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Task Decomposition item for T644)
- `docs/artifacts/release-v8-audit-v2.md`, `docs/artifacts/release-documents-ruling-v1.md`
- The user's approval of plan-122 on 2026-10-15 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"; the decisions quoted in the plan's header.

## 1. What and why

Open `release/v8.0.0` from `develop` (after T643). Bump the four version markers (`README.md:14`, `docs/wiki/README.md:6`, `docs/wiki/home.md:5`, `implementation/README.md:6`) to `Latest release: v8.0.0`, fix the other stale version lines of `docs/artifacts/release-v8-audit-v2.md` C-1 (`README.md:201`, `docs/wiki/implementation-guide.md:5` and `:41`, `implementation/README.md:4` and `:56`) and the stale component counts it lists in C-7 (27 vs 28 agents, 18 or 16 vs 19 commands, "two remote servers" vs four, manual-copy tables without `implementation/runtime/`). Acceptance: `python3 scripts/check-version-consistency.py` passes at v8.0.0; only those files changed; one local commit, not pushed.

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
