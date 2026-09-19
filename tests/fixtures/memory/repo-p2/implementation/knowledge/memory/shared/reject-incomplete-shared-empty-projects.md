---
scope: shared
shared_consumers:
  projects: []
  platforms: ["claude-code"]
title: "Fixture: rejection case — shared_consumers.projects is an empty list"
tags: [fixture, t452, rejection-case]
---

`shared_consumers.projects` is present but an empty list. Per §5 this is
malformed input, not "no consumers" — it must be rejected on the same terms
as a missing field.
