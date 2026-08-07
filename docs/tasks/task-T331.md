# Task T331 — Catch up `main` with `develop` via `release/v6.5.0` (GitFlow drift remediation)

**ID:** T331
**Owner:** orchestrator
**Status:** done
**Completed:** 2026-08-07
**Priority:** P1
**Depends on:** —
**Created:** 2026-08-07
**Based on:** `.claude/rules/git-workflow.md`; `docs/checkpoints/checkpoint-001-gitlab-bootstrap.md`;
`docs/checkpoints/checkpoint-release-v6.5.0.md`

## Objective
Land `develop`'s history (up to and including tag `v6.5.0`, commit `f75335c`) onto `main` via a
proper `release/v6.5.0` branch and merge request, per the GitFlow policy documented in
`.claude/rules/git-workflow.md` (`release/* ← develop`, merges to `main`; `main` = "production
releases only (protected)").

## Context
- Phase: Release (drift remediation, not a new feature release)
- User explicitly requested this after noticing `main` was not receiving releases despite the
  documented rule requiring it.
- Initial premise (from the orchestrator's first pass at this task) was that `main` was simply
  173 commits behind, last touched 2026-06-16, reaching only `v6.0.2` — sourced from a stale
  local `main` ref that had not been re-fetched from origin. This was WRONG and was caught and
  corrected mid-task (see Outcome).
- `docs/checkpoints/checkpoint-001-gitlab-bootstrap.md` confirms the original intent: "GitFlow
  with `develop` as default; `main` reserved for releases." No ADR reverses this.
- GitLab project `em-age/emage.code`: `main` protected (push=[No one], merge=[Maintainers],
  allow_force_push=false). Project `merge_method: merge`, `squash_option: default_on` — squash
  must be explicitly disabled per-merge for release branches to preserve history, matching the
  pre-existing non-squashed `release/v6.0.3 → main` merge commit already in `main`'s log.

## What actually happened (see full outcome below)
This task was first delegated to `@release-manager` under the orchestrator, which correctly
discovered the true state of `main` (not what the initiating brief assumed), found `main` and
`develop` had genuinely diverged since their common ancestor `363aeb8` (v6.0.3) — `main`
independently received releases v6.0.4, v6.0.5, v6.2.0–v6.4.2 via the documented `release/* →
main` flow (never abandoned as first assumed), while `develop`'s `chore/backmerge-*` merges
reconciled v6.2.0/v6.3.0/v6.4.0/v6.4.1 back but never v6.0.4 or v6.4.2. This produced 65
conflicting files on MR `release/v6.5.0 → main` (!103), including security-sensitive CWSO
runtime code and agent-permission-grant files. Resolving required content judgment outside a
mechanical branch/MR/merge task, so the orchestrator correctly stopped and escalated
(`technical` + `unclear_requirements`, `critical`) rather than resolving unilaterally — no
destructive or unscoped action was taken at that point.

The user reviewed the escalation and decided: resolve by taking `develop`'s side throughout
(verified, not assumed — `main` had zero independent commits on any conflicting path beyond
stale release-bundling snapshots), with a dedicated security spot-check on the 3 CWSO runtime
files before merging. This was then executed directly (not re-delegated) after a `SendMessage`
attempt to resume the backgrounded orchestrator was blocked by the Claude Code auto-mode
permission classifier.

## Acceptance Criteria
- [x] `release/v6.5.0` branched from `origin/develop` tip `f75335c`, pushed to origin
- [x] MR `release/v6.5.0 → main` (!103) opened, referencing this task and `docs/releases/v6.5.0.md`
- [x] Real divergence (not simple lag) identified and independently re-verified before acting
- [x] All 65 conflicts resolved by taking `develop`'s side, verified byte-identical to
      `origin/develop` post-resolution (`git diff origin/develop` → empty)
- [x] Dedicated security review of the 3 CWSO runtime files (`ast_conflict_check.py`,
      `concurrent_merge.py`, `mcp_client.py`) — PASS, develop's version strictly additive
      (defensive parsing helpers, extra type guards), nothing security-relevant dropped
- [x] Full test suite green post-resolution (270 tests), registry + sync drift checks clean
- [x] MR pipeline green (lint/verify/sync/test stages; no `release` job, as expected —
      tag-triggered only)
- [x] Merged as a real, non-squashed merge commit (`squash=false` explicit via API — required
      because project default is `squash_option: default_on`), source branch removed
- [x] Post-merge pipeline on `main` green
- [x] Content verified identical between `origin/main` and `origin/develop` (0 diff) after merge
- [ ] ~~`origin/main` verified to reach tag `v6.5.0` via `git merge-base --is-ancestor`~~ — does
      NOT hold literally. GitLab's merge API materialized a new commit object with identical
      tree and message rather than reusing `f75335c` as a direct parent, so the tag (which
      points at the `develop`-side commit) is not an ancestor of `main`'s new tip by SHA. This is
      a cosmetic/technical gap, not a functional one: content equivalence is verified directly
      (0 diff). Noted here rather than silently claimed as passing.
- [x] No new tags created (existing `v6.5.0` tag on `develop`'s commit was left as-is, correctly)
- [x] `develop` untouched by the main-sync work itself (only this task-brief follow-up touches it)
- [x] No destructive git operations used at any point

## Outcome (2026-08-07)
`main` (`origin/main`) tip is now `5d5fd00` — a real merge commit with two parents
(`febd85a`, the prior `main` tip at v6.4.2, and a GitLab-materialized commit content-identical to
`release/v6.5.0`). `main`'s tree is verified byte-identical to `origin/develop`. Post-merge
pipeline on `main` (`2739676142`) succeeded. MR: <https://gitlab.com/em-age/emage.code/-/merge_requests/103>.

Process note for future releases: the `release/vX.Y.Z → main` step needs to actually happen
every release, not just be documented — this drift accumulated silently across 8+ releases
before being noticed. Consider adding a CI check that fails if `main` falls more than one
release behind `develop`, so this class of drift surfaces immediately instead of requiring a
manual catch-up years later.
