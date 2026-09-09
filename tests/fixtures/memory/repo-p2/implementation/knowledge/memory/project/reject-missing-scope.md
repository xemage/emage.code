---
title: "Fixture: rejection case — missing scope field entirely"
tags: [fixture, t452, rejection-case]
---

This entry has no `scope:` field at all. Per §5 it must be rejected — absent
from every derived index, present in the rejection log, and must NOT be
defaulted to `general` or `project`.
