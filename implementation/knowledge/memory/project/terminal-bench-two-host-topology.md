---
scope: project
project_id: em-age/emage.code
title: "Terminal-Bench trial data lives on two hosts; the remote host's data is read, never copied into the repo"
tags: [terminal-bench, infrastructure, evaluation]
---

## Two independent trajectory sources

This project's Terminal-Bench measurement work combines trial data from two separate hosts: a
local run, and a separate remote host reached over read-only SSH. Both sources' raw result/verifier
output are treated as authoritative and are independently re-derived directly from the raw files
(not trusted from any prior self-report) when closing out a measurement task.

## Deliberate non-duplication

The remote host's own trial data is read directly for analysis but is explicitly not copied into
this repository — an artifact-reconciliation decision made when the two sources were first
combined. Verification steps that need to confirm "no new trial activity happened" check the remote
host's own state directly (e.g. its container/image list) rather than relying on a summary produced
by whichever pass generated the report being verified.
