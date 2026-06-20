# Task T214 - Pattern A integration test (3 agents, deterministic merge)

## Objective
Validate Pattern A end-to-end: three agents concurrently edit a small Go/Python repo and the results merge
deterministically with zero manual conflict resolution.

## Inputs
- Orchestration module (T212) + pre-check (T213)
- A fixture repo with Go and Python files

## Expected outputs
- Integration test exercising 3 concurrent shadow workspaces → semantic merge → committed result
- Test report artifact with timings, OIDs, and conflict outcomes

## Acceptance criteria
- Three independent edits merge with no manual intervention; result compiles/parses.
- Re-running the test yields identical merge output (determinism).
- A deliberately conflicting edit is detected and reported (negative case).
- Test runs in CI against the dev profile.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
