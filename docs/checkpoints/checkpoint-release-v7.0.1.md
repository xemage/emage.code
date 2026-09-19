# Checkpoint — Release v7.0.1

> Filename: `checkpoint-release-v7.0.1.md`
> Written at the release phase boundary, per the user's explicit instruction ("Run /prepare-release
> to bring to a Release").

## Phase summary

Patch release. Packages two real pieces of work since `v7.0.0`, both done directly by the top-level
session in response to explicit user requests, neither part of the `plan-035` roadmap arc: a root
self-install harness refresh (T512), and the root-cause investigation and fix for a real,
user-reported MCP-server connectivity bug (T513). No new features, no breaking changes. See
`docs/releases/v7.0.1.md` for the full highlights.

## Completed tasks (this phase)

| ID | Title | Owner | Outcome |
|----|-------|-------|---------|
| T512 | Root self-install harness refresh to v7.0.0 | top-level session | Done — 409 files refreshed across all 7 platform mirrors; two real corrections made to the raw update output (restored `.claude/settings.json`, fixed a false ledger-scaffold claim) before committing |
| T513 | Fix `context-retriever`/`security-audit` MCP servers never working outside this repo | top-level session | Done — three compounding root causes found and fixed (missing pip dependency, missing runtime source distribution, missing per-project index), plus a real `set -e` bug in the fix itself caught by CI and fixed; both this repo and the user's real CWSO project independently confirmed working |

## Open / carried over

| ID | Title | Owner | Status | Notes |
|----|-------|-------|--------|-------|
| — | `servers.yaml` hardcodes `context-retriever`'s index directory name (`em-age-emage.code`) for every target project | — | Not scoped | Found during T513, deliberately not fixed — does not break connectivity, but is semantically wrong for any project other than this one. Left for the user's own future decision. |
| — | `promotion.py`'s `floor_met()`-adjacent hardening follow-up | — | Not scoped | Carried over from `checkpoint-035` — Options A/B/C from `T509`'s design are all now built (`T510`/`T511`); nothing further scoped or requested. |
| — | `plan-035` §2.7 deferred SIA/CWSO revival decision | — | Untouched | Carried over from every prior checkpoint since `checkpoint-034`; no re-entry condition met. |
| — | `feature/T475-codex-platform-integration` | — | Untouched, further behind | Deliberately deferred per `plan-054`; backed up to `origin` this session (a plain push, no content change) but not revived. |

## Key decisions

None this cycle — both T512 and T513 were direct bug-fix/housekeeping work with no open design
question requiring a recorded decision.

## Maturity distribution

Regenerated fresh via `python3 implementation/scripts/generate-registry.py --root implementation`
before this checkpoint was written; `implementation/registry/summary.md` confirmed unchanged
(already current — only a cosmetic `generatedAt` timestamp differed, not committed).

| Category | Stable | Experimental | Deprecated | Total |
|----------|-------:|-------------:|-----------:|------:|
| Agents | 20 | 8 | 0 | 28 |
| Commands | 0 | 19 | 0 | 19 |
| Instructions | 4 | 2 | 0 | 6 |
| Skills | 7 | 19 | 0 | 26 |
| **Total** | **31** | **48** | **0** | **79** |

Unchanged from `v7.0.0`'s own distribution — this release added no new registry components beyond
what `T512` already brought into the root self-install (which mirrors `implementation/`'s existing
registry, not a new registration).

## Artifacts produced

- `docs/releases/v7.0.1.md`
- `docs/tasks/task-T512.md`, `docs/tasks/task-T513.md` (authored retroactively at closure, matching
  this project's own established precedent for direct top-level-session work)
- This checkpoint

## Blockers (active)

None.

## Token usage

Not separately tracked against a phase budget for this release-prep cycle.

## Next steps

- Tag `v7.0.1` from `main` per `CONTRIBUTING.md`'s documented release procedure, pending the user's
  explicit go-ahead for the `main` merge — the same discipline applied to `v7.0.0`'s own release.
- `servers.yaml`'s hardcoded index-directory-name gap (above) remains available as a future,
  separately-scoped task if the user wants it addressed.

## Compression note

This checkpoint is the canonical handoff for whatever comes next. A future session should receive
this checkpoint, `docs/releases/v7.0.1.md`, and `docs/tasks/completed-tasks.md`'s T512/T513 rows —
not the full conversation history behind them.
