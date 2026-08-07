# Checkpoint — Release v6.6.0

> Filename: `checkpoint-release-v6.6.0.md`
> Written at the release phase boundary.

## Phase summary
Minor, release-only cycle. No new implementation work performed in this cycle — the feature work
(plan-019, T332–T336: `scripts/check-main-develop-drift.py` + regression tests + two new
`.gitlab-ci.yml` jobs + `CONTRIBUTING.md` "### Drift detection" subsection) was already fully
complete, tested, and merged to `develop` prior to this release. This phase only packages and
ships that already-done work: release docs, marker updates, verification, tag, and publish.
`main` and `develop` are currently content-identical (both v6.5.0 at the point this release cycle
started), per the T331 GitFlow drift remediation (MR !103, merged 2026-08-07). Phase B (release
branch → `main` sync) is a separate, later call and is out of scope for this checkpoint.

## Completed work (this cycle)
| ID / Commit | Type | Summary |
|--------|------|---------|
| (this cycle) | docs | Updated `Latest release: v6.5.0` → `v6.6.0` marker in `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md` |
| (this cycle) | docs | Authored `docs/releases/v6.6.0.md` (Install + Highlights + Breaking changes + Internal) |
| (this cycle) | docs | Authored this checkpoint |

Prior cycle work being shipped in this release (already merged to `develop`, not redone here):
| ID | Type | Summary |
|----|------|---------|
| T332 | feat | `scripts/check-main-develop-drift.py` — README marker + tag-index drift check, 1-release grace window |
| T333 | test | Regression tests for the script's pure functions — 16 tests (brief text said "14", code block defines 16; documented discrepancy) |
| T334 | ci | Wired `main-develop-drift-check` (verify, non-blocking) + `main-develop-drift-gate` (release, blocking) into `.gitlab-ci.yml`; `release:` `needs:` extended |
| T335 | docs | `CONTRIBUTING.md` "### Drift detection" subsection |
| T336 | gate | End-to-end verification, VERDICT PASS on all 5 criteria |
| T331 | fix | GitFlow drift remediation between `main`/`develop` (MR !103) — the incident that motivated plan-019 |

## Open / carried over
| ID | Title | Owner | Status | Notes |
|----|-------|-------|--------|-------|
| T316 | Tracked follow-up: role-split + minor Pattern A gaps (BUG-A/E/F/G/H, non-blocking) | backend-developer | pending | Pre-existing backlog item, unrelated to this release |

## Key decisions
- **Version bump: MINOR (v6.5.0 → v6.6.0).** `develop` carries a genuinely new, tested, documented
  capability since v6.5.0 — the main/develop drift-detection CI mechanism (plan-019/T332–T336):
  a new script, new regression tests, two new `.gitlab-ci.yml` jobs, and new `CONTRIBUTING.md`
  documentation. This matches this repo's own established convention that new capabilities (not
  fixes) bump MINOR, the same shape already set by `docs/releases/v6.4.0.md` ("Two new sync-engine
  capabilities", "New platform manifest and projection") and `docs/releases/v6.3.0.md` ("Shipped
  ledger validator", a new script + command), both MINOR bumps for new tooling of the same kind as
  this release's drift-detection script. Not a PATCH (this is materially more than a bug fix) and
  not a MAJOR (fully backward compatible, no breaking changes, purely additive CI/tooling).
- This release completes the T331-recommended prevention mechanism: T331's remediation task brief
  identified the need for an automated main/develop drift check to prevent recurrence of the
  GitFlow divergence it had to fix by hand; plan-019 was scoped and executed as that mechanism, and
  it is shipping in this same release (v6.6.0) rather than a later one — there is no gap between
  the incident and the fix landing in a release.
- Tagging on `develop` via a `docs/release-v6.6.0` branch, consistent with actual practice for
  every release since ~v6.0.7 (documented in the v6.5.0 checkpoint). `main` sync to this tip is
  Phase B of the parent plan (plan-020), a separate, later call — not performed as part of this
  checkpoint.
- No breaking changes; no deprecations.

## Artifacts produced
- `docs/releases/v6.6.0.md` (Install + Highlights + Breaking changes + Internal)
- `docs/checkpoints/checkpoint-release-v6.6.0.md` (this file)
- Release markers updated: `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md`

## Blockers (active)
| ID | Type | Severity | Owner | Reported | Status |
|----|------|----------|-------|----------|--------|
| — | — | — | — | — | none open |

## Quality gates run this cycle
| Gate | Result |
|------|--------|
| `python3 scripts/verify-release-docs.py --tag v6.6.0` | see literal output recorded in the release-manager's completion report for this cycle |
| `python3 -m unittest discover -s tests -p "test_*.py"` | see literal output recorded in the release-manager's completion report for this cycle |
| `python3 tests/run.py` | see literal output recorded in the release-manager's completion report for this cycle |
| `python3 implementation/scripts/generate-registry.py --check` | see literal output recorded in the release-manager's completion report for this cycle |
| `node implementation/scripts/sync.mjs --check` | see literal output recorded in the release-manager's completion report for this cycle |
| `python3 docs/tasks/validate-tasks.py` | see literal output recorded in the release-manager's completion report for this cycle |

## Next steps
- Phase: Release
- Tasks: open MR `docs/release-v6.6.0 → develop`, wait for pipeline green, merge (squash), tag
  `v6.6.0` on the new `develop` tip, push tag to trigger the `release` CI job (which now also runs
  the new `main-develop-drift-gate` before `release`, regenerates `CHANGELOG.md`/`release-notes.md`
  as job artifacts, and publishes the GitLab Release from `docs/releases/v6.6.0.md`).
- Follow-on: Phase B (plan-020) — `release/v6.6.0 → main` sync, out of scope for this checkpoint.
- Inputs to delegate forward: this checkpoint + `docs/releases/v6.6.0.md`.

## Compression note
This checkpoint is the canonical handoff for the release phase. Subsequent agents receive
**only**: this checkpoint + `docs/releases/v6.6.0.md`.
