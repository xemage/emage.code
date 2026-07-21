# Task T203 - CWSO dev profile with rollout enabled + `<some-model>` via vLLM/HAL

## Objective
Stand up a reproducible CWSO dev environment with the rollout proxy enabled and a local open-weight
`<some-model>` served OpenAI-compatibly (vLLM) behind cwso-hal, so capture and execution can be exercised end-to-end.

## Inputs
- `CWSO/deploy/docker-compose.yml` (+ profiles)
- Rollout env contract: `CWSO_ROLLOUT_*` (see `services/cwso-rollout/src/{config,store}.rs`)
- HAL adapter docs (`orchestrator/internal/hal`, `services/cwso-hal`)
- Chosen `<some-model>` (e.g. a Qwen2.5-Coder-class open-weight model)

## Expected outputs
- Documented dev profile bring-up (compose command + env file template, secrets via env only)
- Rollout proxy reachable; trajectory store writing Parquet (`CWSO_ROLLOUT_TRAJECTORY_STORE_ENABLED=true`)
- `<some-model>` reachable through HAL with an OpenAI-compatible endpoint

## Acceptance criteria
- `curl /healthz` passes; `:8080/mcp` authenticates.
- A hand-made provider call through the rollout proxy produces one `CompletionRecord` in the Parquet store.
- No secrets committed; all keys/secret references via env or mounted files.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
