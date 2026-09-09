# Knowledge-vault indexing pipeline (T452) + hybrid retrieval (T453)

Turns the knowledge vault (`implementation/knowledge/memory/{general,project,shared}/`,
git-versioned Markdown + YAML frontmatter, per ADR-005 Decision 1) into a
derived, rebuildable, scope-enforced vector index (T452), then queries that
index with a fused semantic+lexical+structural ranking, behind a mandatory
query-time scope filter (T453).

**Full design docs:** `docs/artifacts/indexing-pipeline-v1.md` (T452 — on-disk
index format, chunk metadata schema, chunking approach, embedding model/
runtime, rebuild-determinism property); `docs/artifacts/hybrid-retrieval-v1.md`
(T453 — fusion strategy, query-time scope filter, latency benchmark).

**Contracts implemented:** `docs/artifacts/memory-scope-model-v1.md` §10
("Handoff to T452") and §4.2 ("mandatory query-time filter", implemented by
T453's `scope_filter.py`).

## Modules

| Module | Stage | Optional deps |
|--------|-------|----------------|
| `schema.py` | shared data types (T452) | none (stdlib) |
| `validate.py` | §5 write-time scope validation (T452) | PyYAML |
| `scanner.py` | §4.1 structural repo-boundary scanning (T452) | none (stdlib + `git`) |
| `chunk_code.py` | tree-sitter code-block chunking (T452) | `tree-sitter`, grammar packages |
| `chunker.py` | body dispatcher, code fences vs. section-aware prose (T452) | (delegates to `chunk_code.py`) |
| `enrich.py` | attach plan-035 + §4.2 metadata to chunks (T452) | none |
| `embed.py` | local embedding, ADR-005 Decision 2 (T452 build; reused by T453 at query time) | `fastembed` |
| `index_writer.py` | deterministic on-disk writer + rebuild diff (T452) | none |
| `build.py` | CLI orchestrator, wires T452's stages together | (all of the above) |
| `scope_filter.py` | §4.2 mandatory query-time scope pre-filter (T453) | none (stdlib) |
| `lexical.py` | BM25 lexical signal over text/symbol/tags (T453) | none (stdlib) |
| `structural.py` | enrichment-metadata boost signal (T453) | none (stdlib) |
| `rank.py` | weighted fusion of the three signals (T453) | none (stdlib) |
| `retrieve.py` | `MemoryIndex`/`Retriever` — T453's query API, integration surface for T454 | `fastembed` (via `embed.py`) |

Only `embed.py`, `chunk_code.py`, `build.py`, and `retrieve.py`
(transitively, via `embed.py`) need the optional deps in `requirements.txt`.
Everything else is stdlib + PyYAML, consistent with this repo's existing
dependency-light convention — `scope_filter.py`, `lexical.py`, `structural.py`,
and `rank.py` are all fully unit-testable with no optional dependency
installed.

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

## Query API (T453)

```python
from implementation.runtime.memory.retrieve import MemoryIndex, Retriever
from implementation.runtime.memory.scope_filter import RequestingContext

index = MemoryIndex.load(Path("implementation/runtime/memory/_index/em-age-emage.code"))
retriever = Retriever(index)  # loads the LocalEmbedder once (embed.py)

context = RequestingContext(project_id="em-age/emage.code", platform="claude-code")
results = retriever.search("load_config helper", context, top_k=10)
for r in results:
    print(r.score, r.chunk["path"], r.chunk["symbol"])
```

`RequestingContext` is a required, non-defaultable argument to every
`Retriever.search` call — see `scope_filter.py` and
`docs/artifacts/hybrid-retrieval-v1.md` for the mandatory query-time scope
filter this enforces before any ranking runs.

## Vault content

Populating a real production knowledge corpus is explicitly out of scope for
T452 — see the task brief. `implementation/knowledge/memory/{general,project,shared}/`
currently contain only a `README.md` documenting the convention (no real
entries). Test fixtures proving the pipeline's own contract live under
`tests/fixtures/memory/`.
