# T823 — SEC-T784-01: fixed Node versions in PREREQUISITES

**ID:** T823
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-13
**Completed:** 2026-11-13
**Based on:**
- `docs/plans/plan-161-release-v11.md` (§ Addendum 1)
- The user's answers of 2026-11-13 (question dialog, option labels verbatim): plan-161 "Approve (Recommended)"; version "v11.0.0, MAJOR (Recommended)"; probe tag "Yes, probe first (Recommended)".

## 1. What and why

As in plan-161 § Addendum 1: wave 1 of the v11.0.0 release, on `develop` before the release branch.

## 2. Output

`implementation/PREREQUISITES.md` (lines 4 and 227, and any other Node floor in that file).

## 3. Constraints

- Only `implementation/PREREQUISITES.md` changes. No shell (the orchestrator commits).
- Do not push, merge, tag or release. Do not edit the ledger, any brief's Status line or the plan.
- Never open `tests/golden/held-out/`. Never read secrets or the user's settings files. Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

As in plan-161 § Addendum 1.

## 5. Blocker protocol

Report each blocker with its type and severity.
