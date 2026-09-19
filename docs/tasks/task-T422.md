# Task T422 — `tests/functional/test_mcp_platform_conformance.py`

**ID:** T422
**Owner:** qa-engineer, orchestrator
**Status:** done
**Priority:** P1
**Completed:** 2026-09-08
**Depends on:** T420 (contract doc), T421 (config gap re-verified/closed)
**Created:** 2026-09-08
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 2 (T421 row; Phase 2
acceptance criteria); `docs/plans/plan-037-phase2-phase5-sequencing.md` (execution sequencing).

This brief is self-contained. **Wait for T420 and T421 to both be merged before starting** — T422
should assert the corrected/confirmed state T421 produces, not race ahead of it.

## Objective

Write `tests/functional/test_mcp_platform_conformance.py`, an automated test that mechanically
proves the platform-projection guarantee this repo already claims informally: every `core`-tagged
server in `servers.yaml` appears, correctly, in all 7 platform projections, and removing it from
any one platform's projection is caught.

## Context

This is Phase 2's acceptance-gate task — its three acceptance criteria (below) are plan-035's own
literal Phase 2 acceptance criteria, unchanged. Before writing new test code, check for duplicate
coverage: `tests/functional/test_platform_projections.py` already has
`test_platform_mcp_configs_have_expected_shape` and
`test_remote_mcp_transport_shape_for_previously_uncovered_platforms`, and
`tests/functional/test_sync_determinism.py` and `test_mcp_schema_validation.py` also exist. Read
all of these first. Your job is to close the specific gap none of them cover — a **round-trip**
test: mutate a copy of `servers.yaml` (add a server, run sync, assert presence everywhere; remove a
server's projection, assert the test fails) — not to duplicate existing static shape assertions.
Per plan-035's own re-scoping instruction for this phase, if you find the existing tests already
satisfy one of the three acceptance criteria below, say so in your report and write only what's
missing, rather than padding scope.

## Inputs

- `docs/artifacts/mcp-platform-contract-v1.md` (T420) — authoritative per-platform contract
- T421's completion report / MR — confirms current known-good state to test against
- `tests/functional/test_platform_projections.py`, `test_mcp_schema_validation.py`,
  `test_sync_determinism.py`, `test_mcp_secret_guard.py` — existing coverage; read before writing
  new tests
- `implementation/scripts/sync.mjs`, `implementation/knowledge/mcp/servers.yaml`,
  `implementation/platforms/*.json` — system under test

## Expected outputs

- `tests/functional/test_mcp_platform_conformance.py` (new file)
- Test(s) should operate against a temporary copy of the knowledge/platforms trees (via
  `sync.mjs`'s existing `--root`/`--knowledge`/`--platforms` args, the same mechanism
  `test_sync_determinism.py` likely already uses — check it first) rather than mutating the real
  `servers.yaml` in place, so the test suite never leaves the repo dirty.

## Acceptance criteria (from plan-035 §2.4 Phase 2, unchanged)

- [ ] Adding a `core` server to `servers.yaml` and running sync makes it appear in all 7 platforms
      — proven by an actual add-and-sync-and-assert round trip in the test, not a static read
- [ ] Deleting it from one platform's projection makes the test fail — proven by an actual
      delete-and-assert-failure round trip (e.g. via `pytest.raises` / equivalent around a helper
      that re-runs the shape assertion after deletion, or a subprocess-based check)
- [ ] `test_mcp_secret_guard.py` still passes after this change — run it explicitly and cite the
      result, don't assume

## Constraints

- Token budget: part of Phase 2's 100k total (plan-035 §2.8).
- File ownership: `tests/functional/test_mcp_platform_conformance.py` only. Do not modify
  `servers.yaml`, `platforms/*.json`, or `sync.mjs` — if the round-trip test reveals a genuine
  conformance bug (not the plan-037 false alarm, which T421 already resolved), report it as a
  blocker rather than fixing it yourself; that would be new scope beyond this task's file
  ownership.
- Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`.
- Do not touch branch `feature/T475-codex-platform-integration`.
- Work in your own worktree/branch (`agent/qa-engineer/T422` from `develop`, taken after T421's MR
  is merged); open an MR rather than self-merging.

## Blocker protocol

Report blockers with type and severity per `AGENTS.md`. Max 2 retries before escalating.

## Closure (2026-09-08) — closes Phase 2 in full

All three plan-035 §2.4 Phase 2 acceptance criteria independently verified met via two new live
round-trip tests. Isolation mechanism reuses `test_sync_determinism.py`'s established copy+cwd
pattern (confirmed real, not the `--root`/`--knowledge`/`--platforms` flags this brief guessed at).
Orchestrator independently re-ran everything before merging: read `test_sync_determinism.py`
directly, ran both new tests (2/2 pass), ran `test_mcp_secret_guard.py` (3/3 pass), ran the full
suite fresh (379 tests, `+2` from baseline, `OK`, `skipped=17`), confirmed `git status` clean and
the merged diff scoped to exactly the one new file. This closes Phase 2 (T420-T423) in its
entirety. Gate G2 is unaffected — see `docs/tasks/active-tasks.md`'s "Phase 2 / Gate G2 closure
status" note and `docs/tasks/completed-tasks.md`'s T422 row for the full record.
