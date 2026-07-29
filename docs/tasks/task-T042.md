**Status:** done
**Completed:** 2026-05-24
# Task T042 - Add v3 CI gates and release wiring

## Objective
Wire v3 projection and validation gates into CI and ensure release flow includes v3 readiness checks.

## Inputs
- .gitlab-ci.yml
- outputs from T041
- v3 validation commands from v3/implementation/README.md

## Expected outputs
- updated .gitlab-ci.yml with v3 verify and super-gate jobs

## Acceptance criteria
- v3 gate jobs run on merge requests and branches.
- CI fails on v3 drift or super-gate failures.
- Existing v2 release flow remains functional.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
