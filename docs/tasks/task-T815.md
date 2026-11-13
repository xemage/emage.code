# T815 — Open release/v11.0.0 and bump the version markers

**ID:** T815
**Owner:** release-manager
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-13
**Completed:** 2026-11-13
**Based on:**
- `docs/plans/plan-161-release-v11.md` (plan-161 § Task Decomposition item 3)
- `docs/artifacts/release-v11-audit-v1.md` (T813)
- The user's answers of 2026-11-13 (question dialog, option labels verbatim): plan-161 "Approve (Recommended)"; version "v11.0.0, MAJOR (Recommended)"; probe tag "Yes, probe first (Recommended)".

## 1. What and why

As in plan-161 § Task Decomposition item 3: wave 2 of the v11.0.0 release, on `release/v11.0.0`.

## 2. Output

The version markers and stale version references that `scripts/check-version-consistency.py` names, on `release/v11.0.0`.

## 3. Constraints

- Work only on `release/v11.0.0` in `/home/emage/Code/emage/worktrees/release-v11.0.0`. Conventional Commits ending with `Co-Authored-By: Claude <noreply@anthropic.com>`.
- Do not push, merge, tag or release. Do not edit the ledger, any brief's Status line or the plan. No `docker`.
- Never open `tests/golden/held-out/`. Never read secrets or the user's settings files. Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

As in plan-161 § Task Decomposition item 3.

## 5. Blocker protocol

Report each blocker with its type and severity.
