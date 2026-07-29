**Status:** done
**Completed:** 2026-06-23
# Task T228 - Phase 2 live integration testing: SIA harness → reward → trajectory storage

## Objective
Validate the complete Phase 2 workflow end-to-end: SIA generation via the harness launcher (T223) → evaluation → reward attachment (T224) → reward shaping (T225) → trajectory storage in Parquet. Verify that the reward signal chain is working correctly and live trajectories are captured with proper metadata.

## Inputs
- T223 ✅: SIA harness launcher (dispatcher, execution, Parquet capture)
- T224 ✅: Reward attachment module (merge signal injection)
- T225 ✅: Reward shaping module (blend merge ±1 with eval metric)
- T226: Deployed CWSO + Polar infrastructure (rollout enabled, Parquet store)

## Expected outputs
- Test scenario: dispatch one SIA generation via harness to emage.code agent task
- End-to-end trace: dispatch → execution → evaluation → merge reward → shaped reward → Parquet write
- Validation report: trajectory record verified with all expected fields (workspace_uuid, rollout_session_id, evaluation_reward, shaped_reward, timestamps)
- Query results from Parquet store demonstrating trajectory is readable and queryable

## Acceptance criteria
- At least one complete SIA generation cycle executes start-to-finish without errors
- Parquet store contains a trajectory record with:
  - Valid workspace_uuid and rollout_session_id (links dispatch to result)
  - evaluation_reward field (from T224 attach_reward_via_merge)
  - shaped_reward field (from T225 shape_reward_for_session)
  - Completion timestamps (ISO8601)
  - Evaluation metadata (score, passed flag, diagnostics)
- Live integration test report documented with execution trace and query results
- Zero regressions in the full test suite (186+ tests)

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
