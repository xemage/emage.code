# Task T394 — Release v6.10.0 (MCP settings hardening + merge-safety + provenance)

**ID:** T394
**Owner:** release-manager
**Status:** in_progress
**Priority:** P0
**Depends on:** T382 (plan-034 final proof point)
**Created:** 2026-08-10
**Based on:** CONTRIBUTING.md § "Cutting a release"; docs/tasks/task-T366.md, task-T358.md,
task-T350.md, task-T337.md (precedent); docs/tasks/completed-tasks.md entries T368-T393, T382

## Objective
Cut and publish v6.10.0, packaging everything merged to `develop` since v6.9.0 was tagged:
plan-031 (installer MCP JSON merge-safety pilot, T368-T372), plan-032 (`render_installed_agents.py`
Cline platform-map fix, T373-T376), plan-033 (MCP settings hardening: merge-safety extended to all
7 platforms, secret guard, schema validation, e2b/redis/figma/notion removal, T377-T388 +
T383-T385), and plan-034 (MCP merge provenance tracking + ADR-002, T389-T393, T382). Follows the
exact precedent in `CONTRIBUTING.md` § "Cutting a release" and the most recent successful release
task (T366 for a MINOR bump).

## Context
- Phase: Release
- Current latest tag: `v6.9.0`. Target: `v6.10.0` — MINOR bump per the user's explicit request.
- **Note on scope:** T360-T365 (plan-030, MCP remote transport alignment) is explicitly EXCLUDED
  from this release's notes — it was already shipped as v6.9.0 (see `docs/releases/v6.9.0.md` and
  `docs/tasks/task-T366.md`). Re-listing it as new in v6.10.0 would misrepresent the changelog;
  verified directly against `docs/tasks/completed-tasks.md` and the `v6.9.0` tag's own content
  rather than assumed.
- **Classification call:** MINOR — one genuinely new-capability item (per-platform MCP merge-safety
  is new protective behavior; provenance-tracking sidecar mechanism is new), several Fixed items
  (Cline platform-map omission), and a Removed item (four MCP servers deleted per explicit user
  request). No Breaking changes: the merge-safety change is strictly additive protection, the
  provenance sidecars are new files alongside existing output, and the `--force-prune-keys` bridge
  used internally by T382 is opt-in only (never triggered by a plain `--update`).
- **Breaking changes:** verified "None" — no schema/API/stdio-server contract changed for any
  platform; `sync.mjs --check` reports 0 drift; full test suite green.

## Inputs
- `docs/releases/_template.md`
- `docs/tasks/completed-tasks.md` entries T368-T393, T382 (source of truth for release-note content)
- T382's final validation (plan-033/plan-034 final proof point, PASS)

## Constraints
- Follow `CONTRIBUTING.md` § "Cutting a release" steps 1-8 exactly, including the PUT-first squash
  sequence for the `release/*→main` merge (that is T395, not this task).
- Follow the repo's established two-step pattern: `docs/release-v6.10.0` branch → develop first
  (release docs + version markers), then a `release/v6.10.0` branch cut for the `→ main` sync in
  the follow-up task (T395).
- Full verification bar green before merging.
- Independent orchestrator re-verification of the diff before merge.
- No `--no-verify`, no force-push, no direct commits to `develop`/`main`.

## Expected Outputs
- `docs/releases/v6.10.0.md`
- Version markers bumped (`README.md`, `docs/wiki/README.md`, `docs/wiki/home.md` — "Latest
  release: vX.Y.Z")
- Checkpoint per checkpoint-protocol skill
- MR (docs branch → develop) merged
- Tag `v6.10.0` created and pushed
- Tag pipeline watched to green (release-docs-gate, main-develop-drift-gate, release job)
- GitLab Release confirmed live via API (not just assumed from pipeline success)

## Acceptance Criteria
1. `python3 scripts/verify-release-docs.py --tag v6.10.0` passes locally before opening the MR.
2. `docs/releases/v6.10.0.md` includes "Latest release: v6.10.0", `## Install`, `## Highlights`,
   and an accurate Breaking Changes section.
3. MR merged only after full verification bar green + independent orchestrator re-verification.
4. Tag `v6.10.0` pushed; tag pipeline green.
5. GitLab API confirms the release is live with notes sourced from `docs/releases/v6.10.0.md` (no
   ad-hoc inline `--notes`).

## Blocker Protocol
Report blockers as: type + severity + proposed mitigation. Max 2 retries.
