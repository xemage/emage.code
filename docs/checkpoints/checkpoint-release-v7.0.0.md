# Checkpoint — Release v7.0.0

> Filename: `checkpoint-release-v7.0.0.md`
> Written at the release phase boundary, per the user's explicit instruction ("run /prepare-release
> major now").

## Phase summary

Major release. Packages the entire `plan-035` "v7 ground-up" roadmap — Phases 0 through 6
(`T400`-`T511`, ~74 completed tasks) — since the last tagged release, `v6.10.0`. This release-prep
cycle performs only documentation and version-marker work; every task it packages was already fully
complete, independently re-verified, and merged to `develop` before this cycle began. See
`docs/releases/v7.0.0.md` for the full highlights, and `docs/checkpoints/checkpoint-016` through
`checkpoint-035` for the per-phase-boundary detail.

## Completed work (this cycle)

| ID / Commit | Type | Summary |
|--------|------|---------|
| release-prep | docs | Updated `Latest release: v6.10.0` → `v7.0.0` marker in `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md` |
| release-prep | docs | Authored `docs/releases/v7.0.0.md` (Install + Highlights per phase + Breaking changes + Internal) |
| release-prep | docs | Authored this checkpoint |
| release-prep | docs | Updated `README.md`'s per-release install-steps link from `v6.10.0.md` to `v7.0.0.md` |

Prior work being shipped in this release (already merged to `develop`, not redone here) — see
`docs/releases/v7.0.0.md`'s Internal section for the full phase-by-phase task-range and checkpoint
citation list:

| Phase | Tasks | Checkpoint |
|---|---|---|
| 0 — Ground Truth | T400-T406 | `checkpoint-016-phase0-ground-truth-complete.md` |
| 1 — Trustworthy Signal | T407-T409 + delta-harness sub-track | `checkpoint-021-phase1-complete-gate-g1-closed.md` |
| 2 — MCP Conformance | T420-T423 | `checkpoint-022-phase2-complete.md` |
| 3 — Maturity Ladder | T430-T437 | `checkpoint-032-phase3-complete.md` |
| 4/5 — Routing / Memory-RAG | T440-T443, T450-T499 | `checkpoint-033-phase4-phase5-complete-gate-g3-closed.md` |
| 6 — Closed Loop | T500-T506 | `checkpoint-034-phase6-six-task-implementation-complete.md` |
| Release readiness + closed-loop hardening | T507-T511 | `checkpoint-035-t507-t511-promotion-hardening-arc-complete.md` |

## Real, independently-verified final state (not assumed)

- `python3 docs/tasks/validate-tasks.py`: PASS (0 active, 310 completed)
- `python3 tests/run.py`: 734 tests, `OK`, `skipped=38`
- `python3 implementation/scripts/check-maturity.py --verbose`: 79 components, 0 failing
- `node implementation/scripts/sync.mjs --root implementation --check`: no drift, 577 files
- `python3 scripts/check-version-consistency.py`: run against the updated `v7.0.0` marker before
  this checkpoint was committed
- `python3 scripts/verify-release-docs.py --tag v7.0.0`: run before opening the release MR

## Open / carried over

- `plan-035` §2.7's deferred SIA/CWSO revival decision — untouched by this release, no re-entry
  condition met.
- `feature/T475-codex-platform-integration` — remains unmerged, deliberately deferred to
  post-v7.0 per `plan-054`, untouched by this release.
- Phase 6's own acceptance criteria around held-out-suite-measured improvement and a lineage
  document for a real *accepted* change remain open by design, not by omission — see
  `checkpoint-035` for the full reasoning. This release does not claim the closed loop has produced
  a trustworthy accepted improvement; it claims the loop runs for real and its human gate works.

## Release Gate Verdict

See the structured `RELEASE VERDICT` posted alongside this checkpoint's MR.

## Token metrics

Not separately tracked against a phase budget for this release-prep cycle.
