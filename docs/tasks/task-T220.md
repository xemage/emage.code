# Task T220 - Real harness-adapter image for SIA target agent

## Objective
Replace a stub harness adapter (`claude_code`/`qwen_code`) with a real image that runs a SIA target agent,
launched by CWSO's harness launcher with the model `base_url` pointed at the rollout proxy.

## Inputs
- `CWSO/orchestrator/internal/harness/registry.go` (adapter pattern, `LaunchEnv`, `BaseURLEnv`)
- `CWSO/orchestrator/internal/harness/launcher.go` (mount `/workspace`, `CWSO_HARNESS_PROMPT`)
- SIA runtime requirements (`sia-agent`, backend deps)
- Dev profile (T203)

## Expected outputs
- A container image that runs a SIA target agent and honors injected `OPENAI_BASE_URL`/`ANTHROPIC_BASE_URL`
- Adapter registration (new `AdapterConfig`) wiring image + command + base-url env
- `docs/artifacts/sia-target-adapter-v1.md`

## Acceptance criteria
- Launcher starts the image, mounts a workspace, and the agent's LLM calls egress through the rollout proxy.
- The agent reads the prompt from `CWSO_HARNESS_PROMPT` and writes outputs into `/workspace`.
- No provider keys baked into the image.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
