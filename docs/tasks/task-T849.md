# T849 — SEC-T702-08: check and draft the upstream report to the Brave project

**ID:** T849
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-172-batch-p-brave-upstream-report.md`
- The user's answer of 2026-11-19, verbatim: "P go"

## 1. What and why

Carry out plan-172 § Task Decomposition item 1.

## 2. Output

`docs/artifacts/brave-upstream-report-draft-v1.md` only, committed on `agent/devops-engineer/T849`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No ledger, brief or plan edits.
- No post to any external service.
- No `docker`.
- Do not run the package.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 50k.

## 4. Acceptance criteria

- The shipped code and upstream are each checked, with versions and commit ids.
- An existing upstream report is searched for.
- The draft discloses nothing about the user or the project.
- These pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
