# T645 — Write docs/releases/v8.0.0.md

**ID:** T645
**Owner:** release-manager
**Status:** done
**Priority:** P1
**Tier:** judgment
**Depends on:** T644
**Affects:** —
**Created:** 2026-10-15
**Completed:** 2026-10-15
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Task Decomposition item for T645)
- `docs/artifacts/release-v8-audit-v2.md`, `docs/artifacts/release-documents-ruling-v1.md`
- The user's approval of plan-122 on 2026-10-15 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"; the decisions quoted in the plan's header.

## 1. What and why

Create `docs/releases/v8.0.0.md` from `docs/releases/_template.md` and `docs/artifacts/release-v8-audit-v2.md` §3-§6 (Migration M-1..M-9 including the SEC-002 note for v7.x installs, Known issues, the `tech-lead` maturity change, the sign-off conflict disclosure of §8). Decide and record the `RELEASE VERDICT` counting rule (audit D-2, basis §1.4) and the Rollback Plan label (audit D-6: test the rollback once on a scratch project or write "not tested"). Repository files in the document are code spans or absolute URLs (the gate link-checks relative links). The `## Gate Verdicts` and `## RELEASE VERDICT` sections are completed by T651. Acceptance: `python3 scripts/verify-release-docs.py --tag v8.0.0` passes up to the sections reserved for T651 (state which); no other file changed; one local commit.

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
