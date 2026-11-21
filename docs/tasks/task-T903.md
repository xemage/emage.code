# T903 — Batch Y: the CI header's bump recipe (TL-T761-08)

**ID:** T903
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-21
**Completed:** 2026-11-21
**Based on:**
- `docs/plans/plan-196-batch-y-shipped-text.md`
- The user's answer of 2026-11-21, verbatim: "Y go"

## 1. What and why

Add the test constants to the bump recipe in the `.gitlab-ci.yml` header comment (plan-196 item 2).

## 2. Output

`.gitlab-ci.yml` (comment only) and tests that quote it.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No docker. Never open `tests/golden/held-out/`. Never edit `tests/golden/`, a published release document or a derived platform folder.
- Never read secrets or the user's settings files.
- Token budget: 30k.

## 4. Acceptance criteria

- No job, value or digest changed.
- The CI lint at the head sha passes and `test_ci_hash_pins.py` passes.

## 5. Blocker protocol

Report each blocker with its type and severity.
