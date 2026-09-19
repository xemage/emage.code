# Knowledge vault — directory convention (T452)

**Structure only — no content populated here.** Populating a real production
knowledge corpus is explicitly out of scope for T452 (see
`docs/tasks/task-T452.md`, "Vault content — explicitly out of scope"); this
document exists so `implementation/runtime/memory/build.py` has a real
directory tree to point at, and so future content-authoring work has an
established convention to follow.

Per `docs/artifacts/memory-scope-model-v1.md` §2/§3, and consumed structurally
by `implementation/runtime/memory/scanner.py` per §4.1:

```
implementation/knowledge/memory/
├── general/   # harness-level knowledge, curated, broadcast to every project
├── project/   # scoped to this repo only — never crosses a repo boundary
└── shared/    # explicit opt-in per entry, named consumers only
```

Each entry is a Markdown file with YAML frontmatter. Required fields depend
on scope — see `memory-scope-model-v1.md` §3 for the full schema and §5 for
write-time validation (a malformed/missing `scope`, `project_id`, or
`shared_consumers` is rejected at index-build time, never defaulted).

Minimal example (`project/` scope):

```markdown
---
scope: project
project_id: em-age/emage.code
title: "Short, specific title"
tags: [relevant, tags]
---

Body content. May include prose sections (chunked section-aware, by Markdown
heading) and fenced code blocks (chunked via tree-sitter when the fence's
language tag has an installed grammar — see
`implementation/runtime/memory/chunk_code.py`).
```

Worked, minimal examples proving the pipeline's own contract (one valid
entry per scope, each §5 rejection case, and the cross-project
unreachability/shared-scope reachability fixture pair) live under
`tests/fixtures/memory/` — synthetic test fixtures, not real knowledge-base
content, mirroring this repo's `tests/golden/_example-scaffold/` precedent.
