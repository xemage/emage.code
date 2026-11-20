# T846 — SEC-T837-01: live `opencode debug agent` evidence v2

**ID:** T846
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-170-sec-t837-01-opencode-live-check.md`
- The user's answer of 2026-11-19, verbatim: "SEC-T837-01 go"

## 1. What and why

Run the live check that plan-170 § Task Decomposition item 1 describes, and store the result as evidence v2.

## 2. Output

All on `agent/devops-engineer/T846`:
- `docs/artifacts/mcp-agent-denials-evidence-v2.md`;
- `docs/artifacts/mcp-agent-denials-evidence-v2/raw-*.json`;
- the Status line of `docs/wiki/mcp-servers.md`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No ledger, brief or plan edits.
- No source or generator change.
- No `docker`.
- No model, no API key, no MCP server started, no credentials in the environment.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 60k.

## 4. Acceptance criteria

- The raw output is stored verbatim, with sha256 values.
- A script compares each resolved agent segment with its generated `permission:` map. The comparison is stored.
- Every difference from v1 is explained.
- These pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
