# T890 — Batch X: pin-age check, CI-image pin, lock header, release-fetch note

**ID:** T890
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-20
**Completed:** 2026-11-20
**Based on:**
- `docs/plans/plan-188-batch-x-round.md`
- The user's answers of 2026-11-20, verbatim: "X go" and "Approve (Recommended)"

## 1. What and why

Carry out plan-188 § Task Decomposition item 1.

## 2. Output

The commits on `agent/devops-engineer/T890`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Never read secrets or the user's settings files.
- Token budget: 100k.

## 4. Acceptance criteria

See plan-188 § Task Decomposition. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
