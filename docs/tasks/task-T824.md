# T824 — SEC-T814-01: bump opentelemetry-api to 1.45.2 in both runtime locks

**ID:** T824
**Owner:** devops-engineer
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

Both `implementation/runtime/{security,memory}/requirements-mcp-server.lock.txt`, byte-identical, regenerated with hashes; only `opentelemetry-api` changes.

## 3. Constraints

- Change no other package. No `docker`.
- Do not push, merge, tag or release. Do not edit the ledger, any brief's Status line or the plan.
- Never open `tests/golden/held-out/`. Never read secrets or the user's settings files. Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

As in plan-161 § Addendum 1.

## 5. Blocker protocol

Report each blocker with its type and severity.
