# T857 — Root refresh after T855

**ID:** T857
**Owner:** orchestrator
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T856
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-175-batch-aa-opencode-and-td-t849-01.md`
- The user's answer of 2026-11-19, verbatim: "AA + TD-T849-01 go"

## 1. What and why

Run the root refresh once the user approves it at that moment.

## 2. Output

The refreshed root files on the same branch.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 20k.

## 4. Acceptance criteria

See plan-175 § Task Decomposition. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
