# Task T394 — Release v6.10.0 (MCP settings hardening + merge-safety + provenance)

**ID:** T394
**Owner:** release-manager
**Status:** done
**Priority:** P0
**Depends on:** T382 (plan-034 final proof point)
**Created:** 2026-08-10
**Completed:** 2026-08-10
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

## Execution notes

**Executed by:** orchestrator, 2026-08-10. Classification: MINOR (v6.9.0 → v6.10.0), classified
under Highlights/Fixed + Highlights/Removed + Highlights/Hardened (not Internal-only, since several
items change observable `--update` behavior for existing consumers). Breaking changes remained
"None" (verified: merge-safety change is strictly additive protection; provenance sidecars are new
files, not replacements; `--force-prune-keys` is opt-in only and never triggered by a plain
`--update`).

**Scope correction (verified against source of truth):** T360-T365 (plan-030) was excluded from
this release's notes — confirmed via `docs/releases/v6.9.0.md` and the existing `v6.9.0` tag that
it was already shipped, rather than assumed from the task brief's initial framing.

1. Branched `docs/release-v6.10.0` from `develop` (post-T382-closeout tip `f9c35c8`).
2. Wrote `docs/releases/v6.10.0.md` (Install table, Highlights/Fixed+Removed+Hardened summarizing
   T368-T393 and T382, Breaking changes: None, Internal section grouped by plan-031/032/033/034).
3. Bumped `Latest release: v6.10.0` marker in `README.md`, `docs/wiki/README.md`,
   `docs/wiki/home.md`.
4. Wrote `docs/checkpoints/checkpoint-release-v6.10.0.md`.
5. Created this task brief and `docs/tasks/task-T395.md`; added both rows to
   `docs/tasks/active-tasks.md`.
6. Full local verification bar: `python3 scripts/verify-release-docs.py --tag v6.10.0` PASS,
   `make verify` (0 drift/557 files), `generate-registry.py --check` up to date, `validate-tasks.py`
   PASS. `tests/run.py` initially caught a real pre-existing ledger-health failure
   (`test_every_active_task_has_a_plan`: T394/T395 not referenced by any plan) — fixed by adding a
   "(release, not a P034 step)" row for both to `docs/plans/plan-034-mcp-provenance-tracking.md`'s
   Task ID Index, matching the T366/T367-in-plan-030 precedent exactly. Full suite re-confirmed
   green after (320/320 OK, 17 skipped).
7. MR !176 (`docs/release-v6.10.0 → develop`) opened, CI green (5/5 jobs), diff independently
   re-verified (`git diff develop docs/release-v6.10.0 --stat` — exactly the 9 expected files)
   before merging via squash.
8. Post-merge `develop` pipeline (`a09c2425`) confirmed green before tagging.
9. `git tag -a v6.10.0 -m "Release v6.10.0"` on `develop`'s tip; `git push origin v6.10.0`.
10. Tag pipeline watched to success: `release-docs-gate`, `main-develop-drift-gate`, `release` job
    all succeeded (`https://gitlab.com/em-age/emage.code/-/pipelines/2747485125`).
11. GitLab Release independently confirmed live via API (`glab api
    projects/em-age%2Femage.code/releases/v6.10.0`): `name: v6.10.0`, `tag_name: v6.10.0`,
    `released_at: 2026-08-10T13:27:27.640Z`, notes sourced from `docs/releases/v6.10.0.md`.

**Result:** https://gitlab.com/em-age/emage.code/-/releases/v6.10.0
