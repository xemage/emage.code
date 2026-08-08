# Task T337 — Release v6.6.0: docs prep, tag, publish

**ID:** T337
**Owner:** release-manager
**Status:** done
**Completed:** 2026-08-07
**Priority:** P1
**Depends on:** — (follows T336, plan-019 GATE)
**Created:** 2026-08-07
**Based on:** `docs/plans/plan-019-main-develop-drift-detection.md`, `docs/tasks/task-T336.md`,
`docs/checkpoints/checkpoint-release-v6.5.0.md`

## Objective
Cut release v6.6.0 from `develop`'s tip, packaging the plan-019 drift-detection capability
(T332-T336, already merged and gated on `develop`) into a versioned, published GitLab Release.
MINOR version bump (v6.5.0 → v6.6.0), matching this repo's own precedent (`docs/releases/v6.4.0.md`,
`docs/releases/v6.3.0.md`: MINOR for new tooling/capabilities shipped into the repo, not just fixes).

## Context
Delegated by the orchestrator via a structured brief (Agent tool), following the twice-proven
release process from this session (v6.5.0/T331 precedent): branch `docs/release-v6.6.0` from
`develop`, update release markers, write `docs/releases/v6.6.0.md` and
`docs/checkpoints/checkpoint-release-v6.6.0.md`, run the full verification bar, merge to `develop`,
tag, watch the tag-triggered pipeline, verify the GitLab Release publishes.

## Acceptance Criteria
- [x] `docs/release-v6.6.0` branched from `origin/develop`, markers bumped in `README.md`,
      `docs/wiki/README.md`, `docs/wiki/home.md`
- [x] `docs/releases/v6.6.0.md` and `docs/checkpoints/checkpoint-release-v6.6.0.md` authored
- [x] `python3 scripts/verify-release-docs.py --tag v6.6.0` PASS
- [x] Full verification bar green: `unittest discover` and `tests/run.py` agree (286 tests, OK,
      skipped=17); `generate-registry.py --check` up to date; `sync.mjs --check` 0 drift (511
      files); `validate-tasks.py` PASS
- [x] MR !107 (`docs/release-v6.6.0 → develop`) merged (squash), merge commit `82f98abbe7119fd354d521aa95ff6409bb713305`
- [x] Tag `v6.6.0` created and pushed

## Outcome (2026-08-07)
Docs prep and MR merge completed cleanly. The first tag-push pipeline (`2740097012`) FAILED at the
new `main-develop-drift-gate` job — a pre-existing CI infrastructure bug (see T338), not real
main/develop drift. After T338's fix landed on `develop`, the `v6.6.0` tag was deleted and
recreated on the fixed commit (`b866a778ba1870f2923b17e3cf37c2e69822cde9`) — performed directly by
the user/main session, since deleting a pushed tag was blocked by the Claude Code auto-mode
permission classifier when attempted by this orchestrator (destructive-git-operation guard;
correctly required live, direct authorization rather than a relayed conversational approval).
Re-run pipeline `2740157827`: all 3 jobs succeeded, `main-develop-drift-gate` produced a real
verdict (`drift-check: main=v6.5.0 develop=v6.6.0 releases_behind=1` → `PASS`), and the GitLab
Release published (`released_at: 2026-08-07T10:01:20.426Z`). Independently re-verified by the
orchestrator via `glab api` and pipeline job traces, not taken on report alone.

Release URL: <https://gitlab.com/em-age/emage.code/-/releases/v6.6.0>
