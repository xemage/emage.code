# Task T492 — Extend `test_mcp_secret_guard.py` to cover `headers` blocks

**ID:** T492
**Owner:** QA Engineer (display name used deliberately here, not the registry id — this role is
already `stable`, and this project's own established convention avoids naming an already-`stable`
component by its literal hyphenated registry id anywhere in an open task's brief, since doing so
trips `check-maturity.py`'s self-referential ledger-defect check against that component for as long
as this row stays open)
**Status:** blocked — depends on T491 landing in `develop` first (see "Why sequential" below)
**Priority:** P1
**Depends on:** T491 (must be merged to `develop` before this task branches, not merely dispatched)
**Created:** 2026-09-16
**Completed:** —
**Based on:** `docs/artifacts/mcp-header-url-templating-design-v1.md` §7 (T483, `Final` — the exact
guidance for this test extension, written precisely so this task should not need to ask follow-up
design questions); `tests/functional/test_mcp_secret_guard.py` (current file, read in full before
editing).

## Why sequential (not dispatched in parallel with T491)

T483's own brief flagged this explicitly: "the test extension may need the `headers` field to
exist in the schema/generator first to have something real to test against." While this task's
*new* adversarial fixture case can technically be authored against a synthetic dict (mirroring
`test_guard_detects_injected_literal_secret`'s existing pattern) without T491 having landed, this
task's Acceptance Criterion 1 (`test_no_literal_secrets_in_generated_mcp_output`, which scans the
*real* on-disk generated files) only exercises the new `headers`-walking code meaningfully once
T491's regenerated projections actually contain `headers` blocks somewhere on disk. Dispatching
this task from a `develop` that does not yet have T491 merged would mean this task's own
verification is partly synthetic where it doesn't need to be. Branch from `develop` only after
T491's MR has merged.

## Objective

Extend `find_literal_env_values()` (and its two `secret`-syntax tests) in
`tests/functional/test_mcp_secret_guard.py` so it also walks `headers` blocks, not only `env`
blocks — closing the real gap T483's design doc identified: a literal secret leaked into a
generated file's `headers` object today would not be caught by this guard at all.

## Inputs

- `docs/artifacts/mcp-header-url-templating-design-v1.md` §7 — the precise spec: a second `walk()`
  branch for `key == "headers"`, a new regex distinct from `ALLOWED_ENV_VALUE_RE` that accepts
  exactly one well-formed placeholder token (`\$\{env:[A-Z][A-Z0-9_]*\}` or `\{env:[A-Z][A-Z0-9_]*\}`)
  with no stray `$`/unmatched `{`/`}` in the surrounding literal text, applied uniformly regardless
  of the authoring-time `secret: true/false` flag.
- `tests/functional/test_mcp_secret_guard.py` (post-T491-merge state) — `find_literal_env_values()`
  (currently lines 40–59: a `walk()` closure with one `if key == "env"` branch at line 48),
  `ALLOWED_ENV_VALUE_RE` (line 20), `test_guard_detects_injected_literal_secret` (currently lines
  76–90), `test_guard_allows_placeholder_syntax` (currently lines 92–103). Re-confirm these line
  numbers in your own checkout after T491 merges, since T491 does not touch this file but any other
  intervening merge could shift lines.
- The real, regenerated `.mcp.json`'s `cwso.headers.Authorization` value
  (`"Bearer ${env:CWSO_BEARER_TOKEN}"`) as the ground-truth positive case to test against.

## Constraints

- Only `tests/functional/test_mcp_secret_guard.py` is in scope for edits (plus, if genuinely
  needed, `tests/fixtures/` additions — but design §7 implies inline fixtures are sufficient,
  matching the file's existing style).
- Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`.
- Do not touch `feature/T475-codex-platform-integration`.
- No new paid/metered API usage.
- Branch from `develop` (post-T491-merge): `agent/<your-role-slug>/T492`. Open an MR referencing
  T492. Do not self-merge — report completion to the orchestrator for independent verification
  first.

## Expected outputs

1. `tests/functional/test_mcp_secret_guard.py` — `find_literal_env_values()` extended to walk
   `headers` blocks with the new regex per design §7; `test_guard_allows_placeholder_syntax` and
   `test_guard_detects_injected_literal_secret` each gain a `headers`-shaped fixture case.

## Acceptance criteria

1. A genuine adversarial case: a fixture with a literal (non-placeholder) secret-shaped string
   inside a `headers` block (e.g. `"Authorization": "Bearer sk_live_FAKEVALUEFORTESTONLYNOTREAL"`)
   is asserted to be caught by `find_literal_env_values()` (i.e. produces a violation) — proving the
   guard actually now covers `headers`, not just asserting the code compiles.
2. A genuine legitimate case: the real wrapped-placeholder shape (`"Bearer ${env:SOME_VAR}"`) is
   asserted to NOT be flagged.
3. `test_no_literal_secrets_in_generated_mcp_output` still passes against the real, T491-regenerated
   on-disk files (this is the test that gives the new `headers`-walking code something real to
   check, per "Why sequential" above).
4. `python3 -m pytest tests/functional/test_mcp_secret_guard.py -v` passes in full, including both
   new cases.
5. Full `python3 -m pytest tests/functional/test_mcp_secret_guard.py tests/functional/
   test_mcp_schema_validation.py tests/functional/test_mcp_platform_conformance.py -v` passes.
6. Full `python3 tests/run.py` shows no regressions against the pre-task baseline.
7. Branch `agent/<your-role-slug>/T492` from `develop`, MR referencing T492, no self-merge.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`) per `AGENTS.md`. Max 2 retries before escalating to the
orchestrator.
