---
scope: shared
shared_consumers:
  projects: ["fixture-org/repo-p2"]
title: "Fixture: rejection case — shared_consumers missing platforms"
tags: [fixture, t452, rejection-case]
---

`shared_consumers.platforms` is missing entirely. Per §5 an incomplete
`shared_consumers` block is malformed — rejected, not treated as "share with
no platforms" or "share with all platforms."
