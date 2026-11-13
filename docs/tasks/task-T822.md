# T822 — Publish v11.0.0

**ID:** T822
**Owner:** orchestrator
**Status:** in_progress
**Priority:** P0
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-13
**Based on:**
- `docs/plans/plan-161-release-v11.md` (§ Task Decomposition item 10)
- `docs/releases/v11.0.0.md` (§ RELEASE VERDICT, Conditions: T820 C-2, C-3, C-4; T818 C3)

## 1. What and why

Publish v11.0.0 in the order of `CONTRIBUTING.md` § Cutting a release, **each step with the user's explicit approval at that moment**: `release/v11.0.0` to `develop`, then to `main` (no squash), then the tag `v11.0.0` on the release branch's tip (pushed as `refs/tags/v11.0.0` only), then the tag pipeline, the Release body against the document, `check-main-develop-drift.py`, and checkpoint-043.

## 2. Output

The tag, the GitLab Release, checkpoint-043, the plan's Outcome.

## 3. Constraints

The tag is never moved or re-created without the user. No `gate` ref on the remote before and after the tag push (C-4). Tag before 2027-01-28, with Brave `latest` 2.1.4 and the audit command passing on the tag day (C-2).

## 4. Acceptance criteria

All three tag jobs run on runner #59129270 (C-3); the Release exists with the document's body; drift `releases_behind=0`.

## 5. Blocker protocol

A failing release job: fix forward or the manual fallback, never a moved tag without the user.
