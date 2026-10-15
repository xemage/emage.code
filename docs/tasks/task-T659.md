# T659 — Root refresh 19

**ID:** T659
**Owner:** orchestrator
**Status:** pending
**Priority:** P0
**Tier:** standard
**Depends on:** T658
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Addendum 5: T659)
- `docs/artifacts/security-review-t655-fetch-removal-v1.md` (SEC-T655-03), `docs/artifacts/security-review-t657-tool-name-mapping-v1.md`
- The user's approval of 2026-10-15 (AskUserQuestion, verbatim option label): "Yes, refresh (Recommended)"

## 1. What and why

After T658 merges, run `scripts/install.sh --target <clean worktree> --platform all --projections-only`, commit the refreshed projections and empty `tests/_baselines/root-install-drift.json`. Closes SEC-T655-03 (the repository root self-install still ships `fetch` and the unrestricted `playwright`). The user's local `.vscode/mcp.json` and `.claude/settings.json` are never read or edited. The hand-edited root `AGENTS.md` is checked against the installed rendering.

## 2. Output

The refreshed root projections, the empty drift baseline, one MR.

## 3. Constraints

Orchestrator executes; no agent edits derived folders; no held-out id anywhere; no `.env*` files.

## 4. Acceptance criteria

`tests/functional/test_root_install_parity.py` passes with an empty drift list; the full suite passes; no `fetch` entry and no whole-server `mcp__playwright` remains in the root configs and agent files.

## 5. Blocker protocol

Report each blocker with its type and severity.
