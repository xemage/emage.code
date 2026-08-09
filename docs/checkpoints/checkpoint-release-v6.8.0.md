# Checkpoint — Release v6.8.0

> Filename: `checkpoint-release-v6.8.0.md`
> Written at the release phase boundary.

## Phase summary
Minor, release-only cycle. No new implementation work performed in this cycle — the six tasks this
release packages (T352–T357: the Cline platform integration, plan-028-v2) were already fully
complete and merged to `develop` prior to this release. This phase only packages and ships that
already-done work: release docs, marker updates, verification, tag, and publish. Per this
session's established pattern (T337/T342/T347/T350), landed via a branch + MR — no direct commits
to `develop`.

## Completed work (this cycle)
| ID / Commit | Type | Summary |
|--------|------|---------|
| (this cycle) | docs | Updated `Latest release: v6.7.1` → `v6.8.0` marker in `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md` |
| (this cycle) | docs | Authored `docs/releases/v6.8.0.md` (Install + Highlights + Breaking changes + Internal) |
| (this cycle) | docs | Authored this checkpoint |

Prior cycle work being shipped in this release (already merged to `develop`, not redone here):
| ID | Type | Summary |
|----|------|---------|
| T352 | feat | `implementation/platforms/cline.json` manifest (v2, reduced scope: instructions + skills only) |
| T353 | feat | `sync.mjs` engine support for Cline (MCP format branch, optional agents/commands fileMap, `rootRelative` flag) |
| T354 | feat | Generated `implementation/.cline/` + `implementation/.clinerules/` canonical output; registry drift fix; MR !141 |
| T355 | feat | Installer support (`install_cline()`, `--platform cline`, `render_installed_agents.py` fix); MR !144 |
| T356 | docs | Cline documentation (README, AGENTS.md, `docs/wiki/cline-setup.md`) |
| T357 | qa | Final e2e validation gate for plan-028-v2 — PASS, no blockers; MR !147 |

## Open / carried over
| ID | Title | Owner | Status | Notes |
|----|-------|-------|--------|-------|
| — | — | — | — | none open at time of writing |

## Key decisions
- **Version bump: MINOR (v6.7.1 → v6.8.0).** Per the user's explicit choice this session: T352–T357
  shipped a genuine new capability (Cline platform support), matching this repo's own convention
  (MINOR for new capabilities, PATCH for fixes/infra-only) — unlike v6.7.1's precedent.
- **Cline platform support classified under Highlights/Features, not Internal.** Contrast with the
  v6.7.1 precedent (no new capability, Internal-only): this release genuinely adds a new supported
  platform, so it is described in Highlights per the task brief's explicit constraint.
- **Agents/commands scope limitation stated plainly, not buried.** No confirmed on-disk format
  exists for Cline-native subagents or slash commands as of this writing; the release doc and
  `docs/wiki/cline-setup.md` both state this as an intentional, documented boundary rather than a
  defect.
- **Breaking changes: None.** Verified by confirming T352–T357 only added new files/capabilities
  and additive, opt-in-gated engine changes (`rootRelative`, optional `fileMap.agents`/`.commands`)
  that don't alter any existing platform's output — per T353's and T357's own `sync.mjs --check`
  verification (0 drift across all platforms, both before/after and on a fresh checkout).
- Tagging on `develop` via a `docs/release-v6.8.0` branch, consistent with the T337/T347/T350
  precedent. The `release/v6.8.0 → main` sync is a separate follow-up task (T359), using the
  PUT-first merge procedure from `CONTRIBUTING.md` (2/2 successful: MR !126, MR !134).
- No deprecations.

## Artifacts produced
- `docs/releases/v6.8.0.md` (Install + Highlights + Breaking changes + Internal)
- `docs/checkpoints/checkpoint-release-v6.8.0.md` (this file)
- Release markers updated: `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md`

## Blockers (active)
| ID | Type | Severity | Owner | Reported | Status |
|----|------|----------|-------|----------|--------|
| — | — | — | — | — | none open |

## Quality gates run this cycle
| Gate | Result |
|------|--------|
| `python3 scripts/verify-release-docs.py --tag v6.8.0` | see literal output recorded in `docs/tasks/task-T358.md` `## Outcome` |
| `python3 tests/run.py` | see literal output recorded in `docs/tasks/task-T358.md` `## Outcome` |
| `node implementation/scripts/sync.mjs --root implementation --check` | see literal output recorded in `docs/tasks/task-T358.md` `## Outcome` |
| `python3 implementation/scripts/generate-registry.py --root implementation --check` | see literal output recorded in `docs/tasks/task-T358.md` `## Outcome` |
| `python3 docs/tasks/validate-tasks.py` | see literal output recorded in `docs/tasks/task-T358.md` `## Outcome` |

## Next steps
- Phase: Release
- Tasks: open MR `docs/release-v6.8.0 → develop`, wait for pipeline green. The orchestrator
  reviews, merges (squash), tags `v6.8.0` on the new `develop` tip, pushes the tag to trigger the
  `release` CI job (which runs `main-develop-drift-gate`, regenerates changelog/release-notes
  artifacts, and publishes the GitLab Release from `docs/releases/v6.8.0.md`), and independently
  verifies the Release object via `glab api` — matching T347/T350's actual execution split
  (delegate prepares, orchestrator merges/tags/verifies).
- Follow-on: `release/v6.8.0 → main` sync is T359, a separate task.
- Inputs to delegate forward: this checkpoint + `docs/releases/v6.8.0.md`.

## Compression note
This checkpoint is the canonical handoff for the release phase. Subsequent agents receive
**only**: this checkpoint + `docs/releases/v6.8.0.md`.
