# Task T491 — Implement `hindsight`/`cwso` MCP registration (servers.yaml + sync.mjs)

**ID:** T491
**Owner:** backend-developer
**Status:** in_progress — dispatched this session
**Priority:** P1
**Depends on:** None (T483's design is `Final` and ratified; this task implements it)
**Created:** 2026-09-16
**Completed:** —
**Based on:** `docs/artifacts/mcp-header-url-templating-design-v1.md` (T483, status `Final`,
independently spot-checked by the orchestrator this session against the real, current
`implementation/scripts/sync.mjs`, `implementation/knowledge/mcp/servers.yaml`, root `.mcp.json`,
`tests/functional/test_mcp_secret_guard.py`, `tests/fixtures/mcp-schemas/{gemini-cli-settings,
opencode-config}.schema.json`, and `implementation/platforms/{github,pi}.json` — every code
citation, line number, and rendering hand-trace in that design checked out against the real
source, including its one disclosed citation correction in §5.3). Treat the design doc as the
authoritative spec for this task; do not re-derive the schema or generator design from scratch.

## Objective

Implement T483's ratified design exactly: extend `parseServersYaml()`, add `mapTemplatedValue()`,
refactor `mapEnv()` to use it, extend all 6 `emitMcp()` format branches to emit `headers` and
template `url`, add the two new `servers.yaml` entries, and regenerate every platform projection —
bringing `hindsight` and `cwso` into this repo's declarative MCP pipeline with zero behavioral
change to any existing server.

## Inputs

- `docs/artifacts/mcp-header-url-templating-design-v1.md` — read in full; §5 has the exact code
  (parser change §5.0, `mapTemplatedValue()`/`mapEnv()` §5.1, all 6 per-format-branch diffs §5.2),
  §6 has the exact `servers.yaml` YAML for both new entries plus a full hand-traced rendering
  verification against the real target `.mcp.json`.
- `implementation/scripts/sync.mjs` — `parseServersYaml()` (lines 170–225), `parseInlineObject()`
  (227–238), `emitMcp()` (293–379), `mapEnv()` (381–388). These are the exact current line ranges;
  re-confirm against your own checkout before editing since line numbers will shift once your own
  edits land.
- `implementation/knowledge/mcp/servers.yaml` — insert the two new entries per design §6 (insertion
  point is not functionally constrained — anywhere under `servers:` is fine).
- Root `.mcp.json` (already correct, hand-added, unmodified by this task except via regeneration —
  see Constraints) — the exact byte-for-byte target for the `claude-code` format branch.
- `docs/artifacts/mcp-platform-contract-v1.md` — update in the same change: §2's "15 servers total,
  7 core + 8 extended" becomes "17 servers total, 8 core + 9 extended" (hindsight → core, cwso →
  extended); §3's per-platform table's "Servers in scope" column counts change from 15 to 17 (or
  from 7 to 8 for the `github`/`core`-only row); §3.1's wire-shape table should note that the
  remote-server shape now optionally includes `headers` where the target format supports it (see
  design §5.3's per-platform evidence table for exactly which formats).

## Constraints

- No literal secret values anywhere in `servers.yaml` or any generated file — `${env:VARNAME}` /
  `{env:VARNAME}` (or, for wrapped headers, the exact literal-plus-placeholder shape design §3
  specifies) only.
- Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`.
- Do not hand-edit `.mcp.json` (or any other generated platform file) directly — it may only change
  as `sync.mjs`'s regenerated output. Root `.mcp.json`'s `hindsight`/`cwso` content must be
  byte-identical before and after this task (see Acceptance Criteria 3) — regeneration should be a
  no-op for that file's content given the design's own hand-traced verification in §6.
- Do not touch `feature/T475-codex-platform-integration` (separate, untouched branch with its own
  independent task-ID lineage — do not read from or branch off it).
- No new paid/metered API usage.
- Branch from `develop`: `agent/backend-developer/T491`. Open an MR referencing T491. Do not
  self-merge — report completion to the orchestrator for independent verification first.

## Expected outputs

1. `implementation/scripts/sync.mjs` — parser, `mapTemplatedValue()`, `mapEnv()`, and all 6
   `emitMcp()` format branches extended per design §5.
2. `implementation/knowledge/mcp/servers.yaml` — `hindsight` and `cwso` entries per design §6.
3. All platform projection files regenerated via `node implementation/scripts/sync.mjs` (not
   `--check` — actually write). Check how many platforms currently exist in your `develop` checkout
   before assuming a count (T483's brief flagged this may be 7 or 8 depending on whether
   `feature/T475-codex-platform-integration`'s Codex work has merged — re-check directly).
4. `docs/artifacts/mcp-platform-contract-v1.md` updated per "Inputs" above.

## Acceptance criteria

1. `hindsight` and `cwso` appear in `servers.yaml` with correct tags (`hindsight`: `core`; `cwso`:
   `extended` — both per design §1/§2's decision rationale, do not re-litigate), no literal
   secrets, and a templating shape `sync.mjs` genuinely implements.
2. `node implementation/scripts/sync.mjs --check` is clean (no drift) across all platforms after
   regeneration.
3. The regenerated `.mcp.json` (claude-code) content for `hindsight`/`cwso` matches the current,
   already-merged `develop` `.mcp.json` content for those two entries byte-for-byte. Verify this
   explicitly (e.g. `git diff` scoped to `.mcp.json` should show zero change to those two keys, or
   zero change at all if no other platform reordering touches the file).
4. `hindsight`/`cwso` appear correctly in every other platform's regenerated projection, per design
   §5.3's per-platform evidence table (note the three "unverified — disclosed extension" platforms
   there — implement per the design's code regardless, the evidence-class caveat is about live
   client compatibility, not about whether this task should emit the field).
5. Existing functional test suite still passes: `python3 -m pytest tests/functional/
   test_mcp_secret_guard.py tests/functional/test_mcp_schema_validation.py tests/functional/
   test_mcp_platform_conformance.py -v` (the `test_mcp_secret_guard.py` file itself is NOT modified
   by this task — that is T492's scope, dispatched separately once this task merges — but it must
   still pass unmodified against your new output, since `hindsight`/`cwso`'s only `headers`-bearing
   value, `cwso.headers.Authorization`, is a wrapped literal ("Bearer ${env:...}"), which the
   *current*, unextended `find_literal_env_values()` does not scan at all — it only walks `env`
   keys, not `headers` — so this is expected to pass trivially today, not a false confidence signal;
   T492 is what makes the guard actually cover this new surface).
6. `docs/artifacts/mcp-platform-contract-v1.md` reflects the new 17-server registry accurately.
7. Full `python3 tests/run.py` shows no regressions against the pre-task baseline.
8. Branch `agent/backend-developer/T491` from `develop`, MR referencing T491, no self-merge.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`) per `AGENTS.md`. Max 2 retries before escalating to the
orchestrator. If the design doc's specified code, once actually applied, does not in fact produce
byte-identical `.mcp.json` output for `hindsight`/`cwso` (i.e. Acceptance Criterion 3 fails), that
is a `technical`/`major` blocker — stop and report rather than hand-patching around the design.
