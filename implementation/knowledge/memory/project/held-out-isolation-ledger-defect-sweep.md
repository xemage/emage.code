---
scope: project
project_id: em-age/emage.code
title: "Two independent leak guards this repo runs before any push: held-out case-ID isolation and the maturity registry's self-referential ledger-defect check"
tags: [golden-suite, protected-paths, maturity-registry]
---

## Held-out case-ID isolation

A repo-wide static guard fails if any file outside `tests/golden/` (as a whole) mentions one of the
golden suite's real held-out case IDs as a whole token, or if any Python source file outside the
held-out directory contains the literal held-out path string. This catches doc or report content
that would otherwise reveal what a held-out case actually tests. New documentation, task briefs,
and reports authored in this repo must never quote a real held-out case ID by name — describe
held-out findings by aggregate or category instead.

## The maturity registry's own self-referential trap

Separately, this repo's component-maturity checker treats any currently-open (non-`done`,
non-`cancelled`), `P0`- or `P1`-priority task row whose title or brief text names an already-top-
tier component's real registry id as a whole word as an open defect against that component — even
if the task has nothing to do with that component. This exact class of mistake has recurred
repeatedly in this project's own task history. The safe pattern established in response: never
trust a previously-quoted id list or count; re-derive the live, current set of top-tier component
ids directly before writing new task content; sweep new task titles/briefs against that live list;
and prefer closing a task within the same commit sequence that created it, so its brief is never
left attached to an open ledger row at all.
