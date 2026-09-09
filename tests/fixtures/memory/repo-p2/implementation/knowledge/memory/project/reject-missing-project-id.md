---
scope: project
title: "Fixture: rejection case — scope: project with no project_id"
tags: [fixture, t452, rejection-case]
---

`scope: project` requires a non-empty `project_id`. This entry omits it and
must be rejected per §5, not silently attributed to whichever repo it was
found in.
