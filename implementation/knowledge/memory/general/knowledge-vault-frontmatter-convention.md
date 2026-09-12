---
scope: general
title: "How to author a knowledge-vault entry this harness's indexing pipeline will actually pick up"
tags: [memory-layer, vault-convention, authoring]
---

## Required shape

A vault entry is a Markdown file with a YAML frontmatter block at the very top. Every entry
requires a `scope` field set to exactly one of `general`, `project`, or `shared` — a `project`-
scope entry additionally requires `project_id`; a `shared`-scope entry additionally requires a
`shared_consumers` block naming both an explicit project allowlist and an explicit platform
allowlist. A missing or malformed value in any of these is rejected at index-build time, never
defaulted.

## Where the file has to live, and why headings matter

The indexing pipeline only ever looks for `.md` files inside three exactly-named subdirectories —
`general/`, `project/`, and `shared/` — under each repository's own knowledge-vault root; a file
placed anywhere else, or a scope value that does not match the subdirectory it was found in, is
never indexed. The body below the frontmatter is chunked section-aware: each Markdown heading
starts a new retrievable chunk, so an entry covering more than one distinct fact reads and retrieves
better as multiple headed sections than as one long undifferentiated block.
