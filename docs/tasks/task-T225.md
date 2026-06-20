# Task T225 - Reward shaping: merge ±1 + `results.json` eval metric

## Objective
Combine the merge state-machine reward with the SIA task evaluation metric into a single shaped reward used
for downstream training.

## Inputs
- Reward attachment (T224)
- SIA `results.json` metric (T222)
- `docs/artifacts/reward-shaping-v1.md` (to be authored)

## Expected outputs
- A documented reward function blending merge outcome (±1) and normalized eval metric, with weights and bounds
- Implementation that emits the shaped reward per session

## Acceptance criteria
- Reward is deterministic given the same merge outcome + metric.
- Weighting and normalization are documented and configurable.
- Degenerate cases (missing metric, failed merge) have defined behavior.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
