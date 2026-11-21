# T908 — Batch X: SEC-T897-01

**ID:** T908
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-21
**Completed:** 2026-11-21
**Based on:**
- `docs/plans/plan-199-batch-x-sec-t897-01.md`
- The user's answer of 2026-11-21, verbatim: "X go"

## 1. What and why

Fix SEC-T897-01 as specified in plan-199 § Task Decomposition item 1.

## 2. Output

The edited test file and checklist page; a report with the old-code and new-code results for each new case.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release. No docker. No image-digest change, no pin bump.
- Never open `tests/golden/held-out/`; never edit `tests/golden/`, a published release document or a derived platform folder.
- Never read secrets or the user's settings files.
- Token budget: 50k.

## 4. Acceptance criteria

- Every old assertion and case stays; the real `.gitlab-ci.yml` still passes.
- Each new case fails on the old code and passes on the new.
- `test_ci_hash_pins.py` and `test_pin_bump_checklist.py` pass.

## 5. Blocker protocol

Report each blocker with its type and severity.
