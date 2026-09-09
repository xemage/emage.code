---
scope: shared
origin_project_id: fixture-org/repo-p1
shared_consumers:
  projects: ["fixture-org/repo-p2"]
  platforms: ["claude-code"]
title: "Fixture: shared-scope entry opted into P2's index"
tags: [fixture, t452, reachability-probe]
---

## FIXTURE-CANARY-SHARED-P1-TO-P2-8891

This entry's author (in `repo-p1`) explicitly opted `fixture-org/repo-p2`
into reading it. It must appear in `fixture-org/repo-p2`'s index when P2's
build is configured to also scan `repo-p1` for shared candidates — proving
the reachability half of the same `include(entry, P)` mechanism that keeps
`p1-only-secret.md` (this repo's `project`-scope entry) unreachable.
