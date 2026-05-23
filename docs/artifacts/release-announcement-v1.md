# Release Announcement v1

Release: [v0.1.1](https://gitlab.com/em-age/emage.code/-/releases/v0.1.1)
Date: 2026-05-23
Based on: [docs/artifacts/v3-migration-guide-v1.md](v3-migration-guide-v1.md), [docs/plans/plan-003-v3-execution-wave1.md](../plans/plan-003-v3-execution-wave1.md)

## Summary

v0.1.1 is now published and the release pipeline is green. This release finalizes v3 execution wave 1 publication flow and confirms release automation reliability after a CI compatibility fix in the `release` job.

Primary change included in release notes:
- `fix(ci): use supported git-cliff strip mode in release job`

## Migration highlights (from v3 migration guide)

- Conservative migration path remains the recommended rollout strategy:
  1. keep v2 deployment untouched,
  2. enable v3 validation and smoke checks,
  3. run trigger and adapter smoke workflows in non-production,
  4. switch pilot project to v3 outputs,
  5. promote after two consecutive green release cycles.
- Reversibility is mandatory:
  - keep a stable v2 tag reference,
  - retain v2 projection verification,
  - keep v3 experimental adapters feature-flagged,
  - maintain rollback runbook ownership.
- Security and reliability controls remain in place:
  - deny-by-default trigger policy,
  - bounded retries and audit logs,
  - adapter command allowlist and disabled-by-default flags.

## Validation and release status

- Tag pipeline for `v0.1.1`: passed.
- GitLab release object: created and published.
- Post-release validation baseline: v3 super-gate and functional suite passed.

## Next operational step

Execute pilot rollout cycle (Path A) and record rollback drill evidence before broader promotion.
