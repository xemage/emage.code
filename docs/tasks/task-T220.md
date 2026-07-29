**Status:** done
**Completed:** 2026-06-23
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

## Additional brief content


## Status
Tech-lead code review: **CONDITIONAL_PASS**. Three security/reproducibility conditions must be resolved before merge.

## Conditions

### M1: Output Credential Sanitization (Security)

**Issue**: output.json error field could leak API keys if SIA agent error includes credentials.

**Fix**:
- Add `sanitize_credentials(data)` function to harness-entrypoint.py
- Use regex to scrub patterns: `sk-ant-[a-zA-Z0-9]+`, `sk-[a-zA-Z0-9]+`, `AIza[a-zA-Z0-9_-]+`
- Call before writing output.json
- Update sia-target-adapter-v1.md: add "Output Credential Sanitization" section

**Effort**: 30 min

### M2: Dockerfile Dependency Pinning (Reproducibility)

**Issue**: No pinned versions for SIA/backends; non-reproducible builds.

**Fix**:
- Create requirements.txt with pinned versions (sia-agent==0.2.1, etc.)
- Update Dockerfile build arg to use git ref (refs/tags/v0.2.1) instead of generic URL
- Update sia-target-adapter-v1.md: add "Dependency Pinning" section

**Effort**: 30 min

### M3: Docker Security Flags (Isolation)

**Issue**: Design claims isolation but doesn't specify docker run flags (--read-only, --tmpfs).

**Fix**:
- Update sia-target-adapter-v1.md: add "Docker Security Model and Launcher Flags" section
- Document required flags: --read-only, --tmpfs /tmp, --tmpfs /run, -v workspace
- Update registry.go with comment explaining flag requirements
- Update Dockerfile: ensure /workspace exists, add comments

**Effort**: 20 min

## Next Steps
1. Address all three conditions in feature/t220-sia-harness-adapter branch
2. Smoke test locally: `docker run --rm --read-only --tmpfs /tmp -v /workspace:/workspace -e CWSO_HARNESS_PROMPT=test emage/cwso-sia-target`
3. Verify output.json has no credential patterns
4. Push updates to origin
5. Request tech-lead re-review (quick pass expected)

**Total Effort**: ~1.5 hours

**Merge Blocker**: No; T221 can proceed independently and merge while T220 fixes are being applied.
