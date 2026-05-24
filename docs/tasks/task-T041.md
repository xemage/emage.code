# Task T041 - Generate and verify v3 outputs

## Objective
Generate v3 platform outputs and validate projection integrity and super-gates.

## Inputs
- outputs from T039 and T040
- v3/implementation/scripts/sync-v3.mjs
- v3/implementation/scripts/verify-v3.mjs
- v3/implementation/scripts/check-v3.py

## Expected outputs
- generated v3 platform folders (.github, .gemini, .opencode, .cursor, .vscode)
- validation evidence from verify-v3 and check-v3

## Acceptance criteria
- verify-v3 passes against v3 root.
- check-v3 full gate passes.
- generated outputs are committed and deterministic.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
