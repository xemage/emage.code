# Task <ID> — <Title>

**ID:** T<NNN>
**Owner:** <agent-slug>
**Status:** pending
**Priority:** P0 | P1 | P2
**Tier:** mechanical | standard | judgment | — (optional)
**Depends on:** <IDs or —>
**Created:** YYYY-MM-DD
**Completed:** —
**Based on:** docs/plans/plan-<NNN>-<slug>.md

> **Tier field (optional, additive):** one of `mechanical`, `standard`, or `judgment`, defined in
> `docs/artifacts/task-tier-schema-v1.md`. Leave as `—` for any brief not yet classified — existing
> briefs authored before this field existed remain valid without it; adding this field is not a
> breaking change to the brief schema. Assigning a tier to any specific existing task is out of
> scope for the task that introduced this field (T440); see that artifact's "Not decided here"
> section.

## Objective
<one paragraph>

## Inputs
- <artifact-vN.md paths>

## Expected outputs
- <artifact paths this task must produce>

## Acceptance criteria
1. <specific, testable>

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
