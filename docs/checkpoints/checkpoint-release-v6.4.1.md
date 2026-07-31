# Checkpoint — Release v6.4.1

> Filename: `checkpoint-release-v6.4.1.md`
> Written at the release phase boundary.

## Phase summary
Patch release. Triggered by a self-install of emage.code onto its own
repository (`scripts/install.sh --target . --platform all --update`), which
surfaced two things: (1) `docs/plans/plan-014-task-ledger-hardening.md` had
been fully executed (T242–T284, shipped as part of v6.3.0) but its own
Status/Approval header was never updated — closed as paperwork, with gate
evidence re-verified rather than assumed; (2) a real, previously-unknown gap
in `scripts/merge-task-docs.py`, which only ever globbed `docs/tasks/*.md`
during `--update` and so never backfilled non-`.md` support files (concretely,
`validate-tasks.py`) into a target whose `docs/tasks/` predates that file —
this repo's own root `docs/tasks/` being the reproducing case, since it has
never been through a *fresh* install. Fixed and proven against this repo's
own ledger. No task briefs were opened for this work — it was done directly
in a conversational session rather than through the orchestrator delegation
protocol, so the changelog below is commit-based rather than task-ID-linked.

## Completed work (this cycle)
| Commit | Type | Summary |
|--------|------|---------|
| `5d28fc2` | chore | Install Claude Code platform (`.claude/`, `.mcp.json`, `CLAUDE.md`) and sync all six platform projections from `implementation/knowledge/` |
| `705ab69` | docs | Approve plan-014; record re-verified gate status (264 tests, `make verify`, registry check, fresh-install + `--update` round trip) |
| `28c1fea` | fix | Generalize `merge-task-docs.py` to seed any missing non-`.md` template-dir file during `--update`, not just `*.md`; seed `validate-tasks.py`/`_template.md` into this repo's own `docs/tasks/` |

No new task briefs were created; T242–T284 (plan-014's execution) were
already archived in `docs/tasks/completed-tasks.md` prior to this cycle,
dated 2026-07-29, before the v6.4.0 tag.

## Open / carried over
| ID | Title | Owner | Status | Notes |
|----|-------|-------|--------|-------|
| T214 | Pattern A Integration Test (3 Agents, Deterministic Merge) | qa-engineer | pending | Pre-existing backlog item, unrelated to this release; confirmed still-live by user during plan-014's T268 |

## Key decisions
- Chose PATCH (v6.4.0 → v6.4.1): only a bug fix plus internal/docs commits
  landed since the last tag; no new features, no breaking changes.
- `.claude/settings.json` / `.claude/settings.local.json` deliberately left
  uncommitted — local session/runtime permission state, not project content.
- Did not fabricate task IDs retroactively for this cycle's work; the gap
  between "release process assumes task-ID-linked changelog entries" and
  "this work had no task IDs" is noted here rather than papered over.

## Artifacts produced
- `docs/releases/v6.4.1.md` (Install + Highlights + Breaking changes + Internal)
- `docs/checkpoints/checkpoint-release-v6.4.1.md` (this file)
- Release markers updated: `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md`
- `docs/plans/plan-014-task-ledger-hardening.md` (approval + gate evidence, prior commit)

## Blockers (active)
| ID | Type | Severity | Owner | Reported | Status |
|----|------|----------|-------|----------|--------|
| — | — | — | — | — | none open |

## Quality gates run this cycle
| Gate | Result |
|------|--------|
| `make verify` (projection drift) | PASS — 0 drift across 505 files |
| `python3 implementation/scripts/check.py --registry` | PASS — 158 checks, 0 errors |
| `python3 tests/run.py -v` | PASS — 266 tests, 0 failures, 13 skipped |
| `python3 scripts/verify-release-docs.py --tag v6.4.1` | PASS |
| Fresh install + `--update` round trip (disposable target) | PASS — `validate-tasks.py` present and exits 0 after both steps |
| Secret scan (`.mcp.json`, `CLAUDE.md`) before commit | PASS — no matches |

No formal Tech Lead / Security Engineer sign-off was obtained (no such agent
was invoked this cycle) — noted as a gate gap rather than claimed as done. See
RELEASE VERDICT for how this factors into the release status.

## Next steps
- Phase: Release
- Tasks: open MR `release/v6.4.1 → main`, merge, tag `v6.4.1`, push tag, then
  back-merge `main → develop`. None of these have been done yet — all require
  explicit user confirmation before proceeding (push/tag/merge to `main` are
  hard-to-reverse, shared-visibility actions).
- Inputs to delegate forward: this checkpoint + `docs/releases/v6.4.1.md`.

## Compression note
This checkpoint is the canonical handoff for the release phase. Subsequent
agents receive **only**: this checkpoint + `docs/releases/v6.4.1.md`.
