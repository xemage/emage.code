# T859 — Batch X: CI images, the CA control and runner settings

**ID:** T859
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-177-batch-x-ci-images-ca-runner.md`
- The user's answer of 2026-11-19, verbatim: "X + AB go"

## 1. What and why

Carry out plan-177 § Task Decomposition item 1.

## 2. Output

The commits on `agent/devops-engineer/T859`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 120k.

## 4. Acceptance criteria

See the plan's § Task Decomposition. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
