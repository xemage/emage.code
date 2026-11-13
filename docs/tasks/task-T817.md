# T817 — Probe tag v11.0.0-gate.1 for the release-gate runner

**ID:** T817
**Owner:** orchestrator
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-13
**Completed:** 2026-11-13
**Based on:**
- `docs/plans/plan-161-release-v11.md` (§ Task Decomposition item 5)
- The user's answer of 2026-11-13 (question dialog, option label verbatim): "Yes, probe first (Recommended)"

## 1. What and why

Push the probe tag `v11.0.0-gate.1` on the tip of `release/v11.0.0`, **with the user's approval at that moment**, to show that `release-docs-gate` and `main-develop-drift-gate` run on runner #59129270 through `gitlab-runner-16028` with `allowed_images` matching. Both gates are expected to fail (no probe document, tag not on `main`), so `release` does not run and nothing is published. The user deletes the probe tag in the web UI afterwards.

## 2. Output

The tag pipeline's id, each job's runner and status, recorded in plan-161.

## 3. Constraints

No tag without the user's approval at that moment. The tag is never moved or re-created without the user.

## 4. Acceptance criteria

Both gate jobs show runner #59129270 (`gitlab-runner-16028`) and start their scripts in the pinned image; `release` does not run.

## 5. Blocker protocol

A job pending with no runner, or an image refused, is reported to the user at once.
