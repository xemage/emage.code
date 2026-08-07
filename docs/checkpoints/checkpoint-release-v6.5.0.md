# Checkpoint — Release v6.5.0

> Filename: `checkpoint-release-v6.5.0.md`
> Written at the release phase boundary.

## Phase summary
Minor release. Two branches landed on `develop` since v6.4.3 and are shipping together in this
release: `feature/327-cwso-agent-knowledge-awareness` (T327–T330, MR !101) and
`bugfix/392-cwso-local-guide-script-alignment` (MR !100, no task IDs — worked directly in a
conversational session). The user explicitly chose to merge the still-open bugfix/392 MR before
cutting this release rather than defer it, and explicitly chose a MINOR bump over PATCH.

## Completed work (this cycle)
| ID / Commit | Type | Summary |
|--------|------|---------|
| T327 | feat | Authored `implementation/knowledge/skills/cwso-awareness/SKILL.md`; wired a CWSO Awareness section into `orchestrator`/`backend-developer`/`devops-engineer` agent knowledge |
| T328 | chore | `make sync` (511 files, 0 drift) + `scripts/install.sh --update` to propagate the new skill to all 6 platform projections |
| T329 | gate | Solution-architect review: role-mapping table verified byte-for-byte identical to `docs/artifacts/role-mapping-cwso-v1.md`. VERDICT: PASS |
| T330 | docs | Authored `docs/deployment/cwso-overview-and-agent-integration-guide.md` |
| `f545994` | fix | `cwso-docker-desktop.sh` no-arg setup flow + `/healthz` help text; removed stale `deploy/local-dev` references from `local-docker-desktop-guide.md` |
| (same MR) | feat | `.vscode/mcp.json` `cwso` entry, `scripts/mint-cwso-jwt.py`, `docs/deployment/cwso-emage-orchestrator-connection-guide.md`, `.gitignore` fix for `deploy/local-dev/` |
| `e3dd6c3` | fix | Regenerated `implementation/registry/{index.json,summary.md}` — CI's `test_registry_gate_passes_for_repo_artifact` failed until this ran (skill added in T327 without a registry regen) |

## Open / carried over
| ID | Title | Owner | Status | Notes |
|----|-------|-------|--------|-------|
| T316 | Tracked follow-up: role-split + minor Pattern A gaps (BUG-A/E/F/G/H, non-blocking) | backend-developer | pending | Pre-existing backlog item, unrelated to this release |

## Key decisions
- Chose MINOR (v6.4.3 → v6.5.0): user's explicit call, matching this repo's own convention
  (v6.4.0/v6.3.0 were minor bumps for new capabilities, not fixes) — the new `cwso-awareness`
  skill is a new capability.
- User explicitly chose to merge MR !100 (bugfix/392) into `develop` before cutting the release,
  rather than defer it to a later patch release.
- Tagging directly on `develop` via a `docs/release-v6.5.0` branch, per the actual practice used
  for every release since ~v6.0.3 (v6.0.7 through v6.4.3 all follow this pattern) — **not** the
  `release/vX.Y.Z → main` flow documented in `CONTRIBUTING.md`. `main` is 173 commits behind
  `develop` and last touched 2026-06-16 (reaches only v6.0.2); the documented main-merge flow has
  been out of sync with actual practice for many releases. This is a pre-existing drift, not
  something introduced by this release — flagged to the user, not silently resolved by attempting
  a 173-commit main sync as an unrequested side effect of a routine release.
- `feature/327-cwso-agent-knowledge-awareness` was originally branched from the tip of
  `bugfix/392` instead of `develop` (an earlier session error); corrected via
  `git rebase --onto develop 523c6ff` before merging so `bugfix/392`'s then-unfinished commit did
  not ship prematurely inside the T327 MR.

## Artifacts produced
- `docs/releases/v6.5.0.md` (Install + Highlights + Breaking changes + Internal)
- `docs/checkpoints/checkpoint-release-v6.5.0.md` (this file)
- Release markers updated: `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md`

## Blockers (active)
| ID | Type | Severity | Owner | Reported | Status |
|----|------|----------|-------|----------|--------|
| — | — | — | — | — | none open |

## Quality gates run this cycle
| Gate | Result |
|------|--------|
| MR !101 pipeline (feature/327 → develop) | PASS on retry — first run failed `test_registry_gate_passes_for_repo_artifact` (registry drift), fixed by regenerating the registry, re-run PASS |
| MR !100 pipeline (bugfix/392 → develop) | PASS |
| `python3 -m unittest discover -s tests -p "test_*.py"` (local, pre-merge) | PASS — 270 tests, 0 failures, 16 skipped |
| Solution-architect role-mapping fidelity gate (T329) | PASS |
| `python3 scripts/verify-release-docs.py --tag v6.5.0` | pending — run before opening the release-docs MR |

No formal Tech Lead / Security Engineer sign-off was obtained for the release-docs step itself
(no such agent was invoked this cycle) — noted as a gate gap rather than claimed as done.

## Next steps
- Phase: Release
- Tasks: open MR `docs/release-v6.5.0 → develop`, merge, tag `v6.5.0` on `develop`, push tag to
  trigger the `release` CI job (regenerates `CHANGELOG.md`, publishes the GitLab Release).
- Inputs to delegate forward: this checkpoint + `docs/releases/v6.5.0.md`.

## Compression note
This checkpoint is the canonical handoff for the release phase. Subsequent agents receive
**only**: this checkpoint + `docs/releases/v6.5.0.md`.
