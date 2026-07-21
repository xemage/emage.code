# Task T224 - Attach reward via `rollout_session_id` through merge

## Objective
Connect the merge outcome to a reward by passing `rollout_session_id` to `merge_concurrent_results`, so the
captured trajectory for a generation carries a programmatic reward.

## Inputs
- Concurrent-merge orchestration (T212)
- Capture PoC (T223)
- `merge_concurrent_results` schema field `rollout_session_id` (T136 reward hook)

## Expected outputs
- Orchestration passes a stable `rollout_session_id` linking a generation's trajectory to its merge result
- Verification that a reward record (±1 / GRPO) is associated with the session

## Acceptance criteria
- A successful merge attaches a positive reward to the session; a failed/conflicting merge attaches the negative signal.
- The reward is queryable/associated with the captured trajectory.
- Session IDs are unique per generation and logged.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
