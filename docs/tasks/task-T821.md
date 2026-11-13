# T821 — Release verdict for v11.0.0

**ID:** T821
**Owner:** release-manager
**Status:** in_progress
**Priority:** P0
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-13
**Based on:**
- `docs/plans/plan-161-release-v11.md` (§ Task Decomposition item 9; § Addenda 1 to 4)
- `docs/artifacts/qa-gate-release-v11-v1.md`; `docs/artifacts/tech-lead-release-v11-v1.md`; `docs/artifacts/security-review-t820-release-v11-v1.md`; `docs/artifacts/security-review-t820-release-v11-addendum-v1.md`
- The user's answers of 2026-11-13 (question dialog, option labels verbatim): plan-161 "Approve (Recommended)"; version "v11.0.0, MAJOR (Recommended)"; probe tag "Yes, probe first (Recommended)".

## 1. What and why

Write `## Gate Verdicts` and `## RELEASE VERDICT` in `docs/releases/v11.0.0.md` from T818 to T820, with `Issued at commit` and the Conditions block (T820 C-1 to C-4). The independent check is `@tech-lead`, who has not edited the release files. After it, only the closed list in `agents/release-manager.md:46` may change.

## 2. Output

`docs/releases/v11.0.0.md`; `verify-release-docs.py --tag v11.0.0` exits 0.

## 3. Constraints

Only that file. Do not push, merge, tag or release.

## 4. Acceptance criteria

The gate passes on the locked parser; each condition has an owner and a deadline; the three accepted-MEDIUM Conditions lines carry every slot (T820 § 3).

## 5. Blocker protocol

Report each blocker with its type and severity.
