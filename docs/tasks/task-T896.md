# T896 — Batch X small round: whole apk-add pairing and future publication date

**ID:** T896
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-21
**Completed:** 2026-11-21
**Based on:**
- `docs/plans/plan-192-batch-x-small-round.md`
- The user's answers of 2026-11-21, verbatim: "X go" and "Approve (Recommended)"

## 1. What and why

Carry out plan-192 § Task Decomposition item 1.

## 2. Output

The commits on `agent/devops-engineer/T896`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Never read secrets or the user's settings files.
- Token budget: 50k.

## 4. Acceptance criteria

See plan-192 § Task Decomposition. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
