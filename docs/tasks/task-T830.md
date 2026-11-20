# T830 — Tracked-debt register v18

**ID:** T830
**Owner:** tech-lead
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-14
**Completed:** 2026-11-14
**Based on:**
- `docs/plans/plan-164-tracked-debt-register-v18.md`
- The user's answer of 2026-11-14, verbatim: "Continue with the next best step"

## 1. What and why

Write register v18 as specified in plan-164 § Task Decomposition.

## 2. Output

`docs/artifacts/tracked-debt-register-v18.md` only, committed on `agent/tech-lead/T830`.

## 3. Constraints

- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No ledger, brief or plan edits.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 50k.

## 4. Acceptance criteria

- Every changed id has a row.
- The counts add up, and the register states whether any open item is above LOW.
- These pass: `validate-tasks.py`, `test_link_integrity`, `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
