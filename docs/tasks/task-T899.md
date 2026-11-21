# T899 — Batch V fourth round: the release gate's last three ids

**ID:** T899
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-21
**Completed:** 2026-11-21
**Based on:**
- `docs/plans/plan-194-batch-v-fourth-round.md`
- The user's answer of 2026-11-21, verbatim: "V go"

## 1. What and why

Close SEC-T888-03, SEC-T888-02(b) and SEC-T888-01 as specified in plan-194 § Task Decomposition.

## 2. Output

`scripts/verify-release-docs.py` and `tests/functional/test_verify_release_docs.py`, committed on `agent/devops-engineer/T899`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No docker. Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published release document.
- Never read secrets or the user's settings files.
- Token budget: 80k.

## 4. Acceptance criteria

- A test and a mutation per id.
- Every published `docs/releases/v*.md` still passes at its own tag.
- The sweep numbers and the before/after timing are reported.
- `validate-tasks.py`, `test_link_integrity`, `test_team_health*` and the release-docs tests pass.

## 5. Blocker protocol

Report each blocker with its type and severity.
