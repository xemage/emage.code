# Task T305 — Follow `local-docker-desktop-guide.md` literally, end to end

**ID:** T305
**Owner:** qa-engineer
**Status:** pending
**Priority:** P1
**Depends on:** T304
**Created:** 2026-07-31
**Completed:** —
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Independently verify that `docs/deployment/local-docker-desktop-guide.md` (plan-013's deliverable)
actually works for a reader who did not write it — the guide has existed since 2026-06/07 but has
never been independently validated end-to-end.

## Inputs
- `docs/deployment/local-docker-desktop-guide.md`
- The live CWSO stack from T304 (for comparison — the guide should be followed on its own terms,
  not assumed identical to T304's exact steps)

## Expected outputs
- `docs/artifacts/t305-deployment-guide-validation-report-v1.md` (new file)

## Acceptance criteria
1. Every command in the guide is run exactly as written; the actual output is recorded — not
   assumed from the guide's prose.
2. Every claim in the guide ("you should now see X", "curl should return Y") is checked against the
   actual output obtained, not against what the guide asserts.
3. Any failing step, missing prerequisite, or output inconsistent with the guide's description is
   filed as a new bug task (next available T-ID) referencing the exact guide section/line and the
   literal failing output. Do not silently fix the guide's prose in this task.
4. If a failure's root cause traces to a CWSO-core defect (not just guide wording), it is also
   routed through T310's convention (issue-summary + fix-plan + task briefs in `../CWSO`).
5. `docs/artifacts/t305-deployment-guide-validation-report-v1.md` lists, per guide section: command
   run, actual output, PASS/FAIL against the guide's claim.
6. Per R8, the report itself IS the evidence — no summary claim without the actual output quoted
   beneath it.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
