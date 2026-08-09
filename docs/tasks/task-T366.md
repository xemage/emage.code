# Task T366 — Release v6.9.0 (MCP remote transport alignment)

**ID:** T366
**Owner:** release-manager
**Status:** pending
**Priority:** P0
**Depends on:** T365
**Created:** 2026-08-09
**Based on:** CONTRIBUTING.md § "Cutting a release"; docs/tasks/task-T358.md, task-T350.md,
task-T347.md, task-T337.md (precedent)

## Objective
Cut and publish v6.9.0, packaging plan-030's MCP remote transport fixes (T360-T365), following the
exact precedent in `CONTRIBUTING.md` § "Cutting a release" and the most recent successful release
tasks (T358 for a MINOR bump, T350 for the PUT-first / verification pattern).

## Context
- Phase: Release
- Current latest tag: `v6.8.0`. Target: `v6.9.0` — MINOR bump per the user's explicit request,
  unless T360-T365's actual outcome turns out to be a breaking change (it is not expected to be;
  confirm before tagging).
- **Classification call:** default to MINOR/Bug-Fixes-and-Chores framing (transport-name
  correction, no API/behavior contract change for any consumer that was already working — Cline
  users get a fix, not a new capability; VS Code and Gemini users who were silently missing/using a
  wrong field for remote MCP get a fix). If T360's audit surfaced something bigger in practice
  (e.g. a platform where remote MCP was completely non-functional until now), call that out in the
  release notes' Highlights, matching v6.8.0's Cline-feature-classification precedent for anything
  genuinely new-capability-shaped; otherwise this is Bug Fixes.
- **Breaking changes:** expected "None" — verify this is actually true (no removed fields, no
  consumer that depended on the old value now failing) before writing that in the release doc.

## Inputs
- `docs/releases/_template.md`
- T364's draft release-note bullet
- T365's final validation gate PASS

## Constraints
- Follow `CONTRIBUTING.md` § "Cutting a release" steps 1-8 exactly, including the PUT-first squash
  sequence for any `release/*→main` merge (that is T367, not this task — this task only covers the
  `release/v6.9.0 → develop`... no: per precedent (T358), the MR flow used was
  `docs/release-v6.9.0` branch → develop first (release docs + version markers), THEN a
  `release/v6.9.0` branch cut for the `→ main` sync in the follow-up task. Confirm current
  precedent in task-T358.md/task-T359.md before assuming the exact branch name sequence, and
  follow whichever the repo's actual established two-step pattern is (docs-to-develop, then
  release-to-main), not a single-step guess.
- Full verification bar green (same commands as T365) before merging.
- Independent orchestrator re-verification of the diff before merge — do not just trust
  release-manager's self-report.
- No `--no-verify`, no force-push, no direct commits to `develop`/`main`.

## Expected Outputs
- `docs/releases/v6.9.0.md`
- Version markers bumped (`README.md`, `docs/wiki/README.md`, `docs/wiki/home.md` — "Latest
  release: vX.Y.Z")
- MR (docs branch → develop) merged
- Tag `v6.9.0` created and pushed
- Tag pipeline watched to green (release-docs-gate, main-develop-drift-gate, release job)
- GitLab Release confirmed live via API (not just assumed from pipeline success)

## Acceptance Criteria
1. `python3 scripts/verify-release-docs.py --tag v6.9.0` passes locally before opening the MR.
2. `docs/releases/v6.9.0.md` includes "Latest release: v6.9.0", `## Install`, `## Highlights`, and
   an accurate Breaking Changes section.
3. MR merged only after full verification bar green + independent orchestrator re-verification.
4. Tag `v6.9.0` pushed; tag pipeline green.
5. `glab release view v6.9.0` (or equivalent API call) confirms the release is live with notes
   sourced from `docs/releases/v6.9.0.md` (no ad-hoc inline `--notes`).

## Blocker Protocol
Report blockers as: type + severity + proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
