# T893 — Batch V short round: look-alike heading hole and help text

**ID:** T893
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-20
**Completed:** 2026-11-20
**Based on:**
- `docs/plans/plan-190-batch-v-short-round.md`
- The user's answers of 2026-11-20, verbatim: "V go" and "Approve (Recommended)"

## 1. What and why

Carry out plan-190 § Task Decomposition item 1.

## 2. Output

The commits on `agent/devops-engineer/T893`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Never read secrets or the user's settings files.
- Token budget: 70k.

## 4. Acceptance criteria

See plan-190 § Task Decomposition. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
