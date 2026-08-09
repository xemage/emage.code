# Task T357 v2 — End-to-End Validation for Cline Platform Support (corrected format)

**ID:** T357
**Owner:** qa-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T356
**Created:** 2026-08-08 (revised 2026-08-09 for corrected Cline format)
**Based on:** `docs/plans/plan-028-cline-platform-integration-v2.md`; `.gitlab-ci.yml`, `Makefile`,
`.editorconfig`

## Objective
Run the full repo verification suite with Cline included and confirm nothing outside
`.clinerules/`, `.cline/`, and this plan's own file inventory regressed. Produce a validation report.

## Context
- Phase: Implementation (plan-028-v2, step 6 of 6, final gate).
- Same tooling notes as v1's brief: `make verify` only runs `sync.mjs --check`, not `check.py`
  (run both, separately); `.gitlab-ci.yml`'s `verify-knowledge-drift`/`sync-no-diff` jobs are generic
  and need no edits.
- **Manual VS Code + Cline-extension check is still out of scope** for this task (no GUI access) —
  and its scope is narrower than v1 anyway, since there's no subagent-selection UI to check anymore
  (agents aren't projected). If performed manually later by a human, it would only be: confirm
  `.clinerules/*.md` shows up in Cline's rules UI, and `.cline/skills/` skills are usable. Report this
  as a follow-up for the orchestrator/user, not attempted here.

## Inputs
- Full repo state after T352-T356 (v2) land
- `.gitlab-ci.yml`, `Makefile`, `.editorconfig`

## Constraints
- Verification only. Route failures back to the owning task (T352/T353 manifest/engine, T355 install,
  T356 docs).
- Token budget: ≤ 20k.

## Expected Outputs
A validation report (`## Outcome`), exact command output quoted for every criterion.

## Acceptance Criteria
- [ ] `make verify` passes (`node implementation/scripts/sync.mjs --root implementation --check`
      exits 0)
- [ ] `python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks
      --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers
      --adapters` passes
- [ ] `node implementation/scripts/sync.mjs --root implementation --check` (all platforms, no filter)
      passes with no drift across all 7 platforms including Cline
- [ ] `implementation/.cline/mcp.json` is valid JSON and contains every expected `core`/`extended`
      server (re-confirm after T355/T356's changes — neither should have touched
      `implementation/.cline/`/`implementation/.clinerules/`, but verify rather than assume)
- [ ] `implementation/.clinerules/` still exists (canonical generated location, committed by T354),
      unaffected by T355/T356's changes
- [ ] `git diff --stat` against the pre-T352 (v2) baseline shows only files from plan-028-v2 §6's file
      inventory (which includes `implementation/.cline/` and `implementation/.clinerules/`, committed
      by T354) — no unexpected files touched, and specifically **no**
      `implementation/.cline/rules/`, `implementation/.cline/agents/`,
      `implementation/.cline/commands/`, or bare repo-root `.clinerules` (v1 leftovers must not
      exist)
- [ ] All new/modified files pass the repo's `.editorconfig` check (check `.gitlab-ci.yml` for the
      exact command; if none exists, state that explicitly)
- [ ] Manual VS Code + Cline-extension check: **explicitly out of scope** (see Context), recorded as
      an orchestrator/user follow-up
- [ ] Task brief updated with an `## Outcome` section, structured as a pass/fail table

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. Any hard failure in
`make verify`, `check.py`, or `sync.mjs --check` is a `technical` blocker of `major` severity.
