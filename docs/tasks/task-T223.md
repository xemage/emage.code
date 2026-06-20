# Task T223 - Run SIA generation via harness launcher; confirm Parquet capture

## Objective
Execute one SIA generation through the CWSO harness launcher and confirm the target agent's LLM calls are
captured as trajectories in the Parquet store.

## Inputs
- SIA target adapter (T220), base_url patch (T221), SIA task (T222)
- Dev profile with rollout enabled (T203)

## Expected outputs
- A run record showing one generation executed via the launcher
- Evidence of `CompletionRecord`s (prompt/sampled token IDs, logprobs) written to the trajectory store
- `docs/artifacts/capture-poc-report-v1.md`

## Acceptance criteria
- ≥1 `CompletionRecord` for the generation is present in the Parquet store with non-empty token IDs and logprobs.
- The generation produces a `results.json` via the task's `evaluate.py`.
- Capture is attributable to the run/session.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
