# T833 — Tracked-debt register v19

**ID:** T833
**Owner:** tech-lead
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-14
**Completed:** 2026-11-14
**Based on:**
- `docs/plans/plan-166-tracked-debt-register-v19.md`
- The user's answer of 2026-11-14, verbatim: "v19 go"

## 1. What and why

Write register v19 as specified in plan-166 § Task Decomposition.

## 2. Output

`docs/artifacts/tracked-debt-register-v19.md` only, committed on `agent/tech-lead/T833`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No ledger, brief or plan edits.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 40k.

## 4. Acceptance criteria

- Every changed id has a row.
- The counts add up.
- These pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
