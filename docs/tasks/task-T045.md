**Status:** done
**Completed:** 2026-06-06
# Task T045 - Prepare v3 release candidate merge

## Objective
Finalize the v3 release-ready branch with green pipelines and merge readiness.

## Inputs
- outputs from T044
- active branch and GitLab MR/pipeline status

## Expected outputs
- merge request with green CI
- release candidate checklist completed

## Acceptance criteria
- MR is mergeable with required checks green.
- develop pipeline is green post-merge.
- release candidate state is recorded in task/checkpoint artifacts.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
