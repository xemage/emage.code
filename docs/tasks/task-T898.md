# T898 — Tracked-debt register v31

**ID:** T898
**Owner:** tech-lead
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-21
**Completed:** 2026-11-21
**Based on:**
- `docs/plans/plan-193-tracked-debt-register-v31.md`
- The user's answer of 2026-11-21, verbatim: "v31 go"

## 1. What and why

Write register v31 as specified in plan-193 § Task Decomposition.

## 2. Output

`docs/artifacts/tracked-debt-register-v31.md` only, committed on `agent/tech-lead/T898`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No ledger, brief or plan edits.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 50k.

## 4. Acceptance criteria

- Every changed id has a row.
- The counts add up.
- These pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
