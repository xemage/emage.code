# T879 — Publishing v12.0.0

**ID:** T879
**Owner:** orchestrator
**Status:** done
**Priority:** P0
**Tier:** judgment
**Depends on:** T878
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-20
**Based on:**
- `docs/plans/plan-182-next-release.md` (§ Task Decomposition item 12; Outcome)
- The user's approvals at each step, verbatim: "Yes, merge to develop (Recommended)"; "Yes, merge to main (Recommended)"; "v12.0.0-gate.1 deleted"; "Yes, push the tag (Recommended)"

## 1. What and why

Publish v12.0.0, following `CONTRIBUTING.md` § Cutting a release. Each step needs the user's approval at that moment.

## 2. Output

- MR !708 and MR !709;
- the tag `v12.0.0`;
- the GitLab Release v12.0.0;
- `docs/checkpoints/checkpoint-044-release-v12.0.0.md`.

## 3. Constraints

- No squash on the release merges.
- The tag is never moved or re-created without the user.
- No `docker`.

## 4. Acceptance criteria

- The three tag jobs run on runner #59129270.
- The Release body equals the document.
- The drift check passes.
- `validate-tasks.py` passes before the checkpoint.

## 5. Blocker protocol

Report each blocker with its type and severity.
