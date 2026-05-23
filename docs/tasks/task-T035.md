# Task T035 — Extend release docs verification

## Objective
Extend the release documentation gate so v3-critical user and contributor docs are validated before release publication.

## Inputs
- `docs/tasks/task-T031.md`
- `.gitlab-ci.yml`
- `scripts/verify-release-docs.py`
- updated root and wiki docs

## Expected outputs
- stronger docs verification script and/or CI gate updates
- release checks that include v3 documentation alignment

## Acceptance criteria
- Tag release pipeline fails when v3-critical docs are missing or stale.
- Gate remains deterministic and produces actionable error messages.
- Existing v1/v2 release expectations continue to pass.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
