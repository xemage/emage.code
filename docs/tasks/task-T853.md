# T853 — Root refresh after the Brave 2.1.5 bump

**ID:** T853
**Owner:** orchestrator
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T852
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-173-brave-2-1-5-pin-bump.md`
- The user's answer of 2026-11-19, verbatim: "Brave 2.1.5 go"

## 1. What and why

Run the root refresh with `scripts/install.sh --projections-only`, once the user approves it at that moment.

## 2. Output

The refreshed root config files on the same branch.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 20k.

## 4. Acceptance criteria

See plan-173 § Task Decomposition. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
