**Status:** done
**Completed:** 2026-05-24
# Task T040 - Implement v3 projection parity

## Objective
Upgrade v3 sync and verify behavior to support deterministic, cross-platform projection parity.

## Inputs
- v3/implementation/scripts/sync-v3.mjs
- v3/implementation/scripts/verify-v3.mjs
- parity fixes already validated in v2 sync/verify flow

## Expected outputs
- updated v3/implementation/scripts/sync-v3.mjs
- updated v3/implementation/scripts/verify-v3.mjs
- regression tests for projection portability where needed

## Acceptance criteria
- Drift checks are stable across Linux and Windows runners.
- Manifest path serialization is deterministic and POSIX-normalized.
- verify-v3 default root targets v3 implementation for native operation.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
