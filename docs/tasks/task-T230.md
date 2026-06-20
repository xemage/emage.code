# Task T230 - Trainer bridge: Parquet trajectories → GRPO/SFT dataset

## Objective
Build the bridge that reads captured trajectories from the Parquet store and produces a training dataset
(GRPO and/or SFT) for fine-tuning `<some-model>`, reusing CWSO's offline SFT mode where possible.

## Inputs
- Parquet store schema: `CompletionRecord` (prompt/sampled token IDs, logprobs, finish_reason, timestamp)
- Shaped reward (T225)
- CWSO offline SFT generation mode (T151) and trajectory builder (T149/T133)

## Expected outputs
- Dataset builder: trajectories + per-session reward → GRPO tuples / SFT pairs in a documented format
- `docs/artifacts/trainer-bridge-v1.md`

## Acceptance criteria
- Builder consumes the Parquet store and emits a training dataset with rewards aligned to sessions.
- Loss-mask / prompt-completion boundaries are correct for the chosen training mode.
- Reproducible (fixed seed/manifest); dataset is witness-trackable for T232.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
