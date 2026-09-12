---
scope: project
project_id: em-age/emage.code
title: "ADR-005: this repo's memory layer keeps a git-versioned canonical store and a separate, non-canonical derived index"
tags: [adr, memory-layer, architecture]
---

## Storage: canonical store vs. derived index are two different things

This repo's accepted memory-layer decision record establishes that knowledge entries live as
Markdown files with YAML frontmatter, committed and reviewed through the normal git workflow, as
the canonical source of truth. A separate, rebuildable vector index is derived from that store at
build time; the index is read-only, is not itself git-versioned, and rebuilding it from a clean
checkout must always reproduce it. Querying code talks to the derived index, never to the canonical
store directly.

## Embeddings: local model, zero recurring cost, chosen precisely to avoid a spend-authorization gate

The same decision record chooses a local, open-source embedding model over any paid embeddings API,
specifically because a paid API would be invoked at every index build and at every retrieval query
thereafter — a recurring, unbounded operational cost, unlike a one-off bounded expense. Because the
chosen model has no per-token or subscription cost, building the indexing pipeline did not require
prior user cost-authorization the way a paid alternative would have.

## Read-only-by-default, asserted in three independent places

No agent may write to the canonical store or the derived index outside the sanctioned rebuild step.
The read-only guarantee is asserted in three independent places (agent definition, server config,
deployment manifest) rather than one — the same "more than one independent control" pattern this
repo already uses for its protected golden-suite paths, so a single missed update cannot silently
reopen the write path.
