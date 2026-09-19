---
scope: project
project_id: em-age/emage.code
title: "Protected paths: tests/golden/** and scripts/scorecard.py are frozen against normal improvement-task edits"
tags: [golden-suite, protected-paths, branch-protection]
---

## Why these two paths are protected

Two paths in this repository, `tests/golden/**` and `scripts/scorecard.py`, are protected: no agent
definition may edit them as part of normal improvement-task work. They are the golden-suite
evaluator's own interface and held-out data — the thing improvement work is graded against, not a
thing improvement work may itself change to make its own results look better. Source:
`docs/artifacts/protected-paths-v1.md`.

## Three independent controls, not one

Because "held-out set leaks into improvement work" is rated Medium likelihood / Critical impact in
this project's own roadmap risk table, three independent controls apply at once: a repo-wide static
path guard that catches functional access to the held-out set and bare mentions of specific
held-out case IDs anywhere outside `tests/golden/`; an evaluator-hash tamper-evidence check; and
this document's own per-agent write-scope exclusion plus a static guard proving every agent
definition declares the exclusion. Each control catches a different failure mode; none alone is
treated as sufficient on its own.

## What is not frozen

Freezing write scope does not freeze read scope: the orchestrator retains standing read/audit
access to both paths for verification and evaluation. Genuine future maintenance to a protected
path requires an explicit, named task brief that cites the protection document and states the
exception outright — never a silent incidental edit inside unrelated work.
