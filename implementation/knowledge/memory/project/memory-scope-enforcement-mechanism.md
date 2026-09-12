---
scope: project
project_id: em-age/emage.code
title: "One predicate, not two: how this repo's memory index makes project-scope content provably unreachable across projects"
tags: [memory-layer, scope-model, architecture]
---

## The same function produces both outcomes

This repo's knowledge-vault indexing pipeline enforces scope with a single inclusion predicate,
evaluated identically regardless of an entry's declared scope: `general`-scope entries are always
included; `project`-scope entries are included only if they were found while scanning the target
project's own repository tree; `shared`-scope entries are included only if the target project is
named in that entry's own explicit consumer allowlist. There is no separate "exclusion mechanism"
for project scope and a separate "inclusion mechanism" for shared scope — one function, branching on
frontmatter data written once at commit time.

## Why project-scope unreachability is structural, not filtered

Building one project's index never even opens a directory outside an explicit, named set of
repository roots. A project-scoped entry that lives in a different repository is not read and then
discarded by a filter — the filesystem call that would have read its directory never happens at
all. This is what makes cross-project unreachability provable rather than merely "currently
observed to work."

## Reject, never default

A missing or malformed scope value is rejected and logged at index-build time; it is never defaulted
to the least-restrictive scope (`general`) or the most-restrictive (`project`). The same rule
applies to a `shared`-scope entry with an incomplete consumer allowlist — an incomplete allowlist is
treated as malformed input, not as "share with everyone" or "share with no one."
