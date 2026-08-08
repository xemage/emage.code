# Checkpoint — Release v6.7.0

> Filename: `checkpoint-release-v6.7.0.md`
> Written at the release phase boundary.

## Phase summary
Minor, release-only cycle. No new implementation work performed in this cycle — the feature and
fix work (T340–T346: the merge-API phantom-ancestry investigation and its remediation, the
protected-branch commit rule, and the T316 Pattern A bugfix wave) was already fully complete,
tested, and merged to `develop` prior to this release. This phase only packages and ships that
already-done work: release docs, marker updates, verification, tag, and publish. Per this session's
established pattern (T337/T342), landed via a branch + MR — no direct commits to `develop`.

## Completed work (this cycle)
| ID / Commit | Type | Summary |
|--------|------|---------|
| (this cycle) | docs | Updated `Latest release: v6.6.0` → `v6.7.0` marker in `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md` |
| (this cycle) | docs | Authored `docs/releases/v6.7.0.md` (Install + Highlights + Breaking changes + Internal) |
| (this cycle) | docs | Authored this checkpoint |

Prior cycle work being shipped in this release (already merged to `develop`, not redone here):
| ID | Type | Summary |
|----|------|---------|
| T340 | investigation | Phantom-ancestry root cause confirmed (GitLab's own `squash_commit_sha` despite `squash: false` override); no code artifact; recommended T341 |
| T341 | feat | `scripts/verify-main-sync-merge.py` + CONTRIBUTING.md "Post-merge squash verification" subsection |
| T342 | docs/process | "Protected Branches — No Direct Commits, Ever" rule codified in canonical git-workflow knowledge, propagated to 12 platform projections |
| T343 | fix | BUG-H: relative import in `ast_conflict_check.py`, eliminating dual-class-identity hazard |
| T344 | fix / breaking | BUG-A + BUG-F: `ConcurrentMergeOrchestrator` role-split (`(client)` → `(worker_client, orchestrator_client)`) + same-path collision guard |
| T345 | fix | BUG-E: best-effort `blob_oid` regex extraction in `write_shadow_file` |
| T346 | gate | End-to-end verification of T343/T344/T345 combined on `develop`'s post-merge tip; VERDICT PASS; BUG-G disposition recorded (deferred) |

## Open / carried over
| ID | Title | Owner | Status | Notes |
|----|-------|-------|--------|-------|
| — | — | — | — | none open at time of writing |

## Key decisions
- **Version bump: MINOR (v6.6.0 → v6.7.0).** Per the user's explicit choice this session: T341
  shipped a genuine new capability (`scripts/verify-main-sync-merge.py`), not just fixes, matching
  this repo's established convention (MINOR for new capabilities, PATCH for fixes-only) — the same
  convention applied for v6.6.0 (drift-detection script) and v6.4.0/v6.3.0.
- **Breaking change documented, not hidden.** T344's `ConcurrentMergeOrchestrator.__init__` change
  is a real breaking API change to `implementation/runtime/cwso/concurrent_merge.py`. It is called
  out explicitly in `docs/releases/v6.7.0.md` under "Breaking changes" (not folded into
  Highlights/Fixed) per the task brief's constraint: what changed, why (live server's permission
  model requires role-scoped clients), and that no external caller is known to be affected (full
  repo `grep` during T344/T346 found none outside this repo's own tests).
- **T340 and T346 classified as Internal, not Highlights.** Per the task brief's explicit
  constraint: T340 is an investigation with no code artifact, T346 is a verification gate with no
  code artifact. T342 is also Internal (process/docs, not a shippable code capability).
- Tagging on `develop` via a `docs/release-v6.7.0` branch, consistent with the T337/T331 precedent.
  `main` sync to this tip is explicitly out of scope for this task (would be a separate follow-up,
  the same way T339 followed T337/T338).
- No deprecations.

## Artifacts produced
- `docs/releases/v6.7.0.md` (Install + Highlights + Breaking changes + Internal)
- `docs/checkpoints/checkpoint-release-v6.7.0.md` (this file)
- Release markers updated: `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md`

## Blockers (active)
| ID | Type | Severity | Owner | Reported | Status |
|----|------|----------|-------|----------|--------|
| — | — | — | — | — | none open |

## Quality gates run this cycle
| Gate | Result |
|------|--------|
| `python3 scripts/verify-release-docs.py --tag v6.7.0` | see literal output recorded in `docs/tasks/task-T347.md` `## Outcome` |
| `python3 tests/run.py` | see literal output recorded in `docs/tasks/task-T347.md` `## Outcome` |
| `node implementation/scripts/sync.mjs --check` | see literal output recorded in `docs/tasks/task-T347.md` `## Outcome` |
| `python3 implementation/scripts/generate-registry.py --check` | see literal output recorded in `docs/tasks/task-T347.md` `## Outcome` |
| `python3 docs/tasks/validate-tasks.py` | see literal output recorded in `docs/tasks/task-T347.md` `## Outcome` |

## Next steps
- Phase: Release
- Tasks: open MR `docs/release-v6.7.0 → develop`, wait for pipeline green. The orchestrator reviews,
  merges (squash), tags `v6.7.0` on the new `develop` tip, pushes the tag to trigger the `release`
  CI job (which runs `main-develop-drift-gate`, regenerates changelog/release-notes artifacts, and
  publishes the GitLab Release from `docs/releases/v6.7.0.md`), and independently verifies the
  Release object via `glab api` — matching T337's actual execution split (delegate prepares, orchestrator
  merges/tags/verifies).
- Follow-on: `release/v6.7.0 → main` sync is explicitly out of scope for this task; to be scheduled
  separately if warranted, the same way T339 followed T337/T338.
- Inputs to delegate forward: this checkpoint + `docs/releases/v6.7.0.md`.

## Compression note
This checkpoint is the canonical handoff for the release phase. Subsequent agents receive
**only**: this checkpoint + `docs/releases/v6.7.0.md`.
