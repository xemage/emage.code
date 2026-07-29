**Status:** done
**Completed:** 2026-06-23
# Task T221 - Patch SIA openhands backend to honor `base_url`

## Objective
Allow SIA to route LLM calls through the cwso-rollout proxy by honoring a configurable base URL in the
openhands backend (the claude backend already honors `ANTHROPIC_BASE_URL`).

## Inputs
- `sia/sia/util.py` (`run_agent_openhands`, `LLM(model=..., api_key=...)`)
- openhands `LLM` `base_url` parameter (litellm)

## Expected outputs
- Minimal patch: pass `base_url=os.getenv("LLM_BASE_URL")` (or equivalent) to `LLM(...)` when set
- Documented env contract for routing both backends to the proxy

## Acceptance criteria
- When `LLM_BASE_URL` is set, openhands LLM calls go to the proxy; unset → unchanged default behavior.
- Claude backend routing documented via `ANTHROPIC_BASE_URL`.
- Change is upstream-friendly (no behavioral change when env unset) and covered by a unit test.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
