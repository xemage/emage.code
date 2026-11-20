# T884 — Batch V: the tag jobs and the CI pins (with SEC-T768-04)

**ID:** T884
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-20
**Completed:** 2026-11-20
**Based on:**
- `docs/plans/plan-184-batch-v-release-gate.md`
- The user's answers of 2026-11-20, verbatim: "V go" and "Approve (Recommended)"

## 1. What and why

Carry out plan-184 § Task Decomposition item 2.

## 2. Output

The commits on `agent/devops-engineer/T884`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Never read secrets or the user's settings files.
- Token budget: 80k.

## 4. Acceptance criteria

See plan-184 § Task Decomposition. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
