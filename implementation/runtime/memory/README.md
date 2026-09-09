# Knowledge-vault indexing pipeline (T452)

Turns the knowledge vault (`implementation/knowledge/memory/{general,project,shared}/`,
git-versioned Markdown + YAML frontmatter, per ADR-005 Decision 1) into a
derived, rebuildable, scope-enforced vector index.

**Full design doc:** `docs/artifacts/indexing-pipeline-v1.md` — on-disk index
format, chunk metadata schema, chunking approach, embedding model/runtime,
rebuild-determinism property.

**Contract this implements:** `docs/artifacts/memory-scope-model-v1.md` §10
("Handoff to T452").

## Modules

| Module | Stage | Optional deps |
|--------|-------|----------------|
| `schema.py` | shared data types | none (stdlib) |
| `validate.py` | §5 write-time scope validation | PyYAML |
| `scanner.py` | §4.1 structural repo-boundary scanning | none (stdlib + `git`) |
| `chunk_code.py` | tree-sitter code-block chunking | `tree-sitter`, grammar packages |
| `chunker.py` | body dispatcher (code fences vs. section-aware prose) | (delegates to `chunk_code.py`) |
| `enrich.py` | attach plan-035 + §4.2 metadata to chunks | none |
| `embed.py` | local embedding (ADR-005 Decision 2) | `fastembed` |
| `index_writer.py` | deterministic on-disk writer + rebuild diff | none |
| `build.py` | CLI orchestrator, wires all stages together | (all of the above) |

Only `embed.py`, `chunk_code.py`, and `build.py` (transitively) need the
optional deps in `requirements.txt`. Everything else is stdlib + PyYAML,
consistent with this repo's existing dependency-light convention.

## CLI usage

```bash
python3 -m implementation.runtime.memory.build \
    --project-id em-age/emage.code \
    --own-repo-root . \
    --general-repo-root . \
    --shared-source-root ../sia \
    --output-dir implementation/runtime/memory/_index/em-age-emage.code
```

`--project-id` is always explicit — never inferred from vault content
(memory-scope-model-v1.md §4.1). `--shared-source-root` may be repeated zero
or more times, once per foreign repo this build should also scan for
`shared`-scope candidates (only that repo's `shared/` subtree is ever read —
see `scanner.py`'s module docstring for the structural guarantee this gives).

## Vault content

Populating a real production knowledge corpus is explicitly out of scope for
T452 — see the task brief. `implementation/knowledge/memory/{general,project,shared}/`
currently contain only a `README.md` documenting the convention (no real
entries). Test fixtures proving the pipeline's own contract live under
`tests/fixtures/memory/`.
