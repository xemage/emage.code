**Status:** done
**Completed:** 2026-07-21
# Task T234 - Cost/latency telemetry per generation

## Objective
Instrument the loop to report per-generation cost and latency (tokens, proxy overhead, sandbox time) so the
economics of self-improvement are transparent and runaway generations are detectable.

## Inputs
- Capture + reward pipeline (T223–T225)
- Closed-loop eval harness (T233)
- CWSO telemetry/OpenTelemetry hooks where available

## Expected outputs
- Per-generation telemetry: prompt/sampled token counts, proxy added latency, sandbox runtime, merge ops
- A simple summary report/dashboard input

## Acceptance criteria
- Each generation emits token counts and latency breakdown.
- A convergence/stop signal can be derived (plateau or budget cap).
- Telemetry contains no provider secrets or raw prompts beyond what capture already retains.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
