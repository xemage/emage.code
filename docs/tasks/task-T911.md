# T911 — Batch X: SEC-T909-01 and SEC-T909-02

**ID:** T911
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-22
**Completed:** 2026-11-22
**Based on:**
- `docs/plans/plan-201-batch-x-sec-t909.md`
- The user's answer of 2026-11-22, verbatim: "X go"

## 1. What and why

Fix SEC-T909-01 and SEC-T909-02 as specified in plan-201 § Task Decomposition item 1.

## 2. Output

The edited test file; a report with the old-code and new-code results for each new case.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release. No docker. No image-digest change, no pin bump.
- Never open `tests/golden/held-out/`; never edit `tests/golden/`, a published release document or a derived platform folder.
- Never read secrets or the user's settings files.
- Token budget: 50k.

## 4. Acceptance criteria

- Every old assertion and case stays; the real `.gitlab-ci.yml` still passes.
- Each new refusal case fails on the old code and passes on the new; `'git>=2.54'` in both jobs is accepted.
- `test_ci_hash_pins.py` and `test_pin_bump_checklist.py` pass.

## 5. Blocker protocol

Report each blocker with its type and severity.
