# Task T357 — End-to-End Validation for Cline Platform Support

**ID:** T357
**Owner:** qa-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T356
**Created:** 2026-08-08
**Based on:** `docs/plans/plan-028-cline-platform-integration.md`; `.gitlab-ci.yml`, `Makefile`,
`.editorconfig`

## Objective
Run the full repo verification suite with Cline included and confirm nothing outside `.cline/` and
this plan's own file inventory regressed. Produce a validation report.

## Context
- Phase: Implementation (plan-028, step 6 of 6, final gate before this work is considered ready for a
  future release).
- **`make verify` only runs `node implementation/scripts/sync.mjs --root implementation --check`**
  (confirmed by reading the `Makefile`) — it does not call `implementation/scripts/check.py`. CI's
  `validation-super-gate` job runs `check.py` separately, with a specific flag set. Run both, but
  don't conflate them as one command.
- **`.gitlab-ci.yml`'s `verify-knowledge-drift` and `sync-no-diff` jobs are generic** — they run
  `verify.mjs`/`sync.mjs` against whatever's in `implementation/platforms/`, with no per-platform
  hardcoding (confirmed by reading both job definitions). **No `.gitlab-ci.yml` edit is needed or
  expected for Cline support** — this task's CI-related criterion is to confirm the existing jobs
  pass on this branch's pipeline, not to add configuration.
- **One criterion in the original draft of this plan cannot be performed by an automated agent**: an
  interactive VS Code + Cline-extension manual check ("open the target project in VS Code, confirm
  `.cline/rules/` loads in Cline's rules panel"). That requires a human GUI session this task's
  delegate does not have. **Do not attempt it.** Report it as out of scope in the Outcome section and
  let the orchestrator flag it to the user as a manual follow-up — this is not a blocker, it's an
  explicit scope boundary.

## Inputs
- Full repo state after T352–T356 land
- `.gitlab-ci.yml`, `Makefile`, `.editorconfig`

## Constraints
- Verification only — if any check fails, report which one and the exact failure; do not attempt to
  fix code from this task (route the fix back to the owning task: T352/T353 for manifest/sync issues,
  T355 for install issues, T356 for docs issues).
- Token budget: ≤ 25k.

## Expected Outputs
A validation report (the `## Outcome` section of this brief), with exact command output quoted for
every criterion below.

## Acceptance Criteria
- [ ] `make verify` passes (i.e. `node implementation/scripts/sync.mjs --root implementation --check`
      exits 0)
- [ ] `python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks
      --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers
      --adapters` passes (the exact command CI's `validation-super-gate` job runs)
- [ ] `make sync -- --check` (or equivalently `node implementation/scripts/sync.mjs --check`, no
      `--platform` filter) passes with no drift across all 7 platforms including Cline
- [ ] `.cline/cline_mcp_settings.json` is valid JSON and contains every expected server (re-confirm;
      this was already checked in T354, re-verify it still holds after T355/T356's changes since
      neither should have touched `.cline/` but confirm rather than assume)
- [ ] `git diff --stat` against the pre-T352 baseline shows only files from plan-028 §6's file
      inventory — no unexpected files touched
- [ ] All new/modified files pass the repo's `.editorconfig` check (run whatever editorconfig-checker
      the repo's CI uses — check `.gitlab-ci.yml` for the exact job/command; if none exists, note that
      explicitly rather than inventing a command)
- [ ] Manual VS Code + Cline-extension check: **explicitly marked out of scope for this task** (see
      Context) — recorded as a follow-up for the orchestrator/user, not attempted
- [ ] Task brief updated with an `## Outcome` section summarizing all of the above, structured as a
      pass/fail table

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. Any hard failure in
`make verify`, `check.py`, or `sync.mjs --check` is a `technical` blocker of `major` severity — do not
mark this task done with a failing gate; report which task the fix routes back to.
