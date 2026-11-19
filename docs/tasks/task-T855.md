# T855 — Batch AA and TD-T849-01

**ID:** T855
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-175-batch-aa-opencode-and-td-t849-01.md`
- The user's answer of 2026-11-19, verbatim: "AA + TD-T849-01 go"

## 1. What and why

Carry out plan-175 § Task Decomposition item 1.

## 2. Output

The commits on `agent/devops-engineer/T855`, and `docs/artifacts/mcp-agent-denials-evidence-v3.md`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 120k.

## 4. Acceptance criteria

See plan-175 § Task Decomposition. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
