**Status:** done
**Completed:** 2026-06-23
# Task T232 - sia-harness release gate + Ed25519 witness signing

## Objective
Wrap the curate→train→eval→deploy steps with sia-harness release gates and Ed25519 witness provenance so
model promotions are governed and signed.

## Inputs
- sia-harness primitives: `releaseGates`, `witness`, `memory` (`sia-harness/package.json`, `src/agents/*`)
- Training dataset + model artifacts (T230, T231)

## Expected outputs
- A gated pipeline: dataset + model pass an evaluator gate before deploy; promotion produces a signed `witness.json`
- Documented gate criteria and signing workflow (`verify-witness` / `publish-harness`)

## Acceptance criteria
- A model cannot be promoted without passing the release gate.
- Promotion emits a signed (non-null signature) witness manifest tied to the dataset + model versions.
- Gate failure blocks deploy and is reported with reasons.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
