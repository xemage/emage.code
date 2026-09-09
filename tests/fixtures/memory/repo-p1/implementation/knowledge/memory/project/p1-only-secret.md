---
scope: project
project_id: fixture-org/repo-p1
title: "Fixture: P1's own project-scope entry (must never reach P2's index)"
tags: [fixture, t452, unreachability-probe]
---

## FIXTURE-CANARY-P1-ONLY-CONTENT-4172

This entry exists purely to prove `memory-scope-model-v1.md` §4.1's
structural unreachability guarantee. If the literal token
`FIXTURE-CANARY-P1-ONLY-CONTENT-4172` ever appears in any index built for a
project other than `fixture-org/repo-p1`, that is an acceptance-criterion-3
failure.
