# Task T309 — Cut the release (STOP FIRST)

**ID:** T309
**Owner:** release-manager
**Status:** pending
**Priority:** P0
**Depends on:** T308
**Created:** 2026-07-31
**Completed:** —
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Cut and tag the release documented in T308, following this repo's mandatory Release Workflow
Preflights, and then HARD STOP the entire plan until the user explicitly confirms they want
execution to continue into Wave 2.

## Inputs
- `docs/releases/v<X.Y.Z>.md` (from T308)
- `AGENTS.md` § "Release Workflow Preflights"; `.claude/agents/orchestrator.md` § same

## Expected outputs
- A merged release MR to `develop`/`main` per this repo's GitFlow.
- A published GitLab release / tag `v<X.Y.Z>`.

## Acceptance criteria
1. **STOP FIRST**: present the release diff and `docs/releases/v<X.Y.Z>.md` to the user and wait
   for explicit confirmation before tagging or pushing anything.
2. CI is green on `develop` for the commits containing T301/T307 before proceeding.
3. Release MR opened from a `release/v<X.Y.Z>` branch — never committed directly to develop/main.
4. After merge: `glab release create v<X.Y.Z> --ref v<X.Y.Z> --name v<X.Y.Z> -F docs/releases/v<X.Y.Z>.md`
   — no ad-hoc inline `--notes`.
5. `glab release view v<X.Y.Z>` shows the release; tag exists on `origin`.
6. **HARD STOP**: after this task, do not begin Wave 2 (T302) or any later wave until the user has
   explicitly confirmed the release is cut and told you to continue. This is a mandatory pause, not
   an optional courtesy.
7. Per R8, paste the literal `glab release view` output into Execution notes.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
